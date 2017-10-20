#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import json
import boto3
import os

print('Loading function')

sqs = boto3.client('sqs')


def lambda_handler(event, context):

    # Token authorize
    if event["token"] != os.environ['token']:
        return { "error": "Invalid token" }
        
    # get SQS queue object by name
    url = sqs.get_queue_url(QueueName='spot_que')['QueueUrl']
    response = sqs.send_message(
        QueueUrl=url,
        MessageBody=json.dumps(event)
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200 :
        return {
            "username": u"SQS Sender",
            "text": u"SQS enqueuing succeed."
        }
    else :
        return {
            "username": u"SQS Sender",
            "text": u"SQS enqueuing failed."
        }