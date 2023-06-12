# Nixos K3s Cluster

Build and deploy a NixOs k3s cluster according to a set of plans.
TODO: link NixOS and other stuff

This project builds and deploys a set of NixOS hosts and runs a Kubernetes cluster in containers.
Its goal is to set up the hardware for a bare metal home cloud with a maximal level of automation.
The configuration is a set of csv tables which also document your deployments.

## Goals

1. Provide a minimal configuration for a K3s Cluster on NixOS
2. Configure a local static network and ssh access (with ssh keys)
3. Leave room for additional NixOS host configuration including non K3s nodes
4. Create installation media for an initial machine setup
5. Deploy updates and change configuration remotely once the machines are initialized
6. Keep the human interaction minimal in the process

## Non Goals

- Configure Kubernetes and Container Apps
- configure non essential network like additional firewall rules
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
- The k3s server is running in a [nixos-container](https://nixos.wiki/wiki/NixOS_Containers) (because it is an easy NixOS integration)
- The k3s agent runs in a podman container (because it needs to be privileged access, which I couldn't figure out for the nixos-containers)
- Every host and k3s container have a static IP address
- Each host can run at most one k3s server and/or agent
  - hosts can be defined without k3s containers for additional deployments
- The network is configured as macvlan
  - including the host configuration
  - the host and the k3s containers share the same interface
- Containers are in the same subnet with the same gateway as the host
  - which of course should be reachable from the deploying machine
- The nix configuration is built on the deploying machine
- Each host has an admin user
  - The NixOS on the associated container for the k3s server (if it exists) has the same admin user
- Hosts are accessible by ssh
  - ssh connections prohibit passwords and root logins (only ssh keys are allowed)
  - the admin user has a password for sudo once an ssh connection is established
- Kubernetes versions are shared
  - All k3s-servers run the same NixOs version
  - All k3s-agents run the same Kubernetes image

No data folders are mounted for the containers.
Deleting the Container deletes all Kubernetes data on the host.

## Requirements

- Internet access
- Physical access to the NixOS hosts
  - or a ready to use NixOS on the host to deploy to

## Setup

Checkout folder structure
```shell
curl smth smth
```

You may want to backup your plans for example in a git repo.
TODO: Link to create a repo from folder.


## Configuration

- Physikal machine and network configuration -> in the hosts.csv
- k3s container and network configuration -> k3s.csv
- additional nix config in "TODO" subfolder
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
host| name| type| ip| ssh-access
|-|-|-|-|-|
olaf| olaf-k3s-server| init-server| 10.0.100.10| true
olaf| olaf-k3s-agent| agent| 10.0.100.11| ignored
ulf| ulf-k3s-server| server| 10.0.100.12| false
ulf| ulf-k3s-agent| agent| 10.0.100.13| ignored
rolf| rolf-k3s-server| server| 10.0.100.14| true
karl| karl-k3s-agent| agent| 10.0.100.15| ignored

| :bulb: INFO   
|:------------------------|
| k3s Agents cannot be accessed via ssh so their ssh-access field is ignored|
|TODO: Is the key even needed? SSH can be part of extra config|
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
