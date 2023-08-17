pipeline {
    agent { docker { image 'python3' } }
    options {
        skipStagesAfterUnstable()
    }

    stages {
        stage('Make Virtual Env') {
            steps {
                sh "mkdir -p PnR/python"
                dir('./') {
                    withPythonEnv('PnR') {
                        sh 'pip install -r requirements.txt'
                    }
                }
            }
        }
        stage('Build') {
            steps {
                dir('./') {
                    withPythonEnv('PnR') {
                        sh 'python -m py_compile src/*.py'
                        stash(name: 'compiled-results', includes: 'src/*.py*')
                    }
                }
            }
        }
        stage('Test') {
            steps {
                dir('./') {
                    withPythonEnv('PnR') {
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
                    sh "cd src && zip PnR-${env.BUILD_ID} *.py*"
                }
            }
            post {
                success {
                    archiveArtifacts "${env.BUILD_ID}/src/PnR-${env.BUILD_ID}.zip" 
                }
            }
        }
    }
}
