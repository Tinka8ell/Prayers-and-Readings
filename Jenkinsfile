pipeline {
    agent { dockerfile true }

    options {
        skipStagesAfterUnstable()
    }

    stages {
        stage('Build') {
            steps {
                sh 'python -m py_compile src/*.py'
                stash(name: 'compiled-results', includes: 'src/*.py*')
            }
        }

        stage('Test') {
            steps {
                sh "python3 -m pytest --junit-xml test-reports/results.xml src/test*.py"
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }

        stage('Deliver') { 
            steps {
                dir(path: env.BUILD_ID) { 
                    unstash(name: 'compiled-results') 
                    sh "ls -l src/"
                    sh "rm -f src/test*"
                    sh "ls -l src/"
                    sh "cd src && zip python-${env.BUILD_ID} *.py*"
                }
            }
            post {
                success {
                    archiveArtifacts "${env.BUILD_ID}/src/python-${env.BUILD_ID}.zip" 
                }
            }
        }
    }
}
