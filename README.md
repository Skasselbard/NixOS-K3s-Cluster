# Nixos K3s Cluster

Build and deploy a [NixOs](https://nixos.org/) [K3s](https://k3s.io/) cluster according to a set of plans.

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

- You running a linux system (with nix installed) for deployment.
- K3s runs in containers on one or more host machines
- The K3s server is running in a [nixos-container](https://nixos.wiki/wiki/NixOS_Containers) (because it is an easy NixOS integration)
- The K3s agent runs in a podman container (because it needs to have privileged access, which I couldn't figure out for the nixos-containers)
- Each host can run at most one K3s server and/or agent
  - hosts can be defined without K3s containers for additional deployments
- Every K3s host and K3s container has a static IP address
  - non K3s hosts can be dynamic
- The network of K3s hosts is configured as macvlan
  - the host and the K3s containers share the same interface
- Containers are in the same subnet with the same gateway as the host
  - which of course should be reachable from the deploying machine
- The nix configuration is built on the deploying machine
- Each host has an admin user
  - The NixOS on the nested K3s server container (if it exists) has the same admin user
- Hosts are accessible by ssh
  - ssh connections prohibit passwords and root logins (only ssh keys are allowed)
  - the admin user has a password for sudo once an ssh connection is established
- Kubernetes versions are shared
  - All K3s-servers run the same NixOs version
  - All K3s-agents run the same Kubernetes image
- The data on the installation medium is disposable and can be overwritten

TODO:
? No data folders are mounted for the containers.?
? Deleting the Container deletes all Kubernetes data on the host.?

## Configuration

- :bulb: all values are stripped of whitespace and normalize to lowercase letters (=> not case sensitive)

- for k3s versions: take a tag from here https://hub.docker.com/r/rancher/k3s/tags #FIXME: Version is not used for server container

- ip can have a distinct deployment target: ip@deployment_target
- ip can be dynamic with "dhcp", or "auto"
  - dynamic ips need deployment target (manually extracted)

- disk with `/` is expected to be formatted during installation
### Example
Check the [examples](/exampls/plans) folder.
And the [[HowTo]] Guide.

#### Download the scripts and set up the configuration

```shell
curl -sSf https://raw.githubusercontent.com/Skasselbard/NixOS-K3s-Cluster/main/install.sh | sh
```

#### Write your configuration

##### Hosts.csv Physical hosts
name| interface| ip| admin
|-|-|-|-|
olaf| enp0s20f0| 10.0.100.2| manfred
ulf| enp1s0| 10.0.100.3| manfred
rolf| eno2| 10.0.100.4| manfred
karl| eni1| 10.0.100.5| manfred
ulrich| eno1| 10.0.100.6| manfred

##### k3s.csv K3s Containers
host| name| type| ip
|-|-|-|-|
olaf| olaf-k3s-server| init-server| 10.0.100.10
olaf| olaf-k3s-agent| agent| 10.0.100.11
ulf| ulf-k3s-server| server| 10.0.100.12
ulf| ulf-k3s-agent| agent| 10.0.100.13
rolf| rolf-k3s-server| server| 10.0.100.14
karl| karl-k3s-agent| agent| 10.0.100.15

#### Prepare an installation medium

```shell
./k3s-cluster install -n testvm -d /dev/USBdevice
```

#### Boot from the installation medium and run the setup a base system with your user and IP congifuration

On the machine:
```shell
setup
```

#### Deploy your complete configuration

```shell
./k3s-cluster hive deploy [colmena-args]
```

## Known Issues

### Root disk is always formatted on installation / Non root disks are not formatted

I use [disko](https://github.com/nix-community/disko) for formatting.
Disko has no way to be partially applyed but should be able to in the future according to 
[this](https://github.com/nix-community/disko/issues/264) and [this](https://github.com/nix-community/disko/issues/295) issue.
As a work around I extract the root disk (mountpoint at `/`) from the partitioning configuration and only force to format that disk.
Other disks are also formatted but fail if a partition table is already present.
Disko is deployed on the boot image, so you can use it.
| :warning: **Warning**   
|:------------------------|
| **Be careful**: disko formats all disks given in its configuration!

If you want to partially aplly it you need to use a modified configuration.
The complete configuration is stored at `/etc/nixos/partitioning` (emacs and vim are also deployed with the installation iso).


### Workaround for DNS issues

The default nameserver configuration does not work (on my test system).
With default settings the nixos binary cache cannot be resolved resulting updates to fail.
As a workaround I added googles nameserver (8.8.8.8) to the configuration as default.
If you like to use your own server, add the `config.nameservers = [ $ip1 $ip2 ... ]` key to your nixos config.

