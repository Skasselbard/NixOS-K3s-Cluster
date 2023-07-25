import sys
import yaml
from utils import populate_host


def get_hive_nix(config: dict):
    nix_config = "# This is an auto generated file.\n{\n"
    for host_name, host_config in config["cluster"]["hosts"].items():
        nix_config += (
            f"{host_name} = "
            + populate_host(host_name, host_config, config["cluster"], is_hive=True)
            + ";\n"
        )
    nix_config += "}"
    return nix_config


if __name__ == "__main__":
    # read yaml config from stdin
    input = ""
    for line in sys.stdin:
        input += line
    print(get_hive_nix(yaml.safe_load(input)))
