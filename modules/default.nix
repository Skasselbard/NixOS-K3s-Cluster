{ config, lib, ... }: {
  options = with lib;
    with types; {
      nixos_version = mkOption {
        type = str;
      };
      k3s = {
        version = mkOption {
          type = str;
        };
        init = {
          ip = mkOption {
            type = nullOr str;
            default = null;
          };
        };
        server = {
          name = mkOption {
            type = nullOr str;
            default = null;
          };
          ip = mkOption {
            type = nullOr str;
            default = null;
          };
          manifests = mkOption {
            type = listOf path;
            default = [];
          };
          extraConfig = mkOption {
            type = nullOr path;
            default = null;
          };
        };
        agent = {
          name = mkOption {
            type = nullOr str;
            default = null;
          };
          ip = mkOption {
            type = nullOr str;
            default = null;
          };
        };
      };
    };
    imports = [
      ./admin.nix
      ./network.nix
      ./ssh.nix
    ];
}
