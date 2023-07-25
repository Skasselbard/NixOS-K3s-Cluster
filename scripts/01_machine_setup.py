#!/bin/python3
import subprocess
from jinja2 import Template
import os
import argparse
import sys
import yaml
from utils import populate_host


def build_host(args, config):
    host_name = args.name
    return populate_host(
        host_name, config["cluster"]["hosts"][host_name], config["cluster"]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a nixos configuration file based on a configuration yaml. The yaml is expected as stdin and the config is printed on stdout."
    )
    parser.add_argument(
        "-n", "--name", required=True, help="Name of the machine to prepare"
    )
    # read yaml config from stdin
    input = ""
    for line in sys.stdin:
        input += line
    print(build_host(parser.parse_args(), yaml.safe_load(input)))
