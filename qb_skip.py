import os, shutil
from qbittorrent import Client
from urllib.parse import parse_qs
import time
import requests  # 新增 requests 库用于直接调用 API

qb_url = ''
qb_username = ''
qb_password = ''
qb_backup_path = ''
tmp_path = os.getcwd() + '/'
iyuu = True

# 新增函数：通过 Web API 添加标签
def add_tag_to_torrent(hash, tag):
    session = requests.Session()
    session.post(f"{qb_url}/api/v2/auth/login", 
                data={'username': qb_username, 'password': qb_password})
    session.post(f"{qb_url}/api/v2/torrents/addTags", 
                data={'hashes': hash, 'tags': tag})

qb = Client(qb_url)
qb.login(qb_username, qb_password)
torrents = qb.torrents()
check_torrents=[]
state = 'stoppedDL' if iyuu else 'checkingUP'  #stoppedDL或者pausedDL
for torrent in torrents:
    #print(torrent['state'])
    if torrent['state'] == state:
        check_torrents.append(torrent)
print('Get', len(check_torrents), 'torrents.')
for torrent in check_torrents:
    filename = torrent['hash'] + '.torrent'
    shutil.copy(qb_backup_path+filename, tmp_path)
    qb.delete(torrent['hash'])
    with open(tmp_path+filename,'rb') as f:
        qb.download_from_file(f,save_path=torrent['save_path'],category=torrent['category'],skip_checking=True)
    uri = torrent['magnet_uri'].split(':', 3)[-1]
    params = parse_qs(uri)
    if iyuu and 'tr' in params.keys() and params['tr']:
        time.sleep(1)
        qb.add_trackers(torrent['hash'], params['tr'])
        add_tag_to_torrent(torrent['hash'], "IYUU自动辅种")
        os.remove(tmp_path + filename)
    if not iyuu:
        os.remove(tmp_path + filename)
    print('Force skip ' + torrent['name'])
print('Finished.')
