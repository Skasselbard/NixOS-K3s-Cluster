#!/bin/python3
import subprocess
from jinja2 import Template
import pathlib
import os
import argparse
import shutil
import sys
sys.path.insert(0, '../plans')

py_script_path = os.path.abspath(os.path.dirname(__file__))


def build_pipeline(args):

    os.chdir(py_script_path)
    # parse target machine (including test vm)
    machine_name = args.name
    # create temp folder
    temp_dir = py_script_path + "/temp"
    pathlib.Path(temp_dir).mkdir(exist_ok=True)
    # configure install iso config.nix
    populate_template(
        "./templates/iso_config.nix.j2",
        temp_dir + "/iso_config.nix",
        getIsoConfigData(machine_name, temp_dir)
    )
    # configure hdd serial
    populate_template(
        "./templates/setup.sh.j2",
        temp_dir + "/setup.sh",
        getSetupScriptData(machine_name)
    )
    # copy machine config.nix
    copy_nix_config(machine_name, temp_dir)
    # build iso
    os.system(
        "nix-shell -p nixos-generators --run 'nixos-generate --format iso --configuration ./temp/iso_config.nix -o nixos'")
    # create stick if applicable (not a test vm)
    if machine_name != "test" and args.device:
        os.system("create_boot_stick {args.device}")
    # cleanup
    shutil.rmtree(temp_dir)
    return 0


def copy_nix_config(machine_name, temp_dir):
    config_path = py_script_path + f"/../hive/{machine_name}.nix"
    shutil.copyfile(config_path, temp_dir + "/configuration.nix")


def populate_template(template_file, target_file: str, config_vars):
    with open(template_file, "r") as nix_template:
        with open(target_file, "w") as nix_config:
            nix_config.write(
                Template(nix_template.read()).render(config_vars))


def getSetupScriptData(machine_name):
    import query
    if query.is_vm(machine_name):
        boot_mnt_comment = "#"
    else:
        boot_mnt_comment = ""
    return {
        "serial": query.get_boot_drive(machine_name),
        "boot_mnt_comment": boot_mnt_comment,
    }


def getIsoConfigData(machine_name, target_path):
    import query
    if query.is_vm(machine_name):
        partition_script = py_script_path+"/partition_virtual.sh"
    else:
        partition_script = py_script_path+"/partition_physical.sh"
    return {
        "ip": query.get_ip(machine_name),
        "interface": query.get_interface(machine_name),
        "nix_config_path": target_path + "/configuration.nix",
        "partition_script": partition_script
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="build a bootable stick for a nixos installation based on a config")
    parser.add_argument('-n', '--name', help="Name of the machine to prepare")
    parser.add_argument(
        '-d', '--device', help="The output device where the created image should be copied to")
    build_pipeline(parser.parse_args())
