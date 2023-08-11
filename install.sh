mkdir -p bin
wget -qO- https://github.com/Skasselbard/NixOS-K3s-Cluster/archive/master.tar.gz | tar xvz --strip-components=1  -C bin

echo '#!/bin/bash

ROOT=$PWD
CMD="k3s-cluster -p $ROOT ${@:1}"
cd bin
nix-shell --run "$CMD"
' > k3s-cluster

chmod +x k3s-cluster