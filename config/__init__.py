import os

from . import staging, dev

config = {
    'staging': staging,
    'dev': dev
}

config_name = os.environ.get('ec2_scheduler', 'dev')
current_timezone = os.environ.get('timezone','Asia/Kolkata')
current_config = config.get(config_name)
