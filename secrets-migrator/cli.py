#/usr/bin/env python3

import boto3
import click
from botocore.exceptions import ClientError
import os
import sys
import json
import logging


logger = logging.getLogger(__name__)


class InvalidAction(Exception):
    pass


class SecretsManager:
    """Encapsulates Secrets Manager functions."""
    def __init__(self, aws_region='us-east-1') -> None:
        """
        :param aws_region: AWS region name, default 'us-east-1'
        """
        # Create a Secrets Manager client
        self.aws_region = aws_region
        session = boto3.session.Session()
        self.secretsmanager = session.client(
            service_name='secretsmanager',
            region_name=self.aws_region
        )
        

    def create(self, name, secret_value):
        """
        Creates a new secret. The secret value can be a string or bytes.
        :param name: The name of the secret to create.
        :param secret_value: The value of the secret.
        :return: Metadata about the newly created secret.
        """
        try:
            kwargs = {'Name': name}
            if isinstance(secret_value, str):
                kwargs['SecretString'] = secret_value
            elif isinstance(secret_value, bytes):
                kwargs['SecretBinary'] = secret_value
            response = self.secretsmanager.create_secret(**kwargs)
            self.name = name
            logger.info("Created secret %s.", name)
        except ClientError:
            logger.exception("Couldn't get secret %s.", name)
            raise
        else:
            return response

    def get_value(self, name, stage=None):
        """
        Gets the value of a secret.
        :param stage: The stage of the secret to retrieve. If this is None, the
                      current stage is retrieved.
        :return: The value of the secret. When the secret is a string, the value is
                 contained in the `SecretString` field. When the secret is bytes,
                 it is contained in the `SecretBinary` field.
        """

        try:
            kwargs = {'SecretId': name}
            if stage is not None:
                kwargs['VersionStage'] = stage
            response = self.secretsmanager.get_secret_value(**kwargs)
            logger.info("Got value for secret %s.", name)
        except ClientError:
            logger.exception("Couldn't get value for secret %s.", name)
            raise
        else:
            return response

    def put_value(self, name, secret_value, stages=None):
        """
        Puts a value into an existing secret. When no stages are specified, the
        value is set as the current ('AWSCURRENT') stage and the previous value is
        moved to the 'AWSPREVIOUS' stage. When a stage is specified that already
        exists, the stage is associated with the new value and removed from the old
        value.
        :param secret_value: The value to add to the secret.
        :param stages: The stages to associate with the secret.
        :return: Metadata about the secret.
        """
        try:
            kwargs = {'SecretId': name}
            if isinstance(secret_value, str):
                kwargs['SecretString'] = secret_value
            elif isinstance(secret_value, bytes):
                kwargs['SecretBinary'] = secret_value
            if stages is not None:
                kwargs['VersionStages'] = stages
            response = self.secretsmanager.put_secret_value(**kwargs)
            logger.info("Value put in secret %s.", name)
        except ClientError:
            logger.exception("Couldn't put value in secret %s.", name)
            raise
        else:
            return response

class Secret:
    def __init__(self, secrets_manager, name, stage=None) -> None:
        self.secret_manager = secrets_manager
        self.name = name
        self.stage = stage
       
        try:
          value = self.secret_manager.get_value(self.name, self.stage)
        except ClientError:
            logger.exception("Secret not exist %s", self.name)
            raise
        logger.debug(value)
        self.secret_string = value['SecretString']
        self._secret_dict = json.loads(self.secret_string) 
        self.version_stages = value.get('VersionStages')
        self._digifi_version = self.get_digifi_version(self.version_stages)

    @property
    def digifi_version(self):
        return self._digifi_version

    @property
    def secret_dict(self):
        return self._secret_dict

    def put_value(self, secret_value, stages=None):
        return self.secret_manager.put_value(self.name, secret_value, stages)


    def get_value(self, stage=None):
        return self.secret_manager.get_value(self.name, stage)

    def get_digifi_version(self, version_stages):
        logger.debug(version_stages)
        if version_stages:
            for label in version_stages:
                if label.startswith('DigifiVersion='):
                    digifi_secret_version = label.split('=')[1]
                    if digifi_secret_version.isdigit():
                        logger.debug(digifi_secret_version)
                        return int(digifi_secret_version)
        return 0


