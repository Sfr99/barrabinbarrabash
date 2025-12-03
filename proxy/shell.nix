{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    flask
    fastapi
    uvicorn

    pydantic
    requests
    httpx
    jinja2
    python-dotenv
  ]);

in pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.curl
    pkgs.git
    pkgs.psmisc
  ];

  shellHook = ''
    echo "==================================================="
    echo " ❄  Welcome to the NixOS Python Environment  ❄ "
    echo "==================================================="
    echo "Python version: $(python --version)"
    echo "Network Tools: curl, killall (psmisc) ready."
    echo ""
    echo "To run the proxy:"
    echo "  python udp_forwarder.py"
    echo "==================================================="
  '';
}
