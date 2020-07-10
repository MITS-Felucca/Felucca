pipeline {
  agent any
  stages {
    if (env.BRANCH_NAME == 'master') {
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
        steps {
          sleep 5
        }
      }
    } else {
      stage('SonarQube') {
        steps {
          sleep 5
        }
      }

      stage('Unit Test') {
        steps {
          sleep 5
        }
      }

      stage('Doc Generation') {
        steps {
          sleep 5
        }
      }
    }
  }
}
