#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import datetime
import json
import os

# ec2 resources
client            = boto3.client('ec2')
dynamodb          = boto3.resource('dynamodb')
table_name        = os.environ['table_name']

# Spot request Specification
spot_price        = float(os.environ['spot_price'])     # ex) 0.05 [$]
duration_minutes  = int(os.environ['duration_minutes']) # ex) 360 [min] -> instance runs 6 hours
security_group_id = os.environ['security_group_id']     # ex) sg-xxxxxxxx
instance_type     = os.environ['instance_type']         # ex) c4.xlarge
availability_zone = os.environ['availability_zone']     # ex) ap-northeast-1c
subnet_id         = os.environ['subnet_id']             # ex) subnet-xxxxxxxx

iam_profile_arn   = os.environ['iam_profile_arn']
iam_fleet_arn     = os.environ['iam_fleet_arn']


instance_count    = 1
request_type      = "request"
valid_until       = datetime.datetime.now() + datetime.timedelta(minutes = duration_minutes)

def lambda_handler(event, context):

    # Token authorize
    if event["token"] != os.environ['token']:
        return { "error": "Invalid token" }
        
    table = dynamodb.Table(table_name)

    # 現在状態が停止であれば起動する
    info = table.get_item(
        Key={
            "Id": '1'
        }
    )['Item']

    if info['state'] == 'stop':
        # 起動するぞう

        
        table.update_item(
            Key={
                'Id': '1'
            },
            AttributeUpdates={
                'state': {
                    'Action': 'PUT',
                    'Value': 'startup'
                },
                'expire': {
                    'Action': 'PUT',
                    'Value': valid_until.isoformat()
                }
            }
        )
        
        response = client.request_spot_fleet(
            DryRun = False,
            SpotFleetRequestConfig = {
                "SpotPrice"           : spot_price,
                "TargetCapacity"      : instance_count,
                "Type"                : request_type,
                "ValidUntil"          : valid_until.replace(microsecond=0),
                "TerminateInstancesWithExpiration" : True,
                "IamFleetRole"        : iam_fleet_arn,
                "LaunchSpecifications"  : [
                    {
                        "ImageId"          : info['latest_ami'],
                        "SecurityGroups" : [{
                            "GroupId" : security_group_id
                        }],
                        "InstanceType"     : instance_type,
                        "Placement"        : {
                            "AvailabilityZone" : availability_zone
                        },
                        "IamInstanceProfile": {
                            "Arn": iam_profile_arn
                        },
                        "SubnetId"         : subnet_id
                    }
                ]
                
            }
        )
       
       return {
            "username": u"Server Strarter",
            "text": u"Spot fleet request succeed."
        }
   else:
       if info['state'] == 'startup':
            return {
                "username": u"Server Strarter",
                "text": u"Spot fleet instance is starting up..."
            }
           
       if info['state'] == 'running':
            return {
                "username": u"Server Strarter",
                "text": u"Spot fleet instance is running."
            }