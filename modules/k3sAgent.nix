{ pkgs, config, ... }:
with config.cluster;
let
  subnet = "";
  k3sVersionTag = "";
  tokenFilePath = "/var/lib/rancher/k3s/server/token";
in with config.cluster;{
  # delay worker service until k3s token is initialized
  systemd.services."podman-${k3s.agent.name}" = {
    # create macvlan for worker node if absent
    preStart =
      "${pkgs.podman}/bin/podman network exists ${k3s.agent.name}-macvlan ||  ${pkgs.podman}/bin/podman network create --driver=macvlan --gateway=${gateway} --subnet=${subnet}/${builtins.toString netmask} -o parent=${interface} ${k3s.agent.name}-macvlan";
      # FIXME: querry the init server host! for the token file
    unitConfig = {
      ConditionPathExists = tokenFilePath;
    };
  };

  # start the k3s agent in a privileged podman container
  # https://fictionbecomesfact.com/nixos-configuration
  virtualisation.oci-containers = {
    backend = "podman";
    containers."${k3s.agent.name}" = {
      image = "rancher/k3s:${k3sVersionTag}";
      cmd = [
        "agent"
        "--token-file=${tokenFilePath}"
        "--server=https://${k3s.init.ip}:6443"
        "--node-external-ip=${k3s.agent.ip}"
      ];
      extraOptions = [
        "--privileged"
        "--hostname=${k3s.agent.name}"
        "--network=${k3s.agent.name}-macvlan"
        "--ip=${k3s.agent.ip}"
        # "--mac-address=MAC"
      ];
      volumes = [
        "${tokenFilePath}:/${tokenFilePath}"
      ];
    };
  };
}
