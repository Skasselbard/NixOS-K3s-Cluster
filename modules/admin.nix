{ lib, config, pkgs, ... }:

with lib;
with pkgs;
with builtins; {
  options = with types; {
    admin = {
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
    users.extraUsers = with config.admin; {
      root = {
        openssh.authorizedKeys.keys = sshKeys;
      };

      "${name}" = {
        isNormalUser = true;
        extraGroups = [ "wheel" ];
        hashedPassword = hashedPwd;
        # openssh.authorizedKeys.keys = map readFile sshKeys;
        openssh.authorizedKeys.keys = sshKeys;
      };
    };
  };
}
