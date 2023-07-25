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
    # parse the hostname from the input nix
    host_name = re.search('hostname = "(.*)";', host_nix).group(1)
    with open(f"generated/{host_name}.nix", "w") as nix_config:
        nix_config.write("# This is an autogenerated file\n")
        nix_config.write(host_nix)

    machine_vars = {
        "host_name": host_name,
    }
    # load template and render templating variables
    rendered = None
    with open(
        os.path.abspath(os.path.dirname(__file__)) + "/templates/iso_config.nix.j2"
    ) as hostTemplate:
        rendered = Template(hostTemplate.read()).render(machine_vars)

    # generate the iso configuration
    with open(f"generated/{host_name}_iso.nix", "w") as nix_config:
        nix_config.write("# This is an autogenerated file\n")
        nix_config.write(rendered)


def build_pipeline(args):
    os.chdir(py_script_path)
    temp_dir = py_script_path + "/temp"
    pathlib.Path(temp_dir).mkdir(exist_ok=True)
    # configure install iso config.nix
    populate_template(
        "./templates/iso_config.nix.j2",
        temp_dir + "/iso_config.nix",
        getIsoConfigData(machine_name, temp_dir),
    )
    # configure hdd serial
    populate_template(
        "./templates/setup.sh.j2",
        temp_dir + "/setup.sh",
        getSetupScriptData(machine_name),
    )
    # copy machine config.nix
    copy_nix_config(machine_name, temp_dir)
    # build iso
    os.system(
        "nix-shell -p nixos-generators --run 'nixos-generate --format iso --configuration ./temp/iso_config.nix -o nixos'"
    )
    # create stick if applicable (not a test vm)
    if machine_name != "test" and args.device:
        os.system("create_boot_stick {args.device}")
    # cleanup
    shutil.rmtree(temp_dir)
    return 0


# def getSetupScriptData(machine_name):
#     import query
#     if query.is_vm(machine_name):
#         boot_mnt_comment = "#"
#     else:
#         boot_mnt_comment = ""
#     return {
#         "serial": query.get_boot_drive(machine_name),
#         "boot_mnt_comment": boot_mnt_comment,
#     }


# def getIsoConfigData(machine_name, target_path):
#     import query
#     if query.is_vm(machine_name):
#         partition_script = py_script_path+"/partition_virtual.sh"
#     else:
#         partition_script = py_script_path+"/partition_physical.sh"
#     return {
#         "ip": query.get_ip(machine_name),
#         "interface": query.get_interface(machine_name),
#         "nix_config_path": target_path + "/configuration.nix",
#         "partition_script": partition_script
#     }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="build a nix iso configuration as base for a machine or vm. Expects a nixos host file as stdin and prints iso configuration on stdout."
    )
    parser.add_argument(
        "-d",
        "--device",
        help="The output device where the created image should be copied to",
    )
    # read yaml config from stdin
    input = ""
    for line in sys.stdin:
        input += line
    # build_pipeline(parser.parse_args())
    build_host(parser.parse_args(), input)
