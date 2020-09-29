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
OUTPUT_DIR="testOutput/"
REPO="test-utilities"

# 56: Commit on develop.
python updatePR.py $REPO "56" "3.0.58" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 57: Commit on develop with ticket
python updatePR.py $REPO "57" "3.0.59" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 58: Commits on develop with different tickets
python updatePR.py $REPO "58" "3.0.60" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 59: Commits on develop with same ticket
python updatePR.py $REPO "59" "3.0.61" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 60: Commit on develop with multiple tickets
python updatePR.py $REPO "60" "3.0.62" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 61: 2 TC commits
python updatePR.py $REPO "61" "3.0.63" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 63: Branch without ticket, commit without ticket
python updatePR.py $REPO "63" "3.0.64" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 67: Branch without ticket, commit with ticket
python updatePR.py $REPO "67" "3.0.65" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 69: Branch without ticket, commits with different tickets
python updatePR.py $REPO "69" "3.0.66" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 74: Branch with ticket, commit without ticket
python updatePR.py $REPO "74" "3.0.69" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 77: Branch with ticket, commit with ticket
python updatePR.py $REPO "77" "3.0.70" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 80: Multiple branches, with multiple tickets
python updatePR.py $REPO "80" "3.0.71" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 83: Multiple branches, single ticket
python updatePR.py $REPO "83" "3.0.72" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 87: Multiple branches, multiple commits, multiple tickets
python updatePR.py $REPO "87" "3.0.74" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"

# 89: Branch with ticket, commit with ticket
#     Commit with ticket
#     TC commit
python updatePR.py $REPO "89" "3.0.75" "Y" "N" "N" "$GITHUB" "JIRA" "Y" "$OUTPUT_DIR"


GIT_STATUS_2=$(git status)

if [ "$GIT_STATUS" == "$GIT_STATUS_2" ]; then
    echo "All tests passed!"
else
    echo "Tests failed, check git diff for issues."
fi
