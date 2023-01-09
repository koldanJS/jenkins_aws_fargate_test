def CLOUD = 'digifi-staging'
def GITHUB_CREDENTIAL_ID = 'github-digifi'
def NAMESPACE = 'apps'
def MIGRATION_CHECK = false

pipeline {
    agent any
    options {
        ansiColor('xterm')
        timestamps()
        buildDiscarder(
        logRotator(artifactDaysToKeepStr: '0',
            artifactNumToKeepStr: '5',
            daysToKeepStr: '5',
            numToKeepStr: '5')
        )
        disableConcurrentBuilds()
    }
    environment {
      AWS_REGION = 'us-east-1'
      AWS_CREDENTIALS_ID = 'digifi-staging-deployment-user'
      AWS_SECRETS_MANAGER_ID = 'arn:aws:secretsmanager:us-east-1:266311286062:secret:digifi/staging/application-dVcQU09D-TmX6IX'
      DEFAULT_INGRESS_HOST = 'staging.digifi.cc'
      ECR_REGISTRY = '439232230176.dkr.ecr.us-east-1.amazonaws.com'
      ENVIRONMENT_NAME = 'staging'
      GIT_REPO_TOKEN = credentials("${GITHUB_CREDENTIAL_ID}")
      GITHUB_CREDENTIAL_ID = "${GITHUB_CREDENTIAL_ID}"
      NAMESPACE = "${NAMESPACE}"
      HELM_EXPERIMENTAL_OCI = 1
      HELM_VALUES_S3_BUCKET = 'digifi-helm-values-eyjhbgcioijiuzi1niisinr5cci6ikpxvcj9' 
      SECRET_NAME_OR_ARN = 'secrets/migrations/test2'
      SECRETS_MIGRATIONS_PATH = 'secrets-migrator/secrets'
    }
//     triggers {
// }
    stages {
        stage('Slack Notification') {
          steps {
            slackSend color: 'good',
                      message: "Job <${env.BUILD_URL}|${env.JOB_NAME}/${env.BUILD_NUMBER}> has started at ${(new Date()).format("yyyy-MM-dd HH:mm 'UTC'")} by ${env.BUILD_USER} from Jenkins Pipeline",
                      channel: '#jenkins-test'
          }
        }
    }
}
