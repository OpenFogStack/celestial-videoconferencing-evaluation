#!/usr/bin/env python3

"""
Common code for all measurement types:
the program main() function, and argument parsing.
"""

import argparse
import random
import typing

from onewaymeasurement import OneWayMeasurement

SERVER_RECV_BUFFER_SIZE = 2048


def start(Measurement: typing.Type[OneWayMeasurement]) -> None:
    """
    Process arguments and run the appropriate functions depending on whether
    we're in server mode or client mode.
    """

    args = parse_args(Measurement.description)

    if args.payload_len > SERVER_RECV_BUFFER_SIZE:
        print(
            "Warning: payload_len (%d) is greater than "
            "SERVER_RECV_BUFFER_SIZE (%d)" % (args.payload_len, SERVER_RECV_BUFFER_SIZE)
        )

    tester = Measurement(args.output_filename)
    if args.server:
        tester.run_server(
            args.n_packets, args.listen_port, SERVER_RECV_BUFFER_SIZE, args.timeout
        )
    elif args.client:
        tester.run_client(
            args.id,
            args.listen_port,
            args.http_port,
            args.n_packets,
            args.workload_file,
        )


def parse_args(description: str) -> argparse.Namespace:
    """
    Parse arguments.
    """

    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--server", action="store_true")
    group.add_argument("--client", action="store_true")
    parser.add_argument("--n_packets", type=int, default=700000)
    parser.add_argument("--payload_len", type=int, default=1227)
    parser.add_argument("--send_rate_kBps", type=int, default=1400)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--id", type=int, default=random.randint(0, 100))
    parser.add_argument("--output_filename", default="udp_packetn_latency_pairs")
    parser.add_argument("--listen_port", type=int, default=8888)
    parser.add_argument("--http_port", type=int, default=8000)
    parser.add_argument("--workload_file", type=str, default="./workload.csv")
    args = parser.parse_args()
    return args


start(OneWayMeasurement)
