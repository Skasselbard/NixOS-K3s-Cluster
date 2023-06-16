from pathlib import Path
import argparse
import configuration
import hive_nix_setup
import csv


def setup_dir(root_path: Path):
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
        "--setup", help="Setup default paths and files in $CWD", action="store_true"
    )
    parser.add_argument("-d", "--dir", help="Custom path to the configuratin files")
    args = parser.parse_args()
    if args.dir:
        path = Path(args.dir)
    if args.setup:
        setup_dir(path)
        exit(0)
    # end of parsing
    ##################################
    print(hive_nix_setup.main(configuration.main(path)))


if __name__ == "__main__":
    main()
