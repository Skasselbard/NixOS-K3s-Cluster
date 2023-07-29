#!/bin/python3
import subprocess
from jinja2 import Template
import pathlib
import os
import argparse
import shutil
import sys
import yaml
from utils import populate_host
import re

py_script_path = os.path.abspath(os.path.dirname(__file__))


def build_host(args, host_nix):
    # gather requirements from input and files
    host_name = re.search('hostname = "(.*)";', host_nix).group(1)
    nixos_version = re.search('nixos_version = "(.*)";', host_nix).group(1)
    token = (pathlib.Path.cwd() / "secrets/init-token").read_text()
    
    with open(f"generated/{host_name}.nix", "w") as nix_config:
        nix_config.write("# This is an autogenerated file\n")
        nix_config.write(host_nix)

    # render setup script
    setup_script = render_from_file(
        py_script_path + "/templates/setup.sh.j2",
        {
            "serial": args.serial,
            "is_vm": args.vm,
            "nixos_version": nixos_version,
            "token": token,
        },
    )
    partition_script = render_from_file(
        py_script_path + "/templates/partition.sh.j2", {"is_vm": args.vm}
    )

    machine_vars = {
        "host_name": host_name,
        "setup_script": setup_script,
        "partition_script": partition_script,
    }
    # load template and render templating variables
    iso_config_nix = render_from_file(
        py_script_path + "/templates/iso_config.nix.j2", machine_vars
    )
    # generate the iso configuration
    with open(f"generated/{host_name}_iso.nix", "w") as nix_config:
        nix_config.write("# This is an autogenerated file\n")
        nix_config.write(iso_config_nix)

    if not args.dry:
        os.system(
            f"nix-shell -p nixos-generators --run 'nixos-generate --format iso --configuration generated/{host_name}_iso.nix -o generated/{host_name}'"
        )


def render_from_file(file, variables):
    with open(file) as template:
        rendered = Template(template.read()).render(variables)
        # remove template comments
        return re.sub(r"(?m)^ *#.*\n?", "", rendered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="build a nix iso configuration as base for a machine or vm. Expects a nixos host file as stdin and prints iso configuration on stdout."
    )
    parser.add_argument(
        "-d",
        "--device",
        help="The output device where the created image should be copied to.",
    )
    parser.add_argument(
        "-s",
        "--serial",
        help="The drive serial to search for partitioning.",
    )
    parser.add_argument(
        "-vm",
        help="Is a virtual machine targeted? If the flag is present the setup script will be adapted for a virtual machine.",
        action="store_true",
    )
    parser.add_argument(
        "--dry",
        help="Make a dry run of the generation without generating an iso image",
        action="store_true",
    )
    # read yaml config from stdin
    input = ""
    for line in sys.stdin:
        input += line
    # build_pipeline(parser.parse_args())
    build_host(parser.parse_args(), input)