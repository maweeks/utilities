#!/usr/bin/env bash

GIT_STATUS=""
if [[ $(git diff) ]] ; then
    echo "Clear git diff before running."
    exit 1
else
    echo "Git diff clear."
    GIT_STATUS=$(git status)
    echo "${GIT_STATUS}"
fi

rm -f testOutput/*.md

GITHUB=$1
REPO="test-utilities"

# 55: Basic test with single commit in other.
python updatePR.py $REPO "55" "3.0.57" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "testOutput/"

GIT_STATUS_2=$(git status)

if [ "$GIT_STATUS" == "$GIT_STATUS_2" ]; then
    echo "All tests passed!"
else
    echo "Tests failed, check git diff for issues."
fi
