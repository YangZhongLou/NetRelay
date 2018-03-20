from ftplib import FTP, error_perm

downloaded = {}

def walk_dir(ftp, dirpath):
    original_dir = ftp.pwd()
    try:
        ftp.cwd(dirpath)
    except error_perm:
        return  # ignore non-directores and ones we cannot enter
    print(dirpath)
    names = sorted(ftp.nlst())
    for name in names:
        print('################ name:', name)
        walk_dir(ftp, dirpath + '/' + name)
    ftp.cwd(original_dir)  # return to cwd of our caller

def download(filename):
    ftp = FTP('198.13.59.123')
    ftp.login('ftpname', '$wK37dJ#Hbf.!{zy')
    walk_dir(ftp, '/home/ftp/')
    ftp.quit()
