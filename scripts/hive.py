import sys
import yaml
import os
import subprocess
import re
from jinja2 import Template


def get_hive_nix(config: dict):
    commit_sha1 = get_nixos_commit_sha(config)
    nix_config = f'# This is an auto generated file.\n{{\nmeta.nixpkgs = import (\n\
    builtins.fetchTarball "https://github.com/NixOS/nixpkgs/archive/{commit_sha1}.tar.gz"\n){{}};\n'
    for host_name, host_config in config["cluster"]["hosts"].items():
        get_hardware_configuration(host_name, host_config)
        nix_config += (
            f"{host_name} = "
            + populate_host(host_name, host_config, config["cluster"], is_hive=True)
            + ";\n"
        )
    nix_config += "}"
    return nix_config


def get_nixos_commit_sha(config):
    # nix channel regexes as listed here https://channels.nixos.org/
    # They except more combinations than possible (or useful), but are close enough
    nix_type = "(nixos|nixpkgs)"
    version = "(unstable|\d\d\.\d\d)"
    suffix = "(small|aarch64|darwin)"
    sha = re.compile("^[a-f0-9]{40}$")
    channel = re.compile(f"{nix_type}-{version}(-{suffix})?")

    nixos_version = str(config["cluster"]["versions"]["nixos"]).lower()
    if sha.fullmatch(nixos_version):
        return nixos_version
    if channel.fullmatch(nixos_version):
        return subprocess.run(
            f"git ls-remote https://github.com/nixos/nixpkgs {nixos_version}".split(),
            capture_output=True,
            text=True,
        ).stdout.split()[0]
    print("Error: Cannot parse nixos version.", file=sys.stderr)
    exit(1)


def get_hardware_configuration(hostname, host_config):
    if (
        os.system(
            f'scp {host_config["admin"]["name"]}@{host_config["ip"]}:/etc/nixos/hardware-configuration.nix $PWD/generated/{hostname}'
        )
        != 0
    ):
        print(
            f"Warning: cannot receive hardware configuration for host {hostname}",
            file=sys.stderr,
        )


def populate_host(host_name, host_config, cluster_config, is_hive=None):
    host_vars = {
        "hostname": host_name,
        "host": host_config,
        "cluster": cluster_config,
        # "token": cluster_config["token"],
        "is_hive_setup": is_hive,
    }
    # load template and render templating variables
    with open(
        os.path.abspath(os.path.dirname(__file__)) + "/templates/host.nix.j2"
    ) as hostTemplate:
        return Template(hostTemplate.read()).render(host_vars)


if __name__ == "__main__":
    # read yaml config from stdin
    input = ""
    for line in sys.stdin:
        input += line
    print(get_hive_nix(yaml.safe_load(input)))
