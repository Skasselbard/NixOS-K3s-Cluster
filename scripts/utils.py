from pathlib import Path
import argparse
import json
import os
import sys


def init_dir(root_path: Path):
    (root_path / "plans").mkdir(parents=True, exist_ok=True)
    (root_path / "nixConfigs").mkdir(parents=True, exist_ok=True)
    (root_path / "secrets").mkdir(parents=True, exist_ok=True)
    (root_path / "manifests").mkdir(parents=True, exist_ok=True)
    (root_path / "plans/hosts.csv").open("w").writelines(
        [
            "name, interface, ip, admin\n",
            "olaf, eno3, 192.168.100.5, admin\n",
            "rolf, enps1, 192.168.100.6, admin\n",
        ]
    )
    (root_path / "plans/k3s.csv").open("w").writelines(
        [
            "host, name, type, ip\n",
            "olaf, olaf-server, init, 192.168.100.10\n"
            "olaf, olaf-agent, agent, 192.168.100.11\n"
            "rolf, olaf-agent, server, 192.168.100.12\n",
        ]
    )
    (root_path / "plans/network.yaml").open("w").writelines(
        ['netmask: "24"\n', "gateway: 192.168.100.1\n"]
    )


def main():
    # default values
    path = Path.cwd()
    parser = argparse.ArgumentParser(
        description="Utility functions to build k3s cluster"
    )
    parser.add_argument(
        "--init",
        help="initialize paths and files in the expected location",
        action="store_true",
    )
    args = parser.parse_args()
    if args.setup:
        init_dir(path)
        exit(0)
    # end of parsing
    ##################################


if __name__ == "__main__":
    main()
