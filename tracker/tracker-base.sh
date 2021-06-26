#!/bin/sh

apk update
apk add -u chrony
echo "refclock PHC /dev/ptp0 poll -2 dpoll -2 offset 0 trust prefer" > /etc/chrony/chrony.conf