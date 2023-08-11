# ConfigurationOptions

A list of all options and expected values that can be configured in the plans.

## Hosts.csv

- **name**: `string`: hostname configured in the network config
- **interface**: `string`: [interface name](https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/) configured for cluster communication.  
  A [macvlan](https://developers.redhat.com/blog/2018/10/22/introduction-to-linux-interfaces-for-virtual-networking#macvlan) will be crated here for static interfaces.
- **ip**: `ipaddress[@ipaddress]`: ip address that the interface should be configured with.
  The first IP is configured as the actual network address (can be `dhcp` for automatic assignment).
  The optional second IP will be used by colmena as [deployment target](https://colmena.cli.rs/unstable/reference/deployment.html#deploymenttargethost) (can be `local` to deploy on the local machine). This is useful for DHCP hosts to give a hint where to connect to for deployment. If the second part is empty, the first IP will be used as deployment host.
- **admin**: `string`: name of the admin user configured for the machine.
  The admin will be configured with the corresponding password and ssh keys from the `sercets` folder

## K3s.csv

- **host**: `string`: a hostname configured in the [hosts.csv](ConfigurationOptions#hostscsv).
  This K3s definition will be deployed on there.
- **name**: `string`: hostname for this k3s container
- **type**: `init|server|agent`: The type of k3s container that should be created.
  - **init**: This K3s instance will boot a new cluster and does not connect to another server itself. `init` implies `server`.
  - **server**: A container for the control plane of the cluster as described in the [architecture](https://docs.k3s.io/architecture) for k3s. Runs etcd. Connects to the `init` server.
  - **agent**: A worker node that runs pods. Connects to the `init` server.
- **ip**: `ipaddress`: a static IP address used by the container. The configured interface is bridged with the host macvlan.

## Network.yaml

- **netmask**: e.g. `/24`: A [subnet mask](https://en.wikipedia.org/wiki/Subnet) in decimal bit length notation. Used to configure container networks.
- **gateway**: `ipaddress`: The standard gateway used to access the internet. An internet connection is necessary to download nixos packages.

## Versions.yaml

- **nixos**: branch, tag or commit hash in the [nixpkgs repository](https://github.com/NixOS/nixpkgs). These nixpkgs are used to build the installation iso and the files that get deployed to the remote hosts.
- **disko**: branch, tag or commit hash in the [disko repository](https://github.com/nix-community/disko/tree/master). Disko is used to partition the storage devices.
<!-- - **k3s**: v1.27.4-k3s1 -->
