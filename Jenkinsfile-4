pipeline {
    agent any

    stages {
        stage('Hello') {
            steps {
                echo 'Hello World'
                echo "Build number is ${currentBuild.number}"
            }
            post {
                success {
                    script {
                        currentBuild.result = "FAILURE"
                    }
                }
            }
        }
    }
    post {
        always {
            echo currentBuild.currentResult
        }
    }
}
