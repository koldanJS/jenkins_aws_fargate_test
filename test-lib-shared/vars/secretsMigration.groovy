def call(Map config = [:]) {
  container('python') {
        withAWS(region: "${AWS_REGION}", credentials: "${AWS_CREDENTIALS_ID}") {
      script {
        try {
          migration = readJSON(text: sh(
                                returnStdout: true,
                                script: "python secrets-migrator/cli.py generate \
                                --secret_name=${SECRET_NAME_OR_ARN} \
                                --secrets_migrations_path=${SECRETS_MIGRATIONS_PATH} \
                                --region=${AWS_REGION}"
                            ).trim())

          parameters = []
          if (migration.size() != 0) {
            migration.each { k, v ->
              if (k != '_migration') {
                defaultValue = ''
                if (v.containsKey('default')) {
                  defaultValue = v['default']
                }
                if (v['action'] != 'delete') {
                  parameters.add(
                                    [
                                        $class: 'StringParameterDefinition',
                                        defaultValue: defaultValue,
                                        description:"${v['action']} variable ${k}",
                                        name: k
                                    ])
                }
              }
            }

            inputs = input(
                            message: 'Provide Values for following secrets',
                            parameters: parameters
                        )
            if (inputs instanceof String || inputs instanceof GString) {
              migration.each { k, v ->
                if (k != '_migration') {
                  migration[k]['value'] = inputs
                }
              }
                        } else if (inputs instanceof HashMap) {
              inputs.each { k, v ->
                migration[k]['value'] = v
              }
            }

            writeJSON file: 'data.json', json: migration

            sh(
                            returnStdout: true,
                            script: "python secrets-migrator/cli.py apply data.json \
                            --secret_name=${SECRET_NAME_OR_ARN} \
                            --secrets_migrations_path=${SECRETS_MIGRATIONS_PATH} \
                            --region=${AWS_REGION}"
                        )
          }
                } catch (Exception ex) {
          println("Failed to apply secrets migration. Exception=[${ex}]")
          throw ex
        }
      }
        }
  }
}
