let
  nixconfigs = (builtins.fetchGit {
    url = "https://github.com/Skasselbard/nixconfigs";
  }).outPath;
in {
  imports = [
    "${nixconfigs}/machines/physical_machines/boot.nix"
    "${nixconfigs}/machines/physical_machines/partitioning.nix"
  ];
}
