def call(Map config = [:]) {
  container('python') {
        withAWS(region: "${AWS_REGION}", credentials: "${AWS_CREDENTIALS_ID}") {
      script {
        try {
          migration_check =  sh(
                                returnStdout: true,
                                script: "python secrets-migrator/cli.py check \
                                --secret_name=${SECRET_NAME_OR_ARN} \
                                --secrets_migrations_path=${SECRETS_MIGRATIONS_PATH} \
                                --region=${AWS_REGION}"
                            ).trim()
          return migration_check
                } catch (Exception ex) {
          println("Failed to check if secrets migration applied. Exception=[${ex}]")
          throw ex
        }
      }
        }
  }
}
