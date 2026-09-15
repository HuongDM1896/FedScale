#!/usr/bin/env python3
import subprocess
import argparse


def read_hostfile(path: str) -> list:
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def cleanup_fedscale(hosts: list):
    """Kill all FedScale processes (aggregator + executor)."""
    print("\n[Cleanup] Killing all FedScale processes on all nodes...")

    # pattern match any python command that contains the word 'fedscale'
    pattern = "python.*fedscale"

    for node in hosts:
        ssh_kill = f"ssh -T {node} \"pkill -f '{pattern}' >/dev/null 2>&1 || true\""
        subprocess.run(ssh_kill, shell=True)

    print("[Cleanup] Done.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup FedScale processes")
    parser.add_argument("-f", "--hostfile", type=str, default="hostfile")
    args = parser.parse_args()

    hosts = read_hostfile(args.hostfile)
    cleanup_fedscale(hosts)
