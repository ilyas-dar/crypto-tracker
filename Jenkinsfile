pipeline {
    agent any

    parameters {
        string(name: 'EC2_HOST', defaultValue: '', description: 'EC2 public IP (from terraform output). Leave empty to skip deploy.')
    }

    environment {
        DOCKERHUB_USER = 'YOUR_DOCKERHUB_USERNAME'   // <-- change this
        IMAGE          = "${DOCKERHUB_USER}/crypto-tracker"
        TAG            = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit tests') {
            steps {
                // runs pytest in a throwaway Python container (mocked API, no internet calls to CoinGecko)
                sh '''
                  docker run --rm -v "$PWD":/work -w /work python:3.12-slim \
                    sh -c "pip install -q -r requirements.txt && pytest -q"
                '''
            }
        }

        stage('Build image') {
            steps {
                sh 'docker build -t $IMAGE:$TAG -t $IMAGE:latest .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    sh '''
                      echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                      docker push $IMAGE:$TAG
                      docker push $IMAGE:latest
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            when { expression { return params.EC2_HOST?.trim() } }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'KEY')]) {
                    sh '''
                      ssh -o StrictHostKeyChecking=no -i "$KEY" ec2-user@$EC2_HOST \
                        "cd ~/crypto-tracker && git pull && docker compose pull && docker compose up -d"
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
        success { echo 'Pipeline finished successfully.' }
        failure { echo 'Pipeline failed. Check the stage logs.' }
    }
}
