/* Requires the Docker Pipeline plugin */
pipeline {
    agent { docker { image 'python:3.11.3' } }
    stages {
        stage('build') {
            steps {
                sh 'python --version'
            }
        }
    }
}
