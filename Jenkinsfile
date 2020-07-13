pipeline {
  agent any
  stages {
    stage('SonarQube') {
      steps {
        script {
          // requires SonarQube Scanner 2.8+
          scannerHome = tool 'SonarQube Scanner'
          withSonarQubeEnv('SonarQube Server') {
            sh "${scannerHome}/bin/sonar-scanner"
          }
        }
      }
    }

    stage('PyLint') {
      steps {
            // Run Pylint.
            sh script:'python3 -m pylint --rcfile=pylint.cfg felucca/backend > pylint.report --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"', returnStatus:true

            // Run Pycodestyle (PEP8 checks).
            sh script:'python3 -m pycodestyle felucca/backend > pep8.report', returnStatus:true
      }
      post {
          always{
              // Generate JUnit, PEP8, Pylint and Coverage reports.
              recordIssues enabledForFailure: true, tool: pyLint(pattern: 'pylint.report')
              recordIssues enabledForFailure: true, tool: pep8(pattern: 'pep8.report')
          }
      }
    }

    stage('Test') {
      steps {
        sh """. /tmp/Felucca/env/venv/bin/activate
        cd tests/unit_test/backend
        python3 resource_manager_test.py
        python3 job_manager_test.py
        deactivate
        """
      }
    }

    stage('Fetch') {
      when {branch 'master'}
      steps {
        sh 'chmod 0744 ./fetch.sh'
        sh './fetch.sh'
      }
    }

    stage('Doc Generation') {
      when {branch 'master'}
      steps {
        sh """. /tmp/Felucca/env/venv/bin/activate
        cd /var/tmp/Felucca/doc &&  sphinx-apidoc -o /tmp/Felucca/doc/source ../felucca/backend
        deactivate
        """
      }
    }

    stage('Deploy') {
      when {branch 'master'}
      steps {
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
  post {
    always {
      cleanWs()
    }
  }
}
