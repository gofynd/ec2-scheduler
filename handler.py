import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "vendors"))

import json
from ec2_utils import ec2_util
import constants


def start_stop(event, context):
    reserved_instances = ec2_util.describe_ec2_instances()
    if not reserved_instances:
        return set_response(400, {'message': 'no ec2 instance found'})
    start_instances, stop_instances = ec2_util.get_all_instances_to_start_stop(reserved_instances)
    ec2_util.start_stop_instances('start', start_instances)
    ec2_util.start_stop_instances('stop', stop_instances)
    body = {
        "message": "Ec2 Scheduler run successfully!",
        "instances": {'start': start_instances, 'stop': stop_instances}
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def handle_multi_ec2(event, context):
    body = json.loads(event['body'])
    if 'instance_ids' not in body or 'action' not in body:
        return set_response(400, {'message': 'instance_ids and action are required parameters'})

    if not body['action'] in constants.action_supported:
        return set_response(400, {'message': body['action'] + ' action not supported'})

    instance_ids = body['instance_ids']

    if type(instance_ids) != list:
        return set_response(400, {'message': 'type of instance_ids must be list'})

    ec2_reserved = ec2_util.describe_ec2_instances(
        ec2_filter=[{
            'Name': 'instance-id',
            'Values': instance_ids
        }])

    if not ec2_reserved:
        return set_response(400, {
            "instance_ids": instance_ids,
            'message': 'instance ids not found'
        })

    instances = ec2_util.get_all_instances(ec2_reserved)

    ec2_util.start_stop_instances(body['action'], instances)
    if body['action'] == 'start':
        ec2_util.create_tag(instances, [{'Key': 'ScheduledShutdown','Value':'false'}])
    else:
        ec2_util.create_tag(instances, [{'Key': 'ScheduledShutdown','Value':'true'}])

    response_body = {
        "instance_ids": instance_ids,
        "message": body['action'] + " executed successfully",
    }

    return set_response(200, response_body)


def handle_group_ec2(event, context):
    body = json.loads(event['body'])
    if 'group_ids' not in body or 'action' not in body:
        return set_response(400, {'message': 'group_ids and action are required parameters'})

    if not body['action'] in constants.action_supported:
        return set_response(400, {'message': body['action'] + ' action not supported'})

    group_ids = body['group_ids']

    if type(group_ids) != list:
        return set_response(400, {'message': 'type of group_ids must be list'})

    group_ec2 = ec2_util.describe_ec2_instances(ec2_filter=[
        {
            'Name': 'tag:Domain',
            'Values': group_ids
        }
    ])

    group_instances = ec2_util.get_all_instances(group_ec2)

    ec2_util.start_stop_instances(body['action'], group_instances)
    if body['action'] == 'start':
        ec2_util.create_tag(group_instances, [{'Key': 'ScheduledShutdown','Value':'false'}])
    else:
        ec2_util.create_tag(group_instances, [{'Key': 'ScheduledShutdown','Value':'true'}])

    response_body = {
        "instance_ids": group_instances,
        "message": body['action'] + " executed successfully",
    }

    return set_response(200, response_body)


def set_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps(message)
    }