class Migrator:
    def __init__(self, secret, digifi_version, secrets_migrations_path) -> None:
        self.secret = secret
        if digifi_version:
            self.digifi_version = int(digifi_version)
        else:
            self.digifi_version = int(self.secret.digifi_version)
        logger.info( self.digifi_version )
        self.secrets_migrations_path = secrets_migrations_path


    def _get_secret_migration_file_names(self):
        result = []
        with os.scandir(self.secrets_migrations_path) as it:
            for entry in it:
                if entry.name.endswith(".json") and entry.is_file():
                    result.append(entry.name)            
        secret_migration_file_names = (sorted(list( filter(lambda x: int(os.path.splitext(x)[0]) > self.digifi_version, result))))
        return  secret_migration_file_names

    def _get_migration_version(self, secret_migration_file_names):
        if secret_migration_file_names:
          return int(secret_migration_file_names[-1].split('.json')[0])

    def check_migration(self):
        secret_migration_file_names = self._get_secret_migration_file_names()
        migration_version= self._get_migration_version(secret_migration_file_names)
        if migration_version:
          return migration_version > self.digifi_version
        else:
          return False


    def build_migration(self):
        merged_dict ={}
        secret_migration_file_names = self._get_secret_migration_file_names()
        migration_version= self._get_migration_version(secret_migration_file_names)
        
        for f in secret_migration_file_names:
            with open(os.path.join(self.secrets_migrations_path, f)) as json_file:
                data = json.load(json_file)
                merged_dict = {**merged_dict, **data}
        if migration_version:
            merged_dict = {**merged_dict, **{'_migration': {'version': migration_version}}}
        return merged_dict


    def apply(self, file_name):
        with open(file_name, 'r') as f:
            data = json.load(f)
        if  '_migration' in data:
            new_secret_string = json.dumps(self.apply_actions(data))
            self.secret.put_value(new_secret_string, [f"DigifiVersion={self.migration_version}", 'AWSCURRENT'])
        else:
            logger.error("Migration file should contain '_migration' key")
            exit(1)

    def rollback(self):
        pass

    def apply_actions(self,data):
        self.migration_version = None
        self.new_secret_dict = self.secret.secret_dict
        for secret_key, secret_value in data.items():
            if secret_key == '_migration':
                self.migration_version =  secret_value.get('version')
            action = secret_value.get('action')
            logger.info(action)
            if action:
                if action == 'create':
                    self.apply_create_action(secret_key, secret_value)
                elif action == 'update':
                    self.apply_update_action(secret_key, secret_value)
                elif  action == 'delete':
                    self.apply_delete_action(secret_key, secret_value)
                else:
                    raise InvalidAction
        return self.new_secret_dict

    def apply_create_action(self, key, value):
        if key in self.new_secret_dict:
            logger.error(f"Can't create key '{key}' because it already exist")
            sys.exit(1)
        else:
            if value.get('value'):
                self.new_secret_dict[key] = value['value']
            elif value.get('default'):
                self.new_secret_dict[key] = value['default']
            else:
                logger.error(f"Can't update key '{key}' because it not exist")
                sys.exit(1)
    
    def apply_update_action(self, key, value):
        if key in self.new_secret_dict:
            self.new_secret_dict.update({key: value['value']})
        else:
            logger.error(f"Can't update key '{key}' because it not exist")
            sys.exit(1)
   
    def apply_delete_action(self, key, value):
        if key in self.new_secret_dict:
            self.new_secret_dict.pop(key)
        else:
            logger.error(f"Can't delete key '{key}' because it not exist")
            sys.exit(1)
   
def check_aws_creds():
    sts = boto3.client('sts')
    try:
      sts.get_caller_identity()
    except ClientError:
        logger.error("Can't get ")  
        raise


secret_name = click.option('--secret_name', '--secret_arn', help='AWS secret_name or secret_arn',required=True)
secrets_migrations_path = click.option('--secrets_migrations_path',  type=click.Path(exists=True), default='secrets')
digifi_version = click.option('--digifi_version', help='DigiFi version')
log_level = click.option('--log_level', '-l', default='INFO',  help="Print more output.")
region = click.option('--region', '--aws_region', default='us-east-1', help='AWS region')
quite = click.option('--quite', '-q',  is_flag=True,  help="Print more output.")

@click.group
@log_level
@quite
def main(log_level, quite):
    if not quite:
      logging.basicConfig(level=log_level.upper()) 
    logger.info('Starting')  
    check_aws_creds()


@main.command()
@region
@secret_name
@secrets_migrations_path
@digifi_version
@click.pass_context
def check(ctx, region, secret_name, secrets_migrations_path, digifi_version):
    logger.info("Check migration")
    secret_manager =  SecretsManager(region)
    secret = Secret(secret_manager, secret_name)
    migrator = Migrator(secret, digifi_version, secrets_migrations_path)
    click.echo(migrator.check_migration())

@main.command()
@region
@secret_name
@secrets_migrations_path
@digifi_version
@click.pass_context
def generate(ctx, region, secret_name, secrets_migrations_path, digifi_version):
    logger.info("Generating migration")
    secret_manager =  SecretsManager(region)
    secret = Secret(secret_manager, secret_name)
    migrator = Migrator(secret, digifi_version, secrets_migrations_path)
    click.echo(migrator.build_migration())
  
@main.command()
@region
@secret_name
@secrets_migrations_path
@digifi_version
@click.argument('file_name', type=click.Path(exists=True))
@click.pass_context
def apply(ctx, region, secret_name, secrets_migrations_path, digifi_version, file_name):
    secret_manager =  SecretsManager(region)
    secret = Secret(secret_manager, secret_name)
    Migrator(secret, digifi_version, secrets_migrations_path).apply(file_name)
    click.echo("apply finished...")

@main.command()
@region
@secret_name
@secrets_migrations_path
@digifi_version
@click.pass_context
def rollback(ctx, region, secret_name, secrets_migrations_path, digifi_version):
    secret_manager =  SecretsManager(region)
    secret = Secret(secret_manager, secret_name)
    Migrator(secret, digifi_version, secrets_migrations_path).rollback()


@main.command()
@region
@secret_name
@click.pass_context
def rollback_to_previous(ctx, region, secret_name):
    secret_manager =  SecretsManager(region)
    previous = secret_manager.get_secret_value(SecretId=secret_name, VersionStage='AWSPREVIOUS').get('VersionId')
    current = secret_manager.get_secret_value(SecretId=secret_name, VersionStage='AWSCURRENT').get('VersionId')
    if previous and current:
      secret_manager.update_secret_version_stage(SecretId=secret_name, VersionStage='AWSCURRENT', RemoveFromVersionId=current, MoveToVersionId=previous)

if __name__ == '__main__':
    main()
