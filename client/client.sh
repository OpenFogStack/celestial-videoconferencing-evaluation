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

echo "STARTING CLIENT"

NAME=$(curl -s "$IP"/self | python3 -c 'import sys, json; print(json.load(sys.stdin)["name"])')

echo "$NAME"
cd ultra_ping || exit

./quack.py --listen_port 3000 --http_port 8000 --n_packets 210000 --send_rate_kBps 200 --id "$NAME" --workload_file /workload.csv --client &
./quack.py --listen_port 3000 --output_filename udp_packetn_latency_pairs --n_packets 420000 --timeout 120 --server

sleep 20