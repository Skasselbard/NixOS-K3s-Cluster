{config, ...}:
{
    services.openssh.enable = true;
    services.openssh.settings.PermitRootLogin = "prohibit-password";
    services.openssh.settings.PasswordAuthentication = false;
    networking.firewall.allowedTCPPorts = config.services.openssh.ports;
}