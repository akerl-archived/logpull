#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml
import imaplib
import email
import tarfile
import tempfile
import gnupg

CONFIG_FILE = 'config.yaml'


def follow_symlink(path):
    if os.path.islink(path):
        return follow_symlink(os.readlink(path))
    return path


def get_path():
    first_location = os.path.abspath(__file__)
    real_location = follow_symlink(first_location)
    return os.path.dirname(real_location)

os.chdir(get_path())

if len(sys.argv) > 1:
    config_path = os.path.expanduser(sys.argv[1])
else:
    config_path = CONFIG_FILE

if not os.path.isfile(config_path):
    print('No config.yaml found')
    raise SystemExit

with open(CONFIG_FILE) as handle:
    config = yaml.load(handle)

config.setdefault('port', 993)
config.setdefault('log_dir', 'logs')

gpg = gnupg.GPG(binary='/usr/local/MacGPG2/bin/gpg2', homedir='gnupg')

if 'password_source' in config:
    if config['password_source'] == 'keychain':
        print('Trying to load password from OSX keychain')
        try:
            config['password'] = [
                x.split('"')[1]
                for x in str(subprocess.check_output(
                    [
                        'security',
                        'find-generic-password',
                        '-g',
                        '-s', 'logpull',
                        '-a', config['username'],
                    ],
                    stderr=subprocess.STDOUT
                ), encoding='utf-8').split('\n')
                if x.find('password:') == 0
            ][0]
        except:
            print('Failed to load password')
            raise
    else:
        print('Unsupported password method')
        raise SystemExit
if 'password' not in config:
    print('No password provided')
    raise SystemExit

imap_conn = imaplib.IMAP4_SSL(
    host=config['host'],
    port=config['port'],
)
imap_conn.login(config['username'], config['password'])
_, count = imap_conn.select(config['new_label'])
print('Message count: {0}'.format(int(count[0])))

uids = imap_conn.uid('search', None, 'ALL')[1][0].split()
for uid in uids:
    _, raw_message = imap_conn.uid('fetch', uid, "(RFC822)")
    message = email.message_from_string(raw_message[0][1].decode())
    hostname = message['From'].split('@')[1].split('.', 1)[0]
    year, month, day = [
        str(x).zfill(2)
        for x in email.utils.parsedate(message['Date'])[:3]
    ]
    paths = [
        x.format(
            hostname=hostname,
            year=year,
            month=month,
            day=day,
        )
        for x in config['paths']
    ]

    print('Parsing: {0} -- {1}'.format(
        '/'.join([year, month, day]),
        hostname,
    ))

    _, tmp_path = tempfile.mkstemp()
    for part in message.walk():
        if part.get_content_type() not in ['application/x-gzip', 'application/octet-stream']:
            continue
        with open(tmp_path, 'wb') as handle:
            decrypted = gpg.decrypt(part.get_payload(decode=True))
            if not decrypted.valid:
                print('Invalid signature')
                raise SystemExit
            handle.write(decrypted.data)
        break
    with tarfile.open(tmp_path) as archive:
        cwd = os.getcwd()
        for path in archive.getmembers():
            if not path.isfile() or os.path.abspath(path.name).find(cwd) != 0:
                print('This tarball contains a malformed file: {0}'.format(path.name))
                raise SystemExit
        archive.extractall(config['log_dir'] + '/' + paths[0])
    for path in paths[1:]:
        os.makedirs(
            config['log_dir'] + '/' + path.rsplit('/', 1)[0],
            exist_ok=True
        )
        if not os.path.islink(config['log_dir'] + '/' + path):
            os.symlink(
                '../' * paths[0].count('/') + paths[0],
                config['log_dir'] + '/' + path,
            )
    os.remove(tmp_path)

    imap_conn.uid('COPY', uid, config['done_label'])
    imap_conn.uid('STORE', uid, '+FLAGS', '(\Deleted)')

imap_conn.expunge()

