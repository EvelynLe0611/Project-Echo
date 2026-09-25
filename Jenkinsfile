pipeline {
    agent any

    environment {
        IMAGE_NAME = 'echo-api'
        VERSION    = "1.0.${BUILD_NUMBER}"
    }

    // Check GitHub for new commits every 2 minutes
    triggers {
        pollSCM('H/2 * * * *')
    }

    options {
        timestamps()
    }

    stages {
        stage('Build') {
            steps {
                script {
                    env.GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                }
                echo "Building ${IMAGE_NAME} version ${VERSION} (commit ${GIT_SHORT})"
                sh '''
                    docker build \
                      -f src/production/backend/API.Dockerfile \
                      -t ${IMAGE_NAME}:${VERSION} \
                      -t ${IMAGE_NAME}:${GIT_SHORT} \
                      -t ${IMAGE_NAME}:latest \
                      --label version=${VERSION} \
                      --label git-commit=${GIT_SHORT} \
                      src/production/backend
                '''
                sh 'docker images ${IMAGE_NAME}'
            }
        }
    }
}