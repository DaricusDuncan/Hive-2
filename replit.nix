{pkgs}: {
  deps = [
    pkgs.chromium
    pkgs.geckodriver
    pkgs.openssl
    pkgs.postgresql
  ];
}
