"""
Measure one-way packet latencies using a hardware timer (here implemented as a
counter) accessible from both the client and the server.
"""

from __future__ import division
import socket
import time
import pickle
import typing
import http.server
import cgi
import csv
import multiprocessing as mp
from multiprocessing.connection import Connection as MultiprocessingConnection
import threading as td

target_address_pipe_in, target_address_pipe_out = mp.Pipe()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,  # type: ignore
            environ={"REQUEST_METHOD": "POST"},
        )

        s = form.getvalue("server")

        target_address_pipe_in.send(s)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK\n")


class OneWayMeasurement:
    description = """Measure one-way UDP packet latency time.
On your server host, run:
    $ ./quack2.py --server
On your client host(s), run:
    $ ./quack2.py --client <IP address of server host>
quack.py on your server host will spit out one file containing
the latencies of each packet received from the client.
"""

    def __init__(self, test_output_filename: str):
        self.test_output_filename = test_output_filename
        self.target_address: typing.Optional[str] = None
        self.target_port: typing.Optional[int] = None

    def update_target(self, target_address_pipe: MultiprocessingConnection) -> None:
        while True:
            target_address = target_address_pipe.recv()
            if self.target_port is not None:
                print(
                    "Updating target address to %s:%d"
                    % (target_address, self.target_port)
                )
            if self.target_address != target_address:
                self.target_address = None

                if target_address != "none":
                    self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.sock_out.connect((target_address, self.target_port))
                    self.target_address = target_address

    def send_packets(self, id: int, n_packets: int) -> None:
        """
        Send n_packets packets, each with a payload of packet_len bytes, to
        target_address, trying to maintain a constant send rate of
        send_rate_kbytes_per_s.
        """

        # send_rate_bytes_per_s = send_rate_kbytes_per_s * 1000
        n_bytes = 0
        # packet_rate = send_rate_bytes_per_s / packet_len
        # packet_interval = 1 / packet_rate

        # print("Sending %d %d-byte packets at about %d kB/s..." %(n_packets, packet_len, send_rate_kbytes_per_s))

        print("Waiting for a target address...")

        while self.target_address is None:
            pass

        print("Got a target address...")

        send_start_seconds = time.time()
        # inter_packet_sleep_times_ms = []

        for packet_n in range(n_packets):
            while self.target_address == None:
                pass

            tx_start_seconds = time.time()

            payload = self.get_packet_payload(id, packet_n)
            packet_len = self.workload_bytes[packet_n % self.workload_length]
            n_fill_bytes = packet_len - len(payload)
            fill_char: bytes = bytes("a", "ascii") * n_fill_bytes
            payload = bytes(payload + fill_char)

            if self.target_address is not None:
                try:
                    self.sock_out.sendall(payload)
                except:
                    pass

            tx_end_seconds = time.time()
            n_bytes += packet_len

            # I don't know why, but this still doesn't yield exactly the desired
            # send rate. But eh, it's good enough.
            tx_time_seconds = tx_end_seconds - tx_start_seconds
            sleep_time_seconds = (
                self.workload_deltas[packet_n % self.workload_length] - tx_time_seconds
            )
            # inter_packet_sleep_times_ms.append("%.3f" % (sleep_time_seconds * 1000))
            if sleep_time_seconds > 0:
                time.sleep(sleep_time_seconds)
        send_end_seconds = time.time()

        print("Finished sending packets!")

        total_send_duration_seconds = send_end_seconds - send_start_seconds
        bytes_per_second = n_bytes / total_send_duration_seconds
        print(
            "(Actually sent packets at %d kB/s: %d bytes for %.1f seconds)"
            % (bytes_per_second / 1e3, n_bytes, total_send_duration_seconds)
        )

        self.sock_out.close()

    @staticmethod
    def save_packet_latencies(
        packetn_latency_tuples: typing.Tuple[
            typing.List[int],
            typing.List[int],
            typing.List[int],
            typing.List[float],
            typing.List[float],
            typing.List[float],
        ],
        n_packets_expected: int,
        output_filename: str,
    ) -> None:
        """
        Save latencies of received packets to a file, along with the total
        number of packets send in the first place.
        """
        with open(output_filename, "w") as out_file:
            # out_file.write("%d\n" % n_packets_expected)
            out_file.write("id,packet_n,packet_len,latency,send_time,recv_time\n")
            for i in range(len(packetn_latency_tuples[0])):
                id = packetn_latency_tuples[0][i]
                packet_n = packetn_latency_tuples[1][i]
                packet_len = packetn_latency_tuples[2][i]
                latency = packetn_latency_tuples[3][i]
                send_time = packetn_latency_tuples[4][i] * 1e9
                recv_time = packetn_latency_tuples[5][i] * 1e9
                out_file.write(
                    "%d,%d,%d,%.2f,%.0f,%.0f\n"
                    % (id, packet_n, packet_len, latency, send_time, recv_time)
                )

    def run_client(
        self,
        id: int,
        listen_port: int,
        http_port: int,
        n_packets: int,
        workload_file: str,
    ) -> None:
        total_packet_len = 0
        total_workload_duration = 0.0

        self.workload_bytes: typing.List[int] = []
        self.workload_deltas: typing.List[float] = []

        with open(workload_file) as workload_csv:
            workload_reader = csv.DictReader(workload_csv)
            for row in workload_reader:
                delta = float(row["delta"]) / 1e9
                length = int(row["length"])

                self.workload_bytes.append(length)
                self.workload_deltas.append(delta)

                total_packet_len += length
                total_workload_duration += delta

        assert len(self.workload_bytes) == len(self.workload_deltas)

        self.workload_length = len(self.workload_bytes)

        expected_duration = n_packets * (total_workload_duration / self.workload_length)

        print("Expected duration: %s seconds" % (expected_duration))

        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target_address = None
        self.target_port = listen_port

        httpd = http.server.HTTPServer(("0.0.0.0", http_port), Handler)

        h = td.Thread(target=httpd.serve_forever)
        h.start()

        print("Started HTTP server on :%d" % (http_port))

        controlThread = td.Thread(
            target=self.update_target, args=[target_address_pipe_out]
        )
        controlThread.start()

        print("Started control thread...")

        self.send_packets(id, n_packets)

        h.join(0.0)
        controlThread.join(0.0)
        exit(0)

    def get_packet_payload(self, id: int, packet_n: int) -> bytes:
        """
        Return a packet payload consisting of:
        - The packet number
        - The timestamp of the packet
        """

        send_time_seconds = time.time()
        payload = pickle.dumps((id, packet_n, send_time_seconds))
        return payload

    def run_server(
        self,
        n_packets_expected: int,
        server_listen_port: int,
        payload_len: int,
        timeout: int = 15,
    ) -> None:
        """
        Receive packets sent from the client. Calculate the latency for each
        packet by comparing the counter value from the packet (the counter value
        at time of transmission) to the current counter value.
        """
        sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock_in.bind(("0.0.0.0", server_listen_port))

        print("UDP server running...")

        sock_in.settimeout(timeout)

        # packets: typing.List[typing.Tuple[int, int, int, float, float, float]] = [(0, 0, 0, 0.0, 0.0, 0.0)] * n_packets_expected
        ids = [0] * n_packets_expected
        packet_ns = [0] * n_packets_expected
        packet_lens = [0] * n_packets_expected
        latency_mss = [0.0] * n_packets_expected
        send_times = [0.0] * n_packets_expected
        recv_times = [0.0] * n_packets_expected

        packet_c = 0

        a = bytes("a", "ascii")

        try:
            while packet_c < n_packets_expected:
                data = sock_in.recv(payload_len)
                recv_time = time.time()
                packet_lens[packet_c] = len(data)
                payload = data.rstrip(a)
                (ids[packet_c], packet_ns[packet_c], send_time) = pickle.loads(payload)
                latency_mss[packet_c] = (recv_time - send_time) * 1e3
                # packets[packet_c] = (id, packet_n, packet_len, latency_ms, send_time, recv_time)
                send_times[packet_c] = send_time
                recv_times[packet_c] = recv_time

                packet_c += 1

                # if packet_c % 2000 == 0:
                #    print("%d packets received so far" % packet_c)

        except socket.timeout:
            print("Note: timed out waiting to receive packets")
            print("So far, had received %d packets" % packet_c)
        except KeyboardInterrupt:
            print("Interrupted")

        sock_in.close()

        print("Received %d packets" % packet_c)

        self.save_packet_latencies(
            (
                ids[:packet_c],
                packet_ns[:packet_c],
                packet_lens[:packet_c],
                latency_mss[:packet_c],
                send_times[:packet_c],
                recv_times[:packet_c],
            ),
            n_packets_expected,
            self.test_output_filename,
        )
