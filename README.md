# Nixos K3s Cluster

Build and deploy a [NixOs](https://nixos.org/) [K3s](https://k3s.io/) cluster according to a set of plans.
TODO: link NixOS and other stuff

This project builds and deploys a set of NixOS hosts and runs a [Kubernetes](https://kubernetes.io/) cluster in containers.
Its goal is to set up the hardware for a bare metal home cloud with a maximal level of automation.
The configuration is a set of csv tables which also document your deployments.

## Goals

1. Provide a minimal configuration for a K3s cluster on NixOS
2. Configure a local static network and ssh access (with ssh keys)
3. Leave room for additional NixOS host configuration including non K3s nodes
4. Create installation media for an initial machine setup
5. Deploy updates and change configuration remotely once the machines are initialized
6. Keep the human interaction minimal in the process

## Non Goals

- Configure Kubernetes and Container Apps
- Configure non-essential network like additional firewall rules
  - these can be added in the custom nix configs for the hosts
- Cluster Access from the internet
  - you should be able to extend the NixOS config for that purpose though
- Automatic updates
  - you decide when the cluster is ready for an update

## Assumptions

There are some assumptions that are embedded in the project.
Some keep the configuration minimal and structured.
Others reflect personal taste.

The following assumptions may be of interest:

- K3s runs in containers on one or more host machines
- The K3s server is running in a [nixos-container](https://nixos.wiki/wiki/NixOS_Containers) (because it is an easy NixOS integration)
- The K3s agent runs in a podman container (because it needs to be privileged access, which I couldn't figure out for the nixos-containers)
- Every host and K3s container has a static IP address
- Each host can run at most one K3s server and/or agent
  - hosts can be defined without K3s containers for additional deployments
- The network is configured as macvlan
  - including the host configuration
  - the host and the K3s containers share the same interface
- Containers are in the same subnet with the same gateway as the host
  - which of course should be reachable from the deploying machine
- The nix configuration is built on the deploying machine
  - the auto generated files use paths that are only valid on the generating machine
- Each host has an admin user
  - The NixOS on the nested K3s server container (if it exists) has the same admin user
- Hosts are accessible by ssh
  - ssh connections prohibit passwords and root logins (only ssh keys are allowed)
  - the admin user has a password for sudo once an ssh connection is established
- Kubernetes versions are shared
  - All K3s-servers run the same NixOs version
  - All K3s-agents run the same Kubernetes image
- The data on the installation medium is disposable and can be overwritten
- ? there is a `hardware-configuration.nix` in `/etc/nixos/` whenn applying the hive configuration.?
- The iso for the generated installation medium comes with an installation script.
  If a disk serial number is given the script partitions a drive with the given serial resulting in a partition labeled "nixos".
  With our without running the partitioning script, the installation script will then configure nixos to use a root (and boot) partition (according to the mbr/efi setting) for the initial installation.


No data folders are mounted for the containers.
Deleting the Container deletes all Kubernetes data on the host.

## Requirements

- Internet access
- Physical access to the NixOS hosts
  - or a ready to use NixOS on the host to deploy to
- installation medium aka USB drive

## Setup

For setup, you need to create the expected folder structure and a token:

```shell
nix-shell --run "setup [path]"
```

The token is needed to authenticate and securely connect the different kubernetes participants.

The folder structure is expected by the setup scripts.
As shown in the [examples](./examples/) folder this structure is composed of four subfolders:

1. The **plans** folder contains the main infrastructure configuration.
   There are three files expected in this folder:
   1. the **hosts.csv** contains information about the physical machines,
   2. the **k3s.csv** contains information about for the k3s container configuration and
   3. the **network.yaml** contains global network configuration nedded for hosts and k3s containers.
2. The **nixConfigs** folder contains additional nix configuration you need.
3. The **secrets** folder contains passwords and ssh keys needed for configuration.
   The token file will be stored here.
4. The **manifests** folder contains kubernetes configuration files that will be statically [deployed by k3s](https://docs.k3s.io/installation/packaged-components)

You may want to back up your plans for example in a git repo.

## Workflow

What I do:

Try:

1. Write plans for the cluster (csv files).
2. Configure Hosts with nix extra configuration.
3. Build a boot stick and install the system for every host
4. update k3s manifests (including a git ops service)
5. deploy cluster configuration
6. Jump to 4.

Catch (hardware problem):

7. Jump to 1.

- the boot stick from 3. contains the system configuration with a setup script
- the setup script is run on startup as systemd ``system_setup.service``
- part of the setup is partitioning the disk if a disk serial was configured

## Configuration

- Physikal machine and network configuration -> in the hosts.csv
- k3s container and network configuration -> k3s.csv
- additional nix config in `NixConfigs` subfolder
  - the config is selected by name e.g. host/container "olaf" -> olaf.nix
- There are X kinds of secrets
  - passwd
    - secrets/passwd is used for all hosts with no {hostname}passwd file
    - secrets/{hostname}passwd is used for {hostname} and takes precedence over passwd file
  - init-token
    - is generated during the build process and stored in the secrets folder
    - used to connect nodes to the initial k3s server
  - ssh keys
    - end on .pub
    - TODO moa ssh
- TODO: work out versions
- TODO: work out network.yaml / global config
- TODO: additional keys in the csv files will be added to the nix configuration
  - host keys go to cluster.${hostname}.${keyName}
  - k3s keys go to cluster.${hostname}.k3s.server
    - agents are podman containers and cannot be modified by nix
  - they need to be a defined option in a nixConfig for all hosts
- Manifests will be deployed to all servers
  - it is not advised to manually edit the manifests, because conflicts may arise
  - k3s does not resolve conflicting manifest files on multiple servers

- :bulb: all values are stripped of whitespace and normalize to lowercase letters (=> not case sensitive)
- you can extend the plans to your liking if you like to store additional data as long as the needed keys are present
- it should be possible to extend (k3s) config of the k3s server with a config file
- for k3s versions: take a tag from here https://hub.docker.com/r/rancher/k3s/tags #FIXME: Version is not used for server container

### Example
Check the [examples](/exampls/plans) folder.

#### Hosts.csv Physical hosts
name| interface| ip| admin
|-|-|-|-|
olaf| enp0s20f0| 10.0.100.2| manfred
ulf| enp1s0| 10.0.100.3| manfred
rolf| eno2| 10.0.100.4| manfred
karl| eni1| 10.0.100.5| manfred
ulrich| eno1| 10.0.100.6| manfred

#### k3s.csv K3s Containers
host| name| type| ip
|-|-|-|-|
olaf| olaf-k3s-server| init-server| 10.0.100.10
olaf| olaf-k3s-agent| agent| 10.0.100.11
ulf| ulf-k3s-server| server| 10.0.100.12
ulf| ulf-k3s-agent| agent| 10.0.100.13
rolf| rolf-k3s-server| server| 10.0.100.14
karl| karl-k3s-agent| agent| 10.0.100.15

## Known Issues

### Nixos-Install bug in (my) vms and maybe on some other systems

The automatic setup script fails softly installing grub on my test vms. This seems to happen because of an [issue finding mount and umount](https://github.com/NixOS/nixpkgs/pull/227696). Hopefully this problem disappears with newer versions.
The VM is still bootable though.

### Workaround for DNS issues

The default nameserver configuration does not work (on my test system).
With default settings the nixos binary cache cannot be resolved resulting updates to fail.
As a workaround I added googles nameserver (8.8.8.8) to the configuration as default.
If you like to use your own server, add the `config.nameservers = [ $ip1 $ip2 ... ]` key to your nixos config.

## Build Boot Stick for Host

```shell
nix-shell --run "create_boot_stick hostname /dev/usb/device"
```

## Build Cluster

```shell
nix-shell --run "build"
```

Populates the templates according to the plans and runs colmena build.
Keeps the populated plans.

## Deploy Cluster

```shell
nix-shell --run "deploy"
```

Populates the templates according to the plans and runs colmena deploy.
Deletes the populated plans after completion.
