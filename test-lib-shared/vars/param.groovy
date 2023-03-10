def getGithubRepoReleases(Map config = [:]) {
  if ( config['github_repo'] == null ) {
    error(['"github_repo" argument is mandatory'])
  }
  if ( config['github_credentials_id'] == null ) {
    error(['"github_credentials_id" argument is mandatory'])
  }

  github_repo = config['github_repo']
  github_credentials_id =  config['github_credentials_id']

  return [$class: 'CascadeChoiceParameter',
          choiceType: 'PT_SINGLE_SELECT',
          description: 'Releases',
          filterLength: 1,
          filterable: false,
          name: 'RELEASE_VERSION',
          randomName: 'choice-parameter-5631314439613978',
          script: [
              $class: 'GroovyScript',
              fallbackScript: [
                sandbox: true,
                script : 'return ["error"]'
              ],
              script: [
                  classpath: [],
                  sandbox: true,
                  script: """
                    import groovy.json.JsonSlurper
                    import jenkins.model.*
                    try {
                        def creds = Jenkins.instance.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getCredentials()
                        def cred = creds.find {
                            it.id == '$github_credentials_id'
                        }
                        def http = new URL('$github_repo').openConnection() as HttpURLConnection
                        http.setRequestMethod('GET')
                        http.setDoOutput(true)
                        http.setRequestProperty('Accept', 'application/json')
                        http.setRequestProperty('Authorization', "token \${cred.secret}")
                        http.connect()
                        def response = [:]
                        if (http.responseCode == 200) {
                            response = new JsonSlurper().parseText(http.inputStream.getText('UTF-8'))
                            def resArr = []
                            response .each { it->
                                resArr.push(it.tag_name)
                            }
                            return resArr
                        } else {
                            response = new JsonSlurper().parseText(http.errorStream.getText('UTF-8'))
                            return [response]
                        }
                    } catch (Exception e) {
                        return ["error"]
                    }
                  """
              ]
          ]
  ]
}
