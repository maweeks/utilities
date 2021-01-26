#!/usr/bin/env bash
repo=$1
pr=$2

cd .. && git clone git@github.com:maweeks/release-notes.git && cd release-notes

if ! cat "${repo}.md" &> /dev/null ; then
    echo "Creating repository release notes file."
    touch "${repo}.md"
    echo "# ${repo}
" > "${repo}.md"
fi

echo "Adding ${repo} release notes."
echo "$(head -n 1 ${repo}.md)

$(cat ${repo}-${pr}.md)
$(tail -n +2 ${repo}.md)" > "${repo}.md" && cat "${repo}.md"

git add "${repo}.md"
git commit -m "Updating release notes."
git push
