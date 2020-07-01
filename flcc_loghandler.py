# Failed Laboratories Department of Technology
# Failed Labs Central Command:
# CloudWatch Logging Handler
#
# Before use, explicit permission must be granted
# by a Department of Technology supervisor under
# the authorization and supervision of the
# Failed Laboratories Director of Tecnology.
#
# Copyright (c) 2020 Failed Laboratories
# Department of Technology. All Rights Reserved.

import boto3
import json
import pytz
import time
from botocore.exceptions import ClientError
from datetime import datetime
#from fldbutils.utils import truncate

__author__ = "Faied Laboratories Department of Technology.\nCopyright (c) 2020 Failed Laboratories Department of Technology. All Rights Reserved."
__version__ = "1.0.0"

pacific = pytz.timezone("US/Pacific")

class CloudwatchLogger():
    log_cache = []
    log_group_name = ""
    cloudwatch_logs = ""
    timezone = ""

    def __init__(self, logGroupName, cloudwatchRegion="us-west-2", timezone="US/Pacific"):
        CloudwatchLogger.log_group_name = logGroupName
        CloudwatchLogger.timezone = timezone
        if CloudwatchLogger.cloudwatch_logs == "":
            CloudwatchLogger.cloudwatch_logs = boto3.client("logs", region_name=cloudwatchRegion)

    def log(self, message):
        """Accepts a message and adds it to the utility's global log cache,
        adding a UTC timestamp in seconds after 1 January 1970 (1970-01-01).
        Then, returns a pretty-formated string with the timestamp in ISO
        format and the message."""
        current_time = time.time()
        current_time_dt = datetime.fromtimestamp(current_time)
        local_time = pytz.timezone(CloudwatchLogger.timezone).localize(current_time_dt)
        cloudwatch_timestamp = int(local_time.timestamp() * 1000)
        self.log_cache.append(
            {
                "timestamp": cloudwatch_timestamp,
                "message": f"{message}"
            }
        )

        return f"[{local_time.isoformat()}]: {message}"

    def __generate_log_stream_name(self):
        """Accepts no parameters. Generates and returns a log stream name
        based on the current date in UTC."""
        current_date = datetime.now()
        current_date_friendly = current_date.strftime("%Y-%m-%d")
        log_stream_name = "cmds-" + current_date_friendly
        return log_stream_name

    def send_to_cloudwatch(self):
        """Accepts no parameters. Automatically takes a generated log stream
        name, checks CloudWatch for an Upload Sequence Token (if any),
        sends the current log_cache to CloudWatch, then clears the log_cache."""
        log_group_name = CloudwatchLogger.log_group_name
        log_stream_name = self.__generate_log_stream_name()
        events = CloudwatchLogger.log_cache
        cloudwatch_logs = CloudwatchLogger.cloudwatch_logs
        upload_sequence_token = ""
        create_new_log_stream = True
        
        try:
            response = cloudwatch_logs.describe_log_streams(
                logGroupName=log_group_name,
                logStreamNamePrefix=log_stream_name
            )
        except Exception as e:
            print(e)
        else:
            log_streams = response["logStreams"]
            for stream in log_streams:
                stream_name = stream["logStreamName"]
                if stream_name == log_stream_name:
                    create_new_log_stream = False
                    if "uploadSequenceToken" in stream:
                        upload_sequence_token = stream["uploadSequenceToken"]
            if create_new_log_stream:
                try:
                    response = cloudwatch_logs.create_log_stream(
                        logGroupName=log_group_name,
                        logStreamName=log_stream_name
                    )
                except Exception as e:
                    print(e)
                
        try:
            if not bool(upload_sequence_token):
                response = cloudwatch_logs.put_log_events(
                    logGroupName=log_group_name,
                    logStreamName=log_stream_name,
                    logEvents=events
                )
            else:
                response = cloudwatch_logs.put_log_events(
                    logGroupName=log_group_name,
                    logStreamName=log_stream_name,
                    logEvents=events,
                    sequenceToken=upload_sequence_token
                )
        except Exception as e:
            print(e)
        else:
            print("Sent to Cloudwatch")
            # print("Response: ")
            # print(json.dumps(response, indent=4))