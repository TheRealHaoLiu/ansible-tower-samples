pipeline {
    agent {
        docker {
            registryUrl "https://artifactory.marriott.com/artifactory"
            registryCredentialsId "ARTIFACTORY"
            image "artifactory.marriott.com/network-devops/ci_runner:latest"
            reuseNode false
            args '-u root --privileged'
        }
    }

    stages {
        stage('Lint') {
            steps {
                sh "ruff ."
                sh "ansible-lint"
            }
        }
    }
}
