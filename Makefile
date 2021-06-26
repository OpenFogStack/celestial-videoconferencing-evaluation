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

.PHONY: all

all: client.ext4 server.ext4 tracker.ext4 alt-tracker.ext4

client.ext4: client/client.sh client/client-base.sh client/workload.csv client/ultra_ping
	@docker run --rm -v $(PWD)/client/client.sh:/app.sh -v $(PWD)/client/client-base.sh:/base.sh -v $(PWD)/client/workload.csv:/files/workload.csv -v $(PWD)/client/ultra_ping:/files/ultra_ping -v $(PWD)/client:/opt/code --privileged rootfsbuilder 300 $@

alt-tracker.ext4: tracker/tracker.bin tracker/alt-tracker.sh
	@docker run --rm -v $(PWD)/tracker/alt-tracker.sh:/app.sh -v $(PWD)/tracker/tracker-base.sh:/base.sh -v $(PWD)/tracker/tracker.bin:/files/tracker.bin -v $(PWD)/tracker:/opt/code --privileged rootfsbuilder 50 $@

tracker.ext4: tracker/tracker.bin tracker/tracker.sh
	@docker run --rm -v $(PWD)/tracker/tracker.sh:/app.sh -v $(PWD)/tracker/tracker-base.sh:/base.sh -v $(PWD)/tracker/tracker.bin:/files/tracker.bin -v $(PWD)/tracker:/opt/code --privileged rootfsbuilder 50 $@

tracker/tracker.bin: tracker/cmd/tracker tracker/go.mod
	@cd tracker ; GOOS=linux GOARCH=amd64 go build -o tracker.bin ./cmd/tracker

server.ext4: server/server.sh server/multiply.nft server/server-base.sh
	@docker run --rm -v $(PWD)/server/server.sh:/app.sh -v $(PWD)/server/server-base.sh:/base.sh -v $(PWD)/server/multiply.nft:/files/multiply.nft -v $(PWD)/server:/opt/code --privileged rootfsbuilder 30 $@