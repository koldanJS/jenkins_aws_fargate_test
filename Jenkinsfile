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
    stages {
        stage('Hello') {
            steps {
                echo 'Hello World'
            }
        }
    }
}