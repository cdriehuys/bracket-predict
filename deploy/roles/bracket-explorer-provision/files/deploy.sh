#!/usr/bin/env bash

site_owner=bracket-explorer
app_root=/opt/bracket-explorer

run() {
    sudo -u "${site_owner}" "$@"
}

pushd "${app_root}"
run git pull
run poetry install --only main

pushd ./bracket_explorer
run poetry run ./manage.py tailwind install
run poetry run ./manage.py tailwind build

run poetry run ./manage.py collectstatic --no-input

sudo systemctl reload bracket-explorer.service
