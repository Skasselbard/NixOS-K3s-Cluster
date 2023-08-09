{ pkgs, config, lib, ... }:
with config;
with lib; 
with builtins;
let 
  tokenFilePath = "/var/lib/rancher/k3s/server/token";
in {
  # delay the etcd container until the network is set up
  # Sometimes the network service crashes. Restarting the network service in the container (from the host with nixos-container) fixes this issue
  systemd.services = {
    "container@${k3s.server.name}" = { after = [ "network-setup.service" ]; };
  };

  # TODO: fix nix version for k3s
  containers = {
    "${k3s.server.name}" = let
      pkgs = import (fetchGit {
        url = "https://github.com/NixOS/nixpkgs";
        ref = "refs/heads/nixos-23.05";
      }) { };
    in {
      config = { pkgs, ... }: {
        imports = [ ]
          ++ optional (k3s.server.extraConfig != null) k3s.server.extraConfig;
        config = {
          # nixpkgs.pkgs = (import (fetchGit {
          # url = "https://github.com/NixOS/nixpkgs";
          # ref = "refs/heads/nixos-23.05";
          # }) { }).pkgs;
          systemd.services.k3s = {
            requires = [ "network-setup.service" ];
            after = [ "network-setup.service" ];
          };
          # ports: https://docs.k3s.io/installation/requirements
          networking.firewall.allowedTCPPorts = [ 6443 2379 2380 ];
          services.k3s = {
            enable = true;
            # k3s -- version
            # package = "k3s-${k3s.version}"; #https://github.com/NixOS/nixpkgs/tree/nixos-23.05/pkgs/applications/networking/cluster/k3s
            role = "server";
            disableAgent = true;
            clusterInit = mkIf (k3s.init.ip == k3s.server.ip) true;
            serverAddr = mkIf (k3s.init.ip != k3s.server.ip) k3s.init.ip;
            extraFlags = "--node-ip ${k3s.server.ip}";
          };
          environment.systemPackages = [ pkgs.k3s ];
          security.sudo.extraConfig = ''
            ${admin.name} ALL = NOPASSWD: ${pkgs.k3s}/bin/k3s
          '';
        };
      };
      macvlans = [ interface ];
      autoStart = true;
      # TODO: logs https://docs.k3s.io/faq#where-are-the-k3s-logs
      bindMounts = {
        "${tokenFilePath}".hostPath = tokenFilePath; 
      #   "/var/lib/rancher/k3s/server/manifests/dashboard.yaml".hostPath =
      #     "${../../Stage_3/dashboard.yaml}";
      #   "/var/lib/rancher/k3s/server/manifests/argocd.yaml".hostPath =
      #     "${../../Stage_3/argocd.yaml}";
      } //
      listToAttrs (map (elem: {
          name = baseNameOf elem;
          value = {
            mountPoint = "/var/lib/rancher/k3s/server/manifests" + baseNameOf elem;
            hostPath = "${/. + elem}";
          };
        }) k3s.server.manifests);
    };
  };
}
