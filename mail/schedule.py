import time
import os

from mail.config import config
from mail.emailparser import parse_email

# prerequisite: new emails should be in inbox using 'getmail'

service_list = os.listdir(config['inbox_loc'])
with open(config['blacklist_loc']) as file:
    blacklist = file.readlines()


def _add_email_feed(file_loc, service_name):
    email_info = parse_email(file_loc)
    if any(substr in email_info['From'] for substr in blacklist):
        return
    if any(substr in email_info['Subject'] for substr in blacklist):
        return
    with open(os.join(config['feed_loc'], service_name), 'a', encoding='utf8') as f:
        line = '{}\t{}'.format(email_info['Subject'], email_info['From'])
        f.write(line)


def _refresh_email_feed(service_name):
    inbox_loc = config['inbox_loc']
    latest_file_loc = os.path.join(inbox_loc, service_name, 'latest')
    if os.path.isfile(latest_file_loc):
        with open(latest_file_loc) as f:
            recent_updated_str = f.read()
            recent_updated = time.strptime(recent_updated_str, '%Y:%m:%d:%H:%M:%S').time()
    else:
        recent_updated = time.strptime('2000:01:01:00:00:00', '%Y:%m:%d:%H:%M:%S').time()

    for filename in os.listdir(os.path.join(inbox_loc, service_name)):
        if filename == 'latest':
            continue
        file_loc = os.path.join(inbox_loc, service_name, filename)
        if os.path.getmtime(file_loc) > recent_updated:
            _add_email_feed(file_loc, service_name)

    with open(latest_file_loc, 'w') as f:
        recent_updated_str = time.localtime().strftime('%Y:%m:%d:%H:%M:%S')
        f.write(recent_updated_str)


for service in service_list:
    _refresh_email_feed(service)
