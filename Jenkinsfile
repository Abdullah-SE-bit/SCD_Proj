// Delivery pipeline (Guide 8.2). A stage never reports success for something that did not run.
// Start Jenkins with scripts/jenkins_up.sh.
pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds(); timeout(time: 60, unit: 'MINUTES') }
  triggers {
    pollSCM('H/2 * * * *')   // webhooks cannot reach a laptop
    cron('H 2 * * *')        // nightly evaluation
  }
  parameters {
    booleanParam(name: 'FAIL_SMOKE', defaultValue: false,
                 description: 'Deliberately fail the smoke test after deployment, to show the rollback.')
  }
  environment {
    NAMESPACE = 'idea-validator'
    // The local registry started by jenkins_up.sh. For ghcr.io, set REGISTRY and add the 'registry' credential.
    REGISTRY  = "${env.REGISTRY_OVERRIDE ?: 'localhost:5001'}"
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
        script {
          if (env.REGISTRY.startsWith('ghcr.io/')) {
            withCredentials([usernamePassword(credentialsId: 'registry', usernameVariable: 'REG_USER', passwordVariable: 'REG_TOKEN')]) {
              sh 'echo "$REG_TOKEN" | docker login ghcr.io -u "$REG_USER" --password-stdin'
              sh './scripts/ci/push_images.sh "$REGISTRY" "$TAG"'
            }
          } else {
            sh './scripts/ci/push_images.sh "$REGISTRY" "$TAG"'
          }
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
          // the cluster is named like the namespace; a deliberate failure expects a text the app never sends
          sh '''if [ "$FAIL_SMOKE" = true ]; then export SMOKE_EXPECT="deliberate failure"; fi
                ./scripts/smoke_test.sh "$NAMESPACE"'''
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
