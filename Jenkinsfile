pipeline {
    agent none
    options {
        skipStagesAfterUnstable()
    }
    stages {
        stage('Build') {
            agent { docker { image 'python3' } }
            steps {
                sh 'python -m py_compile src/*.py'
                stash(name: 'compiled-results', includes: 'src/*.py*')
            }
        }
        stage('Test') {
            agent { docker { image 'python3' } }
            steps {
                sh 'py.test --junit-xml test-reports/results.xml src/test_*.py'
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }
        stage('Deliver') { 
            agent any
            steps {
                dir(path: env.BUILD_ID) { 
                    unstash(name: 'compiled-results') 
                    sh "rm src/test_*"
                    sh "cd src && zip P&R-${env.BUILD_ID} *.py*"
                }
            }
            post {
                success {
                    archiveArtifacts "${env.BUILD_ID}/src/P&R-${env.BUILD_ID}.zip" 
                }
            }
        }
    }
}
