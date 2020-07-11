pipeline {
  agent any
  stages {
    stage('SonarQube') {
      steps {
        // script {
        //   // requires SonarQube Scanner 2.8+
        //   scannerHome = tool 'SonarQube Scanner'
        //   withSonarQubeEnv('SonarQube Server') {
        //     sh "${scannerHome}/bin/sonar-scanner"
        //   }
        // }
        sleep 1
      }
    }

    stage('PyLint') {
      steps {
            // Run my project tests.
            // sh 'coverage run manage.py tests'

            // Dump coverage metrics to XML.
            // sh 'coverage xml'

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
        python3 tests/unit_test/backend/*.py
        deactivate
        """
      }
    }

    stage('Doc Generation') {
      steps {
        sleep 1
      }
    }

    stage('Deploy') {
      when { branch 'master' }
      steps {
        sleep 1
      }
    }
  }
  // post {
  //   always {
  //     cleanWs()
  //   }
  // }
}
