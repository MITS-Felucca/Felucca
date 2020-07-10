pipeline {
  agent any
  stages {
    stage('SonarQube') {
      steps {
        sleep 5
      }
    }

    stage('Test') {
      steps {
        sleep 5
      }
    }

    stage('Doc Generation') {
      steps {
        sleep 5
      }
    }
    
    stage('Deploy') {
      if (env.BRANCH_NAME == 'master') {
        steps {
          sleep 5
        }
      }
    }
  }
}
