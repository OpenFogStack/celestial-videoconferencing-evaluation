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

import re

with open("vmstatdisk.csv", "w") as out_file:

    out_file.write("t,io_cur,io_sec\n")

    with open("vmstatdisk.txt", "r") as vmstat_disk_file:
        for line in vmstat_disk_file:
            if not "sda" in line:
                continue

            components = re.split(r"\s+", line)

            t = components[-2]
            io_cur = components[9]
            io_sec = components[10]

            out_file.write(t)
            out_file.write(",")
            out_file.write(io_cur)
            out_file.write(",")
            out_file.write(io_sec)
            out_file.write("\n")
