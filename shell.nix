# { pkgs ? import (import ./nixpkgs.nix) { } }:
{pkgs ? import <nixpkgs> {}, ...}:
let

  # create a token file for node authentication
  create-token = pkgs.writeShellScriptBin "create-token" ''
    secrets=./secrets
    if [ "$#" -gt 0 ]; then
      secrets=$1/secrets
    fi
    mkdir -p $secrets
    ${pkgs.k3s}/bin/k3s token create > $secrets/init-token
  '';

  cluster = pkgs.writeShellScriptBin "k3s-cluster" ''
    ${pkgs.python3}/bin/python3 scripts/cluster.py ''${@:1}
  '';

in pkgs.mkShell {
  buildInputs = with pkgs; [
    colmena
    k3s
    python3
    nixos-generators
    git
    openssh
    coreutils
    # scripts
    cluster
  ];
  packages = let
    python-packages = ps: with ps; [
      jinja2
      pathlib2
      pyyaml
    ];
  in[
     (pkgs.python3.withPackages python-packages)
  ];
}
