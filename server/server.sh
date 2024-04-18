#!/bin/sh

#
# This file is part of Celestial's Videoconferencing Evaluation
# (https://github.com/OpenFogStack/celestial-videoconferencing-evaluation).
# Copyright (c) 2021 Tobias Pfandzelter, The OpenFogStack Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


MY_IP=$(/sbin/ip route | sed -n '2 p' | awk '{print $9}')

echo "STARTING SERVER"

sed -i -e "s/%%%HOST%%%/$MY_IP/g" multiply.nft

ip link add name vethinj up type veth peer name vethgw
ip link set vethgw up

sysctl -w net.ipv4.conf.vethgw.forwarding=1
sysctl -w net.ipv4.conf.vethgw.accept_local=1
sysctl -w net.ipv4.conf.vethgw.rp_filter=0
sysctl -w net.ipv4.conf.all.rp_filter=0
ip route add $MY_IP/32 dev vethinj

sleep 1

nft -f multiply.nft

sleep 10

while true ; do
   sleep 10
done
