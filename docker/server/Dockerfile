# Application server.
#
# A container used as a VM, not as an application image: it is built once
# and then long-lived, and deployments copy a JAR into it over SSH. That
# is deliberate - it mirrors how a JAR reaches a real server, and keeps
# the moving parts visible.
#
# A JRE, not a JDK. Nothing is compiled here; the runner builds the JAR
# and only the artifact arrives.

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-21-jre-headless \
        openssh-server \
        supervisor \
        sudo \
        curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# sshd refuses to start without this directory.
RUN mkdir -p /run/sshd /var/log/supervisor

# The deploy account. No password is ever set, so password login is
# impossible regardless of configuration - only the key works.
RUN useradd -m -s /bin/bash deploy \
    && mkdir -p /opt/catalog /home/deploy/.ssh \
    && chown -R deploy:deploy /opt/catalog /home/deploy/.ssh \
    && chmod 700 /home/deploy/.ssh

COPY deploy_key.pub /home/deploy/.ssh/authorized_keys
RUN chown deploy:deploy /home/deploy/.ssh/authorized_keys \
    && chmod 600 /home/deploy/.ssh/authorized_keys

# Key-only authentication. Root login off, passwords off entirely.
RUN sed -i \
        -e 's/^#\?PermitRootLogin.*/PermitRootLogin no/' \
        -e 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' \
        -e 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' \
        -e 's/^#\?PermitEmptyPasswords.*/PermitEmptyPasswords no/' \
        /etc/ssh/sshd_config

# deploy needs to restart the app, and nothing else.
RUN echo 'deploy ALL=(ALL) NOPASSWD: /usr/bin/supervisorctl' > /etc/sudoers.d/deploy \
    && chmod 440 /etc/sudoers.d/deploy

COPY supervisord.conf /etc/supervisor/conf.d/catalog.conf

EXPOSE 22 8080

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
