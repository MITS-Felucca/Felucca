pipeline {
  agent any
  stages {
    stage('SonarQube') {
      steps {
        script {
          // requires SonarQube Scanner 2.8+
          scannerHome = tool 'SonarQube Scanner'
        }
        withSonarQubeEnv('SonarQube Scanner') {
          echo "${scannerHome}/bin/sonar-scanner"
        }
      }
      // steps {
      //   sleep 5
      // }
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
      when { branch 'master' }
      steps {
        sleep 5
      }
    }
  }
}
