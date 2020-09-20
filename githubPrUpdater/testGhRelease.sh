cd ../../test-utilities
git checkout develop
git pull
date > randomChange.txt
git add *
git commit -m "Change."
sleep 2
git push
sleep 3
gh pr create -t "Release" -b ""
sleep 3
gh pr merge -m # -d false
git checkout master
git pull

PR_NUMBER=$(git log -1 --pretty=%B | head -n 1 | sed 's/[^0-9]*//g')

npm version patch

VERSION=$(git log -1 --pretty=%B)

git push --all
git push --tags
git checkout develop
git merge master --no-edit
git push

REPO=$(basename `git rev-parse --show-toplevel`)

cd ../utilities/githubPRUpdater

echo $REPO
echo $PR_NUMBER
echo $VERSION

python updatePR.py $REPO $PR_NUMBER $VERSION "Y" "Y" "Y" "GITHUB" "JIRA"
