{config, ...}:
{
    services.openssh.enable = true;
    services.openssh.permitRootLogin = "prohibit-password";
    services.openssh.passwordAuthentication = false;
    networking.firewall.allowedTCPPorts = config.services.openssh.ports;
}