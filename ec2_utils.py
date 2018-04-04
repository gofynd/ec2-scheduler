from datetime import datetime, timedelta

import constants
import boto3

from config import current_timezone
from croniter import croniter
import pytz


class EC2Utils(object):
    def __init__(self):
        tz = pytz.timezone(current_timezone)
        self.current_now = datetime.now(tz)

    def start_stop_instances(self, action, instances):
        if instances:
            if action == constants.START:
                self.client.start_instances(InstanceIds=instances)
            if action == constants.STOP:
                self.client.stop_instances(InstanceIds=instances)

    def describe_ec2_instances(self, ec2_filter=None):
        if ec2_filter is None:
            ec2_filter = [
                {
                    'Name': 'tag:AutoStartSchedule',
                    'Values': ['*']
                }, {
                    'Name': 'tag:AutoStopSchedule',
                    'Values': ['*']
                }, {
                    'Name': 'tag:ScheduledShutdown',
                    'Values': ['true']
                }
            ]
        self.client = boto3.client('ec2')
        all_ec2 = self.client.describe_instances(Filters=ec2_filter)
        return all_ec2['Reservations']

    def cron_action(self, start_cron, stop_cron, machine_state="stopped"):
        '''
            find stop and start region for current 24 hour current day
        '''

        current_datetime = self.current_now
        start_cr = croniter(start_cron, ret_type=datetime, start_time=current_datetime)
        end_cr = croniter(stop_cron, ret_type=datetime, start_time=current_datetime)
        next_start = {
            "time": start_cr.get_next(),
            "type": "running"
        }
        previous_start = {
            "time": start_cr.get_prev(),
            "type": "running"
        }

        next_stop = {
            "time": end_cr.get_next(),
            "type": "stopped"
        }

        previous_stop = {
            "time": end_cr.get_prev(),
            "type": "stopped"
        }

        '''
            find start region   
        '''
        sorted_previous = sorted([previous_start, previous_stop], key=lambda k: k.get("time"))
        sorted_next = sorted([next_start, next_stop], key=lambda k: k.get("time"))

        # print(sorted_previous[1].get("time"), sorted_previous[1].get("type"))
        # print(sorted_next[0].get("time"), sorted_next[0].get("type"))

        last_state = sorted_previous[1].get("type")
        next_state = sorted_next[0].get("type")

        action = last_state
        if action != machine_state:
            return action

        return "no action"

    def get_all_instances_to_start_stop(self, ec2_reservations):
        start_instances = []
        stop_instances = []

        for reserve in ec2_reservations:
            instances = reserve['Instances']
            for instance in instances:
                if instance['State']['Name'] in ['running', 'stopped']:
                    tags = instance.get('Tags')
                    if tags:
                        start_value = None
                        stop_value = None
                        for tag in tags:
                            if tag.get('Key') == 'AutoStartSchedule':
                                start_value = tag.get('Value')

                            if tag.get('Key') == 'AutoStopSchedule':
                                stop_value = tag.get('Value')

                        if stop_value and start_value:
                            action = self.cron_action(start_value, stop_value, instance['State']['Name'])
                            if action == 'running':
                                start_instances.append(instance['InstanceId'])
                            elif action == 'stopped':
                                stop_instances.append(instance['InstanceId'])

        return start_instances, stop_instances

    def get_all_instances(self, ec2_reservations):
        instances = []
        for reserved in ec2_reservations:
            for instance in reserved['Instances']:
                instances.append(instance['InstanceId'])
        return instances

    def create_tag(self, instances,tags):
        self.client.create_tags(Resources=instances, Tags=tags)


ec2_util = EC2Utils()
