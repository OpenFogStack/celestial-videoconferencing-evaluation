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

with open("vmstat.csv", "w") as out_file:

    out_file.write("t,free_mem,cpu\n")

    with open("vmstat.txt", "r") as vmstat_file:
        for line in vmstat_file:
            if "--" in line:
                continue

            components = re.split(r"\s+", line)

            t = components[-2]
            free_mem = components[4]
            cpu = components[13]

            out_file.write(t)
            out_file.write(",")
            out_file.write(free_mem)
            out_file.write(",")
            out_file.write(cpu)
            out_file.write("\n")
