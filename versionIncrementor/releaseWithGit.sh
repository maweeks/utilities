#!/bin/bash

file="VERSION.txt"

version=$(cat "$file")

git add $file

if [ ! -z "$MESSAGE" ]
then
    git commit -m "$version - $MESSAGE"
else
    git commit -m "$version"
fi

git tag $version

prURL=$(git push | grep https)

git push --tags

if [ ! -z $prURL ]
then
    open $prURL
fi
