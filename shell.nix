{ pkgs ? import (import ./nixpkgs.nix) { } }:
let
  # Stage_0
  #####################
  # create_image = pkgs.writeShellScriptBin "create_image" ''
  #   nixos-generate --format iso --configuration ./Stage_0/iso_config.nix -o nixos # --show-trace
  # '';
  # create_boot_stick = pkgs.writeShellScriptBin "create_boot_stick"
  #   (builtins.readFile ./Stage_0/create_boot_stick.sh);

  # Stage 1
  #######################
  create-token = pkgs.writeShellScriptBin "create-token" ''
    secrets=./secrets
    if [ "$#" -gt 0 ]; then
      secrets=$1/secrets
    fi
    mkdir -p $secrets
    ${pkgs.k3s}/bin/k3s token create > $secrets/init-token
  '';
  configure = pkgs.writeShellScriptBin "configure" ''
    path=$PWD
    if [ "$#" -gt 0 ]; then
      path=$1
    fi
    create-token $path
    python3 scripts/configuration.py $path | python3 scripts/hive_nix_setup.py ./$path/nixConfigs > hive.nix
    '';
  build = pkgs.writeShellScriptBin "build" ''
    export NIX_CONFIG="tarball-ttl = 0"
    path=$PWD
    if [ "$#" -gt 0 ]; then
      path=$1
    fi
    configure $path
    colmena build -f hive.nix
  '';
  deploy = pkgs.writeShellScriptBin "deploy" ''
    export NIX_CONFIG="tarball-ttl = 0"
    path=$PWD
    if [ "$#" -gt 0 ]; then
      path=$1
    fi
    configure $path
    colmena apply -f hive.nix
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
  ];
}
