# { pkgs ? import (import ./nixpkgs.nix) { } }:
{pkgs ? import <nixpkgs> {}, ...}:
let

  setup = pkgs.writeShellScriptBin "setup" ''
    path=$PWD
    if [ "$#" -gt 0 ]; then
      path=$1
    fi
    ${pkgs.python3}/bin/python3 scripts/utils.py --setup --dir $path
  '';

  # create a token file for node authentication
  create-token = pkgs.writeShellScriptBin "create-token" ''
    secrets=./secrets
    if [ "$#" -gt 0 ]; then
      secrets=$1/secrets
    fi
    mkdir -p $secrets
    ${pkgs.k3s}/bin/k3s token create > $secrets/init-token
  '';

  # read configuration files and create hive.nix
  configure = pkgs.writeShellScriptBin "configure" ''
    path=$PWD
    if [ "$#" -gt 0 ]; then
      path=$1
    fi
    mkdir -p $path/generated
    create-token $path
    python3 scripts/configuration.py $path | python3 scripts/hive_setup.py $path/nixConfigs > generated/hive.nix
    '';

  # build the previously generated hive.nix with colmena
  build = pkgs.writeShellScriptBin "build" ''
    export NIX_CONFIG="tarball-ttl = 0"
    path=$PWD
    if [ "$#" -gt 0 ]; then
      path=$1
    fi
    configure $path
    colmena build -f $path/generated/hive.nix
  '';

  # create an iso file for the machine with name $1
  create_image = pkgs.writeShellScriptBin "create_image" ''
    path=$PWD
    if [ "$#" -gt 1 ]; then
      path=$2
    fi
    nixos-generate --format iso --configuration ./Stage_0/iso_config.nix -o nixos # --show-trace
  '';

  create_boot_stick = pkgs.writeShellScriptBin "create_boot_stick"
    (builtins.readFile ./Stage_0/create_boot_stick.sh);

  # deploy the previously generated hive.nix to the configured IPs with colmena
  deploy = pkgs.writeShellScriptBin "deploy" ''
    export NIX_CONFIG="tarball-ttl = 0"
    path=$PWD
    if [ "$#" -gt 0 ]; then
      path=$1
    fi
    configure $path
    colmena apply -f $path/generated/hive.nix
  '';

in pkgs.mkShell {
  buildInputs = with pkgs; [
    # software
    colmena
    k3s
    #nixos-generators
    # scripts
    configure
    # create_image
    # create_boot_stick
    create-token
    build
    deploy
    setup
  ];
}
