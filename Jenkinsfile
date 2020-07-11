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
        // sleep 5
      }
    }

    stage('PyLint') {
      steps {
            // Run my project tests.
            // sh 'coverage run manage.py tests'

            // Dump coverage metrics to XML.
            // sh 'coverage xml'

            // Run Pylint.
            sh 'pylint --rcfile=pylint.cfg felucca/backend > pylint.report'

            // Run Pycodestyle (PEP8 checks).
            sh 'pycodestyle felucca/backend > pep8.report'
      }
      post {
          always{
              // Generate JUnit, PEP8, Pylint and Coverage reports.
              // junit 'reports/*junit.xml'
              recordIssues enabledForFailure: true, tool: pyLint(pattern: 'pylint.report')
              recordIssues enabledForFailure: true, tool: pep8(pattern: 'pep8.report')
              // recordIssues(
              //     tool: pep8(pattern: 'pep8.report'),
              //     unstableTotalAll: 200,
              //     failedTotalAll: 220
              // )
              // recordIssues(
              //     tool: pyLint(pattern: 'pylint.report'),
              //     unstableTotalAll: 20,
              //     failedTotalAll: 30
              // )
              // cobertura coberturaReportFile: 'reports/coverage.xml'
          }
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
      when { branch 'master' }
      steps {
        sleep 1
      }
    }
  }
  post {
    always {
      cleanWs()
    }
  }
}
