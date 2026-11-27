// Delivery pipeline foundation (Guide 8.2). Application stages stay unavailable until their
// prerequisites exist; they never report success for something that did not run.
pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds(); timeout(time: 60, unit: 'MINUTES') }
  triggers {
    pollSCM('H/2 * * * *')   // webhooks cannot reach a laptop
    cron('H 2 * * *')        // nightly evaluation
  }
  environment {
    NAMESPACE = 'idea-validator'
    REGISTRY  = 'ghcr.io/abdullah-se-bit'
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
        script { env.TAG = env.GIT_COMMIT.take(7) }
      }
    }
    stage('Prerequisites') {
      steps {
        script {
          env.DEPLOYABLE = sh(returnStatus: true, script: './scripts/ci/deployable.sh') == 0 ? 'true' : 'false'
          if (env.DEPLOYABLE != 'true') {
            currentBuild.result = 'NOT_BUILT'
            echo 'No module images exist yet: delivery stages are unavailable. Nothing is built or deployed.'
          }
        }
      }
    }
    stage('Build') {
      when { environment name: 'DEPLOYABLE', value: 'true' }
      steps { sh './scripts/ci/build_images.sh "$REGISTRY" "$TAG"' }
    }
    stage('Push') {
      when { environment name: 'DEPLOYABLE', value: 'true' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'registry', usernameVariable: 'REG_USER', passwordVariable: 'REG_TOKEN')]) {
          sh 'echo "$REG_TOKEN" | docker login ghcr.io -u "$REG_USER" --password-stdin'
          sh './scripts/ci/push_images.sh "$REGISTRY" "$TAG"'
        }
      }
    }
    stage('Deploy') {
      when { environment name: 'DEPLOYABLE', value: 'true' }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-test', variable: 'KUBECONFIG')]) {
          script { env.DEPLOY_STARTED = 'true' }
          sh './scripts/ci/deploy.sh "$REGISTRY" "$TAG" "$NAMESPACE"'
        }
      }
    }
    stage('Smoke test') {
      when { environment name: 'DEPLOYABLE', value: 'true' }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-test', variable: 'KUBECONFIG')]) {
          sh './scripts/smoke_test.sh "$NAMESPACE"'
        }
      }
    }
    stage('Nightly evaluation') {
      when {
        allOf { triggeredBy 'TimerTrigger'; environment name: 'DEPLOYABLE', value: 'true' }
      }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-test', variable: 'KUBECONFIG')]) {
          sh './scripts/check_eval.sh "$NAMESPACE"'
        }
      }
    }
  }
  post {
    failure {
      script {
        if (env.DEPLOY_STARTED == 'true') {
          // failed during deployment, smoke test or evaluation: block promotion and undo this run's changes
          withCredentials([file(credentialsId: 'kubeconfig-test', variable: 'KUBECONFIG')]) {
            sh './scripts/ci/rollback.sh "$NAMESPACE"'
          }
          echo 'Checks failed after deployment started; changes of this run were rolled back. Nothing promoted.'
        } else {
          echo 'Pipeline failed before deployment; nothing was deployed.'
        }
      }
    }
  }
}
