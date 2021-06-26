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

with open("top_results.csv", "w") as top_out_file:

    top_out_file.write("t,cpu,mem,type,name\n")

    with open("topoutput.txt", "r") as top_file:
        t = ""
        for line in top_file:
            if line == "\n":
                continue
            if "[" in line:
                continue
            if line[:6] == "top - ":
                t = line[6:14]
                continue
            if re.match(r"\d+\sroot\s+0\s+-20", line) is None:
                continue

            components = re.split(r"\s+", line)

            cpu = components[8]
            mem = components[9]
            command = components[11:]

            top_out_file.write(t)
            top_out_file.write(",")
            top_out_file.write(cpu)
            top_out_file.write(",")
            top_out_file.write(mem)
            top_out_file.write(",")

            if "celestial.bin" in command[0]:
                top_out_file.write("celestial,\n")
                continue
            elif "firecracker" in command[0]:
                top_out_file.write("microVM,")

                name = command[2].split("-")[2:-1]
                top_out_file.write("-".join(name))
                top_out_file.write("\n")
                continue
            else:
                top_out_file.write("other,\n")

            #print(t, cpu, mem, command)