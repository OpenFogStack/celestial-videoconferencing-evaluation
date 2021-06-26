#!/bin/sh

rc-service chronyd start

IP=$(/sbin/ip route | awk '/default/ { print $3 }')

echo nameserver "$IP" > /etc/resolv.conf

chronyc tracking

chronyc -a makestep

sleep 10

chronyc tracking

chronyc -a makestep

chronyc tracking

sleep 10

chronyc tracking

sleep 10

echo "STARTING TRACKER"
/tracker.bin --update-interval=5 --gateway="$IP"