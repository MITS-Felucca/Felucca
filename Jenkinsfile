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
        sh 'cp felucca.service /etc/systemd/system/felucca.service'
        sh 'chmod 0644 /etc/systemd/system/felucca.service'
        sh 'systemctl restart felucca'
      }
    }
  }
}
