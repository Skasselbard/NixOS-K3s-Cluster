from pathlib import Path
import argparse
import json
from jinja2 import Template
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


def populate_host(host_name, host_config, cluster_config, is_hive=None):
    custom_modules = Path.cwd() / "nixConfigs"
    if not custom_modules.exists():
        print(
            f'Error: nix configuration path "{custom_modules}"does not exists',
            file=sys.stderr,
        )
        exit(1)
    # set empty default module paths and include them based on the host configuration
    server_module, agent_module, custom_module = "", "", ""
    if "server" in host_config["k3s"]:
        server_module = "../modules/k3sServer.nix"
    if "agent" in host_config["k3s"]:
        agent_module = "../modules/k3sAgent.nix"
    if host_name + ".nix" in [
        module.stem + module.suffix for module in custom_modules.iterdir()
    ]:
        custom_module = str(custom_modules / host_name) + ".nix"
    # indent parsed json for readable output
    json_values = ""
    for line in str.splitlines(json.dumps(host_config, indent=2), keepends=True):
        line = "      " + line
        json_values += line
    # set the templating vars
    host_vars = {
        "hostname": host_name,
        "k3sServer": server_module,
        "k3sAgent": agent_module,
        "customModule": custom_module,
        "ip": host_config["ip"],
        "hostConfig": json_values,
        "token": cluster_config["token"],
        "is_hive_setup": is_hive,
    }
    # load template and render templating variables
    with open(
        os.path.abspath(os.path.dirname(__file__)) + "/templates/host.nix.j2"
    ) as hostTemplate:
        return Template(hostTemplate.read()).render(host_vars)


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
