#!/bin/python3
from jinja2 import Template
import os
import argparse
import sys
import yaml
import re
from pathlib import Path

py_script_path = os.path.abspath(os.path.dirname(__file__))


def build_host(args, config):
    host_name = args.name
    host_config = config["cluster"]["hosts"][host_name]
    cluster_config = config["cluster"]

    # render setup scripts
    setup_script = render_file(
        py_script_path + "/templates/setup.sh.j2",
        {
            "serial": args.serial,
            "legacy": args.legacy_boot,
            "nixos_version": cluster_config["versions"]["nixos"],
        },
    )
    partition_script = render_file(
        py_script_path + "/templates/partition.sh.j2", {"legacy": args.legacy_boot}
    )

    machine_vars = {
        "hostname": host_name,
        "host": host_config,
        "cluster": cluster_config,
        "partition_script": partition_script,
        "setup_script": setup_script,
        "legacy": args.legacy_boot,
    }
    # load template and render templating variables
    iso_config_nix = render_file(
        py_script_path + "/templates/iso_config.nix.j2", machine_vars
    )
    # generate the iso configuration
    Path(f"generated/{host_name}").mkdir(
        parents=True, exist_ok=True
    )
    with open(f"generated/{host_name}/{host_name}_iso.nix", "w") as nix_config:
        nix_config.write("# This is an autogenerated file\n")
        nix_config.write(iso_config_nix)

    if not args.dry:
        if (
            os.system(
                f"nix-shell -p nixos-generators --run 'nixos-generate --format iso --configuration generated/{host_name}/{host_name}_iso.nix -o generated/{host_name}/iso'"
            )
            == 0
        ):
            if args.device != None:
                # if the iso build was successful and should be copied to a device: start copying
                os.system(
                    f"sudo dd if=generated/{host_name}/iso/iso/nixos.iso of={args.device} bs=4M conv=fsync status=progress"
                )
            else:
                return
        else:
            exit(1)


def render_file(file, variables):
    with open(file) as template:
        rendered = Template(template.read()).render(variables)
        # remove template comments
        return re.sub(r"(?m)^ *#.*\n?", "", rendered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="build a nix iso configuration with the network config of the given machine. Expects a configuration in yaml as stdin and generates an is file in $PWD/generated/$hostname/$hostname.iso"
    )
    parser.add_argument(
        "-d",
        "--device",
        help="The output device where the created iso image should be copied to to make a bootable device.",
    )
    parser.add_argument(
        "-s",
        "--serial",
        help="The drive serial to search for partitioning. If omitted you can give a serial as parameter later",
    )
    parser.add_argument(
        "-n", "--name", required=True, help="Name of the machine to prepare"
    )
    parser.add_argument(
        "-l",
        "--legacy-boot",
        help="If this flag is set the partition script is written for MBR legacy boot (see nixos manual)",
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
    build_host(parser.parse_args(), yaml.safe_load(input))