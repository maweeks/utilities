#!/usr/bin/env bash

GIT_STATUS=""
OUTPUT_DIR="testOutput/"

if [[ $(git diff "$OUTPUT_DIR") ]] ; then
    echo "Clear git diff before running."
    exit 1
else
    echo "Git diff clear."
    GIT_STATUS=$(git status)
    echo "${GIT_STATUS}"
fi

rm -f testOutput/*.md testOutput/*.txt

GITHUB=$1
JIRA=$2
REPO="test-utilities"

# 56: Commit on develop.
# 57: Commit on develop with ticket
# 58: Commits on develop with different tickets
# 59: Commits on develop with same ticket
# 60: Commit on develop with multiple tickets# 61: 2 TC commits
# 63: Branch without ticket, commit without ticket
# 67: Branch without ticket, commit with ticket
# 69: Branch without ticket, commits with different tickets
# 74: Branch with ticket, commit without ticket
# 77: Branch with ticket, commit with ticket
# 80: Multiple branches, with multiple tickets
# 83: Multiple branches, single ticket
# 87: Multiple branches, multiple commits, multiple tickets
# 89: Branch with ticket, commit with ticket
#     Commit with ticket
#     TC commit

prs=("56" "57" "58" "59" "60" "61" "63" "67" "69" "74" "77" "80" "83" "87" "89")
versions=("3.0.58" "3.0.59" "3.0.60" "3.0.61" "3.0.62" "3.0.63" "3.0.64"
        "3.0.65" "3.0.66" "3.0.69" "3.0.70" "3.0.71" "3.0.72" "3.0.74" "3.0.75")

for (( n=0; n<=14; n++ ))
do
    python updatePR.py $REPO "${prs[n]}" "${versions[n]}" "Y" "N" "N" "N" "Y" "N" "$GITHUB" "$JIRA" "SLACK" "$OUTPUT_DIR"
done

GIT_STATUS_2=$(git status)

if [ "$GIT_STATUS" == "$GIT_STATUS_2" ]; then
    echo "All tests passed!"
else
    echo "Tests failed, check git diff for issues."
fi
