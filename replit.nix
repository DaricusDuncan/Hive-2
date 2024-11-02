{pkgs}: {
  deps = [
    pkgs.ollama
    pkgs.chromedriver
    pkgs.nodePackages.prettier
    pkgs.chromium
    pkgs.geckodriver
    pkgs.openssl
    pkgs.postgresql
  ];
}
