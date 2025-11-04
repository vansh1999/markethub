pipeline {
    
    agent { label 'jenkins-agent' }
    
    stages{
        
        stage("Code"){
            steps{
                git url: 'https://github.com/vansh1999/markethub.git' , branch: 'main' 
                echo "Code received successfully from github +++"
                
            }
        }
        
        stage("Build and Test"){
            steps{
                sh 'docker build . -t markethub'
            }
        }
        
    //     stage("login in dockerhub"){
	//          steps{
    //              withCredentials([usernamePassword(credentialsID: 'markethub-pass' , passwordVariable: 'dockerHubPassword' , usernameVariable: 'dockerHubUsername' )]){
	// 	                sh 'docker login -u ${env.dockerHubUsername} -p ${dockerHubPassword}''
    //                      }
    //             }
    //     }
        
        stage("Deploy"){
            steps{
                sh '''

      			CONTAINER_ID=$(docker ps -q --filter publish=8000)

			if [ -n "$CONTAINER_ID" ]; then
  				docker stop $CONTAINER_ID
			else
  				echo "No container is using port 8000"
			fi

		    
		    
		    	docker run -d -p 8000:8000 markethub:latest


		        '''
		    
            }
        }
        
        
    }
    
    
}
