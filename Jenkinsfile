pipeline {

    // ✅ Changed from `agent { label 'jenkins-agent' }` to `agent any`
    agent any

    stages {
        
        stage("Code") {
            steps {
                git url: 'https://github.com/vansh1999/markethub.git', branch: 'main'
                echo "Code received successfully from GitHub +++"
            }
        }
        
        stage("Build and Test") {
            steps {
                sh 'docker build -t markethub:latest .'
            }
        }

        stage("Deploy") {
            steps {
                sh '''
                    # ✅ Stop existing container running on port 8000 (if any)
                    CONTAINER_ID=$(docker ps -q --filter "publish=8000")
                    if [ -n "$CONTAINER_ID" ]; then
                        echo "Stopping existing container..."
                        docker stop $CONTAINER_ID
                        docker rm $CONTAINER_ID
                    else
                        echo "No container running on port 8000"
                    fi

                    # ✅ Run new container
                    docker run -d -p 8000:8000 --name markethub markethub:latest
                '''
            }
        }
    }
}
