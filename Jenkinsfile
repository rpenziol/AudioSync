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
        string(name: 'DOCKER_REPOSITORY_STAGE', defaultValue: 'audiosync', description: 'Name of the image to be built for scanning (e.g.: rpenziol/audiosync-staging)') 
        string(name: 'DOCKER_REPOSITORY_PROD', defaultValue: 'audiosync', description: 'Name of the image to be built for production (e.g.: rpenziol/audiosync)') 
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
                    sh "img build -f Dockerfile -t audiosync ."
                }
            }
        }
   }
}