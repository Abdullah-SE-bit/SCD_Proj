# Jenkins with the Docker CLI and kubectl (Guide 8.2, JNK-003). Build context: scripts/jenkins.
FROM jenkins/jenkins:lts-jdk21@sha256:161ec15b027ea80911256552191034bf2aaede1aa39dd06ca1fef60d9b585be5
USER root
COPY --from=docker:29-cli@sha256:4e60c31615e83523afbb59773b25d055c0da9edcd5f80a4c6a6eebad49de1a25 /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:29-cli@sha256:4e60c31615e83523afbb59773b25d055c0da9edcd5f80a4c6a6eebad49de1a25 /usr/local/libexec/docker/cli-plugins/docker-buildx /usr/local/libexec/docker/cli-plugins/docker-buildx
RUN curl -fsSLo /usr/local/bin/kubectl https://dl.k8s.io/release/v1.36.4/bin/linux/amd64/kubectl \
 && echo "8b8f088da2dab964f853b38464033b1be15ede2839eca751482357c45abdd05a  /usr/local/bin/kubectl" | sha256sum -c - \
 && chmod 755 /usr/local/bin/kubectl
COPY plugins.yaml /usr/share/jenkins/ref/plugins.yaml
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.yaml
COPY casc.yaml /usr/share/jenkins/casc.yaml
ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/casc.yaml \
    JAVA_OPTS="-Xmx768m -Djenkins.install.runSetupWizard=false"
# Stays root: the pipeline drives the host's Docker socket, which only root can open on Docker Desktop.
