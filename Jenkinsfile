pipeline {
    agent {
       kubernetes {
           yaml """
apiVersion: v1 
kind: Pod 
metadata: 
    name: img 
    annotations:
      container.apparmor.security.beta.kubernetes.io/img: unconfined
      container.seccomp.security.alpha.kubernetes.io/img: unconfined
spec: 
    containers: 
      - name: img
        image: r.j3ss.co/img
        command: ['cat']
        tty: true
"""
       }
   }

    parameters { 
        string(name: 'DOCKER_REGISTRY_URL', defaultValue: 'https://ghcr.io', description: 'Docker image registry URL used for authentication') 
        string(name: 'DOCKER_IMAGE_URL', defaultValue: 'ghcr.io/rpenziol/audiosync', description: 'Fully-qualified URL for the Docker image registry') 
        string(name: 'PUBLISH_DOCKER_IMAGE', defaultValue: 'false', description: 'true/false whether to publish Docker image to Docker image registry') 
        string(name: 'DOCKER_IMAGE_TAG', defaultValue: 'latest', description: 'Docker image tag') 
    }
    
    environment {
        GITHUB = credentials('GITHUB')
    }

    stages {
        stage('Checkout') {
            steps {
                container("img") {
                    checkout scm
                }
            }
        }
        stage('Build Image') {
            steps {
                container("img") {
                    sh "img build -f Dockerfile -t audiosync . -t $params.DOCKER_IMAGE_URL:$params.DOCKER_IMAGE_TAG"
                }
            }
        }
        stage('Push Production Image') {
            when {
                expression { params.PUBLISH_DOCKER_IMAGE == 'true' }
            }
            steps {
                container("img") {
                    sh "img login $params.DOCKER_REGISTRY_URL -u $GITHUB_USR -p $GITHUB_PSW"
                    sh "img push $params.DOCKER_IMAGE_URL:$params.DOCKER_IMAGE_TAG"
                }
            }
        }
   }
}