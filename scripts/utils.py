from pathlib import Path
import argparse
import configuration
import hive_nix_setup


def setup_dir(plans, nix_configs):
    plans.mkdir(parents=True, exist_ok=True)
    nix_configs.mkdir(parents=True, exist_ok=True)


def main():
    # default values
    plans = Path.cwd() / "plans"
    nix_configs = Path.cwd() / "nixConfigs"
    parser = argparse.ArgumentParser(
        description="Utility functions to build k3s cluster")
    parser.add_argument(
        '--setup', help="Setup default paths and files in $CWD", action='store_true')
    parser.add_argument(
        '-p', '--plan-dir', help="Custom path to the plan csvs")
    parser.add_argument(
        '-n', '--nix-config-dir', help="Custom path to additional niy configs")
    args = parser.parse_args()
    if args.plan_dir:
        plans = Path(args.plan_dir)
    if args.nix_config_dir:
        plans = Path(args.nix_config_dir)
    if args.setup:
        setup_dir(plans, nix_configs)
        exit(0)
    # end of parsing
    ##################################
    print(hive_nix_setup.main(configuration.main(plans)))


if __name__ == "__main__":
    main()
