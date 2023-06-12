from pathlib import Path
import sys

import yaml
from jinja2 import Template
import json


def get_hive_nix(config: dict, custom_modules: Path):
    nix_config = "# This is an auto generated file.\n{\n"
    for host, values in config["cluster"]["hosts"].items():
        server_module, agent_module, custom_module = "", "", ""
        if "server" in values["k3s"]:
            server_module = "      ./modules/k3sServer.nix\n"
        if "agent" in values["k3s"]:
            agent_module = "      ./modules/k3sAgent.nix\n"
        if host + ".nix" in [
            module.stem + module.suffix for module in custom_modules.iterdir()
        ]:
            custom_module = (
                "      ./"
                + str(custom_modules.absolute().relative_to(Path.cwd()) / host)
                + ".nix\n"
            )
        json_values = ""
        for line in str.splitlines(json.dumps(values, indent=2), keepends=True):
            line = "      " + line
            json_values += line
        host_vars = {
            "hostname": host,
            "k3sServer": server_module,
            "k3sAgent": agent_module,
            "customModule": custom_module,
            "ip": values["ip"],
            "hostConfig": json_values,
            "token": config["cluster"]["token"],
        }
        nix_config += populate_host(host_vars) + "\n"
    nix_config += "}"
    return nix_config


def populate_host(vars):
    hostTemplate = '\
  {{hostname}} = {\n\
    imports = [\n\
      ./modules/admin.nix\n\
      ./modules/network.nix\n\
      ./modules/ssh.nix\n\
      ./modules/k3s.nix\n\
{{k3sServer}}\
{{k3sAgent}}\
{{customModule}}\
      ];\n\
    deployment.targetHost = "{{ip}}";\n\
    deployment.keys."token" = {\n\
      text = "{{token}}";\n\
      destDir = "/var/lib/rancher/k3s/server";\n\
    };\
    cluster = {hostname = "{{hostname}}";}//\n\
        builtins.fromJSON(\'\'\n\
{{hostConfig}}\n\
    \'\');\n\
  };\n\
'
    return Template(hostTemplate).render(vars)


def main(yaml_str: str, custom_modules: Path = None):
    config = yaml.safe_load(yaml_str)
    if custom_modules == None:
        custom_modules = Path.cwd() / "nixConfigs"
    return get_hive_nix(config, custom_modules)


if __name__ == "__main__":
    # read yaml config from stdin
    input = ""
    path = None
    for line in sys.stdin:
        input += line
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    print(main(input, path))
