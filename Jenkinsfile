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
        sh 'fetch.sh'
        sh 'cp felucca.service /etc/systemd/system/felucca.service'
        sh 'chmod 0644 /etc/systemd/system/felucca.service'
        sh 'systemctl restart felucca'
      }
    }
  }
}
