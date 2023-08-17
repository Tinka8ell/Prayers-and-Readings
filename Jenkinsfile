pipeline {
    agent { docker { image 'python3' } }
    options {
        skipStagesAfterUnstable()
    }

    stages {
        stage('Make Virtual Env') {
            steps {
                withPythonEnv('Python3') {
                    sh 'pip install -r requirements.txt'
                }
            }
        }
        stage('Build') {
            steps {
                dir('./') {
                    withPythonEnv('Python3') {
                        sh 'python -m py_compile src/*.py'
                        stash(name: 'compiled-results', includes: 'src/*.py*')
                    }
                }
            }
        }
        stage('Test') {
            steps {
                dir('./') {
                    withPythonEnv('Python3') {
                        sh "python3 -m pytest"
                        sh 'py.test --junit-xml test-reports/results.xml src/test*.py'
                    }
                }
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
