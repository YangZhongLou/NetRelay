# NetRelay
Download contents in relay server, and send them to target client.

Configure NetRelayConfig.json
    -server_ip, "server's ip"
    -username, "ftp username"
    -password, "ftp password"

Currently, only used to download video from youtube.

To run server:
    python3 server.py ""

Environment:
-FTP server.
-pytube. To install pytube, "pip install pytube" for python2, "pip3 install pytube" for python3

Python version: 3.6
