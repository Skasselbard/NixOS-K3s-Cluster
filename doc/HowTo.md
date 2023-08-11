
## Requirements

- Internet access
- Physical access to the NixOS hosts
  - or a ready to use NixOS on the host to deploy to
- installation medium aka USB drive

## Setup

First you need to [setup Nix](https://nixos.org/manual/nix/stable/installation/installation.html) on your current system if you dont have yet. The scripts use a nix shell environment to get all other dependencies.

After that you can set up, your directory and download the cluster scripts:

```shell
curl -sSf https://raw.githubusercontent.com/Skasselbard/NixOS-K3s-Cluster/main/install.sh | sh
```

This will:
1. download this repository to $PWD/bin
2. create a runnable script which forwards the given arguments to the python scripts running in a nix shell environment
3. runs the created script with the `setup` subcommand to create the expected folders and example files to set up your cluster

The generated folder structure has the following form:

1. The **plans** folder contains the main infrastructure configuration.  
   There are three files expected in this folder:
   1. the **hosts.csv** contains information about the physical machines,
   2. the **k3s.csv** contains information about for the k3s container configuration and
   3. the **network.yaml** contains global network configuration needed for hosts and k3s containers.
2. The **nixConfigs** folder contains additional nix configuration you need.  
   A nix file that matches the hostname `{hostname}.nix` is expected there for every host
3. The **secrets** folder contains passwords and ssh keys needed for configuration.  
   - The token file to authenticate kubernetes hosts between each other will be stored here.
   - hashed login passwords are configured here, either
     - for all hosts with a `passwd` file
     - or for each host individually with a `{hostname}_passwd` file (takes precedence)
   - you can create a password has by running `mkpasswd -m sha-512`
   - ssh tokens can be stored here
     - for all hosts with a `ALL.pub` file
     - and for each host individually with a `{hostname}.pub` file TODO: test if this is actually implemented
   - you can [create an ssh key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) by running `ssh-keygen -t ed25519 -C "your_email@example.com"`
4. The **partitioning** folder contains [disko](https://github.com/nix-community/disko/tree/master) configurations with a partitioning layout for each host  
   - check out the [disko examples folder](https://github.com/nix-community/disko/tree/master/example) and [docs](https://github.com/nix-community/disko/blob/master/docs/INDEX.md) to write your own configuration
   - A nix file that matches the hostname `{hostname}.nix` is expected there for every host
5. The **manifests** folder contains kubernetes configuration files that will be statically [deployed by k3s](https://docs.k3s.io/installation/packaged-components)

## Workflow

What I do:

Try:

1. [Download scripts and setup](HowTo#setup) folder structure
2. Write plans for the cluster.
   - [ ] csv files
   - [ ] nix config
   - [ ] partitioning
   - [ ] passwords
   - [ ] ssh keys
   - [ ] kubernetes manifests
3. [Build a boot stick and install](HowTo#prepare-an-installation-medium) the system for every host
4. Update k3s manifests (including a git ops service) and other config.
5. Deploy cluster configuration
6. Jump to 4.

Catch (hardware problem):

7. Jump to 2.


#### Prepare an installation medium

```shell
./k3s-cluster install -n testvm -d /dev/USBdevice
```

- the boot medium contains a minimal configuration with IP and user config, and a setup script.
<!-- - the setup script is run on startup as systemd ``system_setup.service`` -->
- For every disk in the disko config, the setup script will ask to format the disk

| :warning: **Warning**  
|:------------------------|
| **Be careful**: Formatted disks loose all data!

Currently, it seems to be not possible to format single partitions, only entire configurations with disko.
I work around this problem by scraping the individual disk configs and write them in separate files.
This may fail on fancy configurations, I only test my use cases.

TODO: disko partition naming and manual partition renaming

#### Boot from the installation medium and run the setup a base system with your user and IP congifuration

On the machine:
```shell
setup
```

#### Deploy your complete configuration

```shell
./k3s-cluster hive deploy [colmena-args]
```