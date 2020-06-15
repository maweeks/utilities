#!/bin/bash

VERSION_ENDPOINT=""
NEW_VERSION=$1
LIVE_VERSION=$(curl -s $VERSION_ENDPOINT)
[[ $NEW_VERSION == $LIVE_VERSION ]] ; IS_DEPLOYED=$?

while [[ $IS_DEPLOYED == "1" ]]
do
    echo "Not yet finished deploying."
    sleep 5
    LIVE_VERSION=$(curl -s $VERSION_ENDPOINT)
    [[ $NEW_VERSION == $LIVE_VERSION ]] ; IS_DEPLOYED=$?
done

echo "Release is live. [$LIVE_VERSION]"
