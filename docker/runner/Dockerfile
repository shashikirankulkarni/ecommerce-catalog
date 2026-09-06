# GitHub Actions self-hosted runner.
#
# Deliberately a plain Ubuntu box with a JDK and Maven on it, rather than
# a purpose-built CI image - it stands in for a build server you would be
# given in a real environment.
#
# arm64, because this runs on Apple Silicon. A cloud VM would almost
# certainly be x86_64, which is a real source of "works on the runner,
# fails in production" problems: native libraries and container images
# built here will not run there.

FROM ubuntu:24.04

ARG RUNNER_VERSION=2.337.0
ARG RUNNER_ARCH=arm64

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl jq git sudo unzip zip tar gzip \
        openssh-client rsync \
        openjdk-21-jdk-headless maven \
    && rm -rf /var/lib/apt/lists/*

# The runner refuses to configure or run as root, by design.
RUN useradd -m -s /bin/bash runner \
    && echo "runner ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/runner

USER runner
WORKDIR /home/runner

RUN curl -fsSL -o runner.tar.gz \
      "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" \
    && tar xzf runner.tar.gz \
    && rm runner.tar.gz

# Runtime dependencies the runner needs (ICU, libssl and friends).
RUN sudo ./bin/installdependencies.sh

COPY --chown=runner:runner entrypoint.sh /home/runner/entrypoint.sh
RUN chmod +x /home/runner/entrypoint.sh

ENTRYPOINT ["/home/runner/entrypoint.sh"]
