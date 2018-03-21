from ftplib import FTP
import config, constants, os

def download(filename):
    config_data = config.get_config()

    ftp = FTP(config_data['server_ip'])
    ftp.login(config_data['username'], config_data['password'])
    ftp.cwd(constants.FTP_DIR)

    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            ftp.retrbinary('RETR %s' % filename, f.write)
            print('finished downloading %s' % filename)

    ftp.quit()
