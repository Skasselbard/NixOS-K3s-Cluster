import sys
import yaml
import os
from jinja2 import Template


def get_hive_nix(config: dict):
    nix_config = "# This is an auto generated file.\n{\n"
    for host_name, host_config in config["cluster"]["hosts"].items():
        get_hardware_configuration(host_name, host_config)
        nix_config += (
            f"#TODO: meta.nixpkgs=version\n{host_name} = "
            + populate_host(host_name, host_config, config["cluster"], is_hive=True)
            + ";\n"
        )
    nix_config += "}"
    return nix_config

def get_hardware_configuration(hostname, host_config):
    if os.system(f'scp {host_config["admin"]["name"]}@{host_config["ip"]}:/etc/nixos/hardware-configuration.nix $PWD/generated/{hostname}') != 0:
        print(f"Warning: cannot receive hardware configuration for host {hostname}", file=sys.stderr)


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
