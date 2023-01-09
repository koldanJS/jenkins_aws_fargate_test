@Library('test-lib-shared') _

def CLOUD = 'test-staging'
def GITHUB_CREDENTIAL_ID = 'github-test-creds'
def NAMESPACE = 'apps'
def MIGRATION_CHECK = false

properties([
    parameters([
        param.getGithubRepoReleases(
            github_repo:'https://api.github.com/repos/koldanJS/jenkins_aws_fargate_test/releases',
            github_credentials_id: "${GITHUB_CREDENTIAL_ID}")
    ])
])

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
      AWS_REGION = 'eu-central-1'
      AWS_CREDENTIALS_ID = 'test-staging-deployment-user'
      AWS_SECRETS_MANAGER_ID = 'arn:aws:secretsmanager:eu-central-1:266311286062:secret:test/staging/application-dVcQU09D-TmX6IX'
      DEFAULT_INGRESS_HOST = 'staging.digifi.cc'
      ECR_REGISTRY = '439232230176.dkr.ecr.eu-central.amazonaws.com'
      ENVIRONMENT_NAME = 'staging'
      GIT_REPO_TOKEN = credentials("${GITHUB_CREDENTIAL_ID}")
      GITHUB_CREDENTIAL_ID = "${GITHUB_CREDENTIAL_ID}"
      NAMESPACE = "${NAMESPACE}"
      HELM_EXPERIMENTAL_OCI = 1
      HELM_VALUES_S3_BUCKET = 'test-helm-values-eyjhbgcioijiuzi1niisinr5cci6ikpxvcj9' 
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