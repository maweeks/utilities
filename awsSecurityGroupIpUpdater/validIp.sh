#!/bin/bash
# https://www.linuxjournal.com/content/validating-ip-address-bash-script

ip=$1
stat=1

if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    OIFS=$IFS
    IFS='.'
    ip=($ip)
    IFS=$OIFS
    [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
        && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
    stat=$?
fi

if [[ $stat -eq 1 ]]; then
    echo "Invalid IP address."
    exit 1;
fi
