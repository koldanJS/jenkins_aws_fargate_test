@Library('test-lib-shared') _

def CLOUD = 'test-staging'
def GITHUB_CREDENTIAL_ID = 'github_test_token'
def GITHUB_TOKEN_ID = 'github_test_token'
def GITHUB_REPO_URL = 'https://github.com/koldanJS/jenkins_aws_fargate_test.git'
def GITHUB_API_REPO_URL = 'https://api.github.com/repos/koldanJS/jenkins_aws_fargate_test/releases'
def NAMESPACE = 'apps'
def MIGRATION_CHECK = false

properties([
    parameters([
        param.getGithubRepoReleases(
            github_repo: "${GITHUB_API_REPO_URL}",
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
          artifactNumToKeepStr: '3',
          daysToKeepStr: '3',
          numToKeepStr: '3')
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
  // triggers {

  // }
  stages {
    stage('Slack Notification') {
      steps {
        slackSend color: 'good',
                  message: "Job <${env.BUILD_URL}|${env.JOB_NAME}/${env.BUILD_NUMBER}> has started at ${(new Date()).format("yyyy-MM-dd HH:mm 'UTC'")} by ${env.BUILD_USER} from Jenkins Pipeline",
                  channel: '#jenkins-test'
      }
    }
    // stage('Checkout secrets-migrator script') {
    //   steps {
    //     container('python') {
    //       checkout(
    //         [
    //           $class: 'GitSCM',
    //           branches: [[name: '*/master']],
    //           doGenerateSubmoduleConfigurations: false,
    //           extensions: [],
    //           submoduleCfg: [],
    //           userRemoteConfigs: [
    //             [
    //               credentialsId: "${GITHUB_CREDENTIAL_ID}",
    //               url: "${GITHUB_REPO_URL}"
    //             ]
    //           ]
    //         ]
    //       )
    //       sh(
    //         returnStdout: true,
    //         label: 'Install secrets-migrator script requirements',
    //         script: 'pip install -r secrets-migrator/requirements.txt'
    //       )
    //     }
    //   }
    // }
    // stage('Check secrets migration') {
    //   steps {
    //     script {
    //       MIGRATION_CHECK = checkSecretsMigration()
    //       echo "${MIGRATION_CHECK}"
    //     }
    //   }
    // }
    // stage('Run secrets migration') {
    //   steps {
    //     secretsMigration()
    //   }
    //   post {
    //     success {
    //       script {
    //         MIGRATION_APPLIED = true
    //       }
    //     }
    //     failure {
    //       script {
    //         MIGRATION_APPLIED = false
    //       }
    //     }
    //   }
    // }
    stage('Login into ECR') {
      steps {
        container('helm') {
          withAWS(region: "${AWS_REGION}", credentials: "${AWS_CREDENTIALS_ID}") {
            sh(
              returnStdout: true,
              label: 'Login into ECR',
              script: "aws ecr get-login-password --region ${AWS_REGION} | \
                      helm registry login --username AWS --password-stdin ${ECR_REGISTRY}"
            )
          }
        }
      }
    }
    stage('Running helm deploy') {
      steps {
        echo "Step"
        // script {
        //   parallel([
        //     'digifi-auth': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-auth-helm-chart',
        //         release_name:  'digifi-auth',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}"),
        //     'digifi-core': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-core-helm-chart',
        //         release_name:  'digifi-core',
        //         default_ingress_host: 'adfaf.blal.afa',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}"),
        //     'digifi-de': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-decision-engine-helm-chart',
        //         release_name:  'digifi-de',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}"),
        //     'digifi-dlp': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-dlp-helm-chart',
        //         release_name:  'digifi-dlp',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}"),
        //     'digifi-dp': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-decision-processing-helm-chart',
        //         release_name:  'digifi-dp',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}"),
        //     'digifi-legacy': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-legacy-backend-helm-chart',
        //         release_name:  'digifi-legacy',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}"),
        //     'digifi-los': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-loan-origination-system-helm-chart',
        //         release_name:  'digifi-los',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}"),
        //     'digifi-webhooks': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-webhooks-helm-chart',
        //         release_name:  'digifi-webhooks',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}"),
        //     'digifi-process-automation': helmDeployClosure(
        //         helm_ecr_repository:  'digifi-process-automation-helm-chart',
        //         release_name:  'digifi-process-automation',
        //         helm_chart_version:  "2.0.0-${RELEASE_VERSION}")
        //   ])
        // }
      }
    }
    stage('Running digifi-migration-job') {
      steps {
        echo "Step"
        // script {
        //   helmDeployClosure(
        //     helm_ecr_repository:  'digifi-migrations-helm-chart',
        //     release_name:  'digifi-migration-job',
        //     helm_chart_version:  "2.0.0-${RELEASE_VERSION}").call()
        // }
      }
      // post {
      //   success {
      //     script {
      //       getK8sLogs(label: 'app=digifi-migration-job')
      //     }
      //   }
      // }
    }
  }
  // post {
  //   failure {
  //     script {
  //       if ("${MIGRATION_CHECK}" == 'True' && "${MIGRATION_APPLIED}" == true) {
  //         rollbackSecretMigrationToPrevious()
  //       }
  //     }
  //   }
  // }
}