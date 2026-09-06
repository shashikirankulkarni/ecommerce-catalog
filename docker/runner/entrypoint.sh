#!/bin/bash
#
# Registers the runner on first start, then runs it.
#
# A registration token is NOT a credential you store - it is minted on
# demand and expires after one hour. Once the runner is configured it
# holds its own long-lived credential in .credentials, which is why the
# token being short-lived costs nothing.

set -euo pipefail

: "${GH_REPO_URL:?set GH_REPO_URL, e.g. https://github.com/owner/repo}"
: "${RUNNER_TOKEN:?set RUNNER_TOKEN - get one with: gh api -X POST repos/OWNER/REPO/actions/runners/registration-token --jq .token}"

RUNNER_NAME="${RUNNER_NAME:-catalog-runner}"
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,linux,arm64,catalog}"

cd /home/runner

# Docker creates a volume's mount point owned by root, but this runner
# executes as `runner` - config.sh refuses to run as root. Anything the
# runner is expected to write to has to be handed over at startup.
for dir in /srv/frontend; do
    if [ -d "$dir" ] && [ ! -w "$dir" ]; then
        echo "runner: taking ownership of $dir"
        sudo chown -R runner:runner "$dir"
    fi
done

cleanup() {
    echo "runner: removing registration"
    ./config.sh remove --token "${RUNNER_TOKEN}" || true
}

if [ ! -f .runner ]; then
    echo "runner: registering ${RUNNER_NAME} with labels ${RUNNER_LABELS}"
    ./config.sh \
        --unattended \
        --url "${GH_REPO_URL}" \
        --token "${RUNNER_TOKEN}" \
        --name "${RUNNER_NAME}" \
        --labels "${RUNNER_LABELS}" \
        --work _work \
        --replace
else
    echo "runner: already configured, reusing existing registration"
fi

# Deregister cleanly on stop, so GitHub does not keep an offline runner.
trap cleanup EXIT SIGINT SIGTERM

./run.sh
