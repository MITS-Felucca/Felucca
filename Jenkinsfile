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
      steps {
        sh 'chmod 0744 ./fetch.sh'
        sh 'chmod 0744 ./felucca.sh'
        sh './fetch.sh'
        sh 'sudo cp felucca.service /etc/systemd/system/felucca.service'
        sh 'sudo chmod 0644 /etc/systemd/system/felucca.service'
        sh 'sudo systemctl daemon-reload'
        sh 'sudo systemctl restart felucca'
      }
    }
  }
}
