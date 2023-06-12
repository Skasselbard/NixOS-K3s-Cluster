{ config, lib, ... }: {
  options = with lib;
    with types; {
      cluster.k3s = {
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
            type = listOf str; # FIXME: should be paths but json does not support that
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
}
