{ lib, config, pkgs, ... }:

with lib;
with pkgs; {
  options = with types; {
    cluster.admin = {
      name = mkOption {
        type = str;
        default = "admin";
      };
      ## mkpasswd -m sha-512
      hashedPwd = mkOption {
        type = nullOr str;
        default = null;
      };
      sshKeys = mkOption {
        type = listOf str;
        default = [ ];
      };
    };
  };
  config = {
    users.extraUsers = with config.cluster.admin; {
      "${name}" = {
        isNormalUser = true;
        extraGroups = [ "wheel" ];
        hashedPassword = hashedPwd;
        openssh.authorizedKeys.keys = sshKeys;
      };
    };
  };
}
