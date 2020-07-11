pipeline {
  agent any
  stages {
    stage('SonarQube') {
      steps {
        script {
          // requires SonarQube Scanner 2.8+
          scannerHome = tool 'SonarQube Scanner'
          withSonarQubeEnv('SonarQube Server') {
            sh "${scannerHome}/bin/sonar-scanner -v"
          }
        }
        sleep 5
      }
    }

    stage('Test') {
      steps {
        sleep 1
      }
    }

    stage('Doc Generation') {
      steps {
        sleep 1
      }
    }

    stage('Deploy') {
      steps {
        sh 'chmod 0744 ./fetch.sh'
        sh './fetch.sh'
        sh '/tmp/Felucca/mongodb.sh'
        sh 'sudo cp felucca.service /etc/systemd/system/felucca.service'
        sh 'sudo chmod 0644 /etc/systemd/system/felucca.service'
        sh 'sudo systemctl daemon-reload'
        sh 'sudo systemctl stop felucca'
        sleep 1
        sh 'sudo systemctl start felucca'
      }
    }
  }
}
