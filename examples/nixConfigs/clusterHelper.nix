# setup macvlan (and other dependencies)
{ ... }:
let
  etcdName = config.cluster.k3s.server.name;
  workerName = config.cluster.k3s.agent.name;
  username = config.cluster.admin.name;
  etcdIP = config.cluster.k3s.server.ip;
in {
  # cluster helper scripts
  environment.systemPackages = [
    pkgs.yq-go
    # remove etcd rootfs and restart server + agent
    (pkgs.writeShellScriptBin "cluster-container-reset" ''
      # stop server service
      sudo systemctl stop container@${etcdName}.service 
      # remove server root fs
      sudo chattr -i /var/lib/nixos-containers/${etcdName}/var/empty
      sudo rm -r  /var/lib/nixos-containers/${etcdName}
      # restart server service
      sudo systemctl start container@${etcdName}.service 
      # delete podman agent and let it restart via systemd
      sudo podman rm -f ${workerName}
    '')
    # print the etcd generated kubeconfig with the etcd ip
    (pkgs.writeShellScriptBin "cluster-get-config" ''
      sudo cat /var/lib/nixos-containers/${etcdName}/etc/rancher/k3s/k3s.yaml |
        ${pkgs.yq-go}/bin/yq '.clusters[0].cluster.server = "https://${etcdIP}:6443"'
    '')
  ];
  # make the helper scripts passwordless with sudo
  security.sudo.extraConfig = ''
    # make kubeconfig accessible
    ${username} ALL = NOPASSWD: ${pkgs.coreutils-full}/bin/cat /var/lib/nixos-containers/${etcdName}/etc/rancher/k3s/k3s.yaml
  '';
}
