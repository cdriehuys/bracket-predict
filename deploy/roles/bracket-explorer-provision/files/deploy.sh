#!/usr/bin/env bash

set -euf
set -o pipefail

site_owner=bracket-explorer
app_root=/opt/bracket-explorer

run() {
    sudo -u "${site_owner}" "$@"
}

manage_cmd() {
    pushd "${app_root}/bracket_explorer" > /dev/null
    local manage_cmd=(poetry run ./manage.py "$@")

    echo
    echo "Running management command: ${manage_cmd[@]}"

    # Use `-a` flag so that sourcing the environment gets applied to the child
    # process when running the management command.
    run bash -ac "source /etc/bracket-explorer/environment; ${manage_cmd[*]}"

    popd > /dev/null
}

pushd "${app_root}" > /dev/null

echo
echo "Updating source code..."
run git pull

echo
echo "Installing dependencies..."
run poetry install --only main

manage_cmd tailwind install
manage_cmd tailwind build
manage_cmd collectstatic --no-input

manage_cmd migrate --no-input

# If the app is active, reload it to read the updated source code. If it isn't
# active, it will read the updated source code when it starts.

echo
if sudo systemctl reload bracket-explorer.service ; then
    echo "Reloaded bracket-explorer.service"
else
    echo "Did not reload bracket-explorer.service because it's not running."
fi
