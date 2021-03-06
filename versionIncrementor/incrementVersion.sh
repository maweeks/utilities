#!/bin/bash

file="VERSION.txt"

version=$(cat "$file")

case $VERSION in
    M|major ) major=true;;
    m|minor ) minor=true;;
    p|patch ) patch=true;;
esac

shift $(($OPTIND - 1))

a=( ${version//./ } )

if [ ${#a[@]} -ne 3 ]
then
    echo "usage: $(basename $0) [-Mmp] major.minor.patch"
    exit 1
fi

if [ ! -z $major ]
then
    ((a[0]++))
    a[1]=0
    a[2]=0
fi

if [ ! -z $minor ]
then
    ((a[1]++))
    a[2]=0
fi

if [ ! -z $patch ]
then
    ((a[2]++))
fi

newVersion="${a[0]}.${a[1]}.${a[2]}"



if [ ! -z "$MESSAGE" ]
then
    echo $newVersion - $MESSAGE
else
    echo $newVersion
fi

echo $newVersion > $file
