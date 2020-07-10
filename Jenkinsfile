pipeline {
  agent any
  stages {
      stage('SonarQube') {
        steps {
          sleep 5
        }
      }

      stage('Integration Test') {
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
        when { branch 'master' }
        steps {
          sleep 5
        }
      }
    }
  }
}
