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

start a ftp server for client:
	sudo apt-get install vsftpd
	mkdir /home/ftp
	sudo useradd -d /home/ftp -s /bin/bash your-ftp-usr-name
	passwd your-ftp-usr-name

	note:Edit vsftpd.conf for security.


Python version: 3.6
