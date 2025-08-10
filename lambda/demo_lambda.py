import boto3
import os
import json
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo  # Python 3.9+

connect = boto3.client("connect")

def parse_arn(arn):
    # Example ARN: arn:aws:connect:region:account-id:instance/instance-id/operating-hours/hoop-id
    parts = arn.split(":")
    region = parts[3]
    resource_parts = parts[5].split("/")
    instance_id = resource_parts[1]
    hoop_id = resource_parts[-1]
    return instance_id, hoop_id, region

def lambda_handler(event, context):
    # Get ARN from environment variable
    # arn = os.environ.get("HOURS_OF_OPERATION_ARN")
    arn = "arn:aws:connect:us-west-2:648867426675:instance/0453967b-2a80-4e06-bf50-8adee7de69bd/operating-hours/fe0798bc-df38-412a-9beb-210ea83349aa"
    if not arn:
        return {"error": "Missing HOURS_OF_OPERATION_ARN environment variable"}

    try:
        instance_id, hoop_id, region = parse_arn(arn)
    except Exception:
        return {"error": "Invalid Hours of Operation ARN"}

    try:
        response = connect.describe_hours_of_operation(
            InstanceId=instance_id,
            HoursOfOperationId=hoop_id
        )
        
        config = response["HoursOfOperation"]["Config"]
        timezone_str = response["HoursOfOperation"]["TimeZone"]
        print("response >>>",config)
    except Exception as e:
        return {"error": f"Failed to describe Hours of Operation: {str(e)}"}

    # Get current time in HOOP's timezone
    now = datetime.now(ZoneInfo(timezone_str))
    current_day = (now.weekday() + 1) % 7  # Convert Python Mon=0 to Connect Sun=0
    current_minutes = now.hour * 60 + now.minute

    # Check today's HOOP
    today_config = next((entry for entry in config if entry["Day"] == current_day), None)
    print("today_config >>>", today_config)
    if today_config and today_config.get("StartTime") and today_config.get("EndTime"):
        start = today_config["StartTime"]["Hours"] * 60 + today_config["StartTime"]["Minutes"]
        end = today_config["EndTime"]["Hours"] * 60 + today_config["EndTime"]["Minutes"]

        if start <= current_minutes < end:
            return {"timeToWait": "30s"}  # Within HOOP
        elif current_minutes < start:
            wait_seconds = (start - current_minutes) * 60
            return {"timeToWait": f"{wait_seconds}s"}  # Before HOOP today

    # Not in today's window or already past today's HOOP, find next available slot
    for offset in range(1, 8):
        next_day = (current_day + offset) % 7
        future_config = next((entry for entry in config if entry["Day"] == next_day), None)
        if future_config and future_config.get("StartTime"):
            open_hour = future_config["StartTime"]["Hours"]
            open_minute = future_config["StartTime"]["Minutes"]
            target_date = now + timedelta(days=offset)
            next_open = datetime.combine(target_date.date(), time(open_hour, open_minute), tzinfo=ZoneInfo(timezone_str))
            wait_seconds = int((next_open - now).total_seconds())
            return {"timeToWait": f"{wait_seconds}s"}

    return {"error": "No upcoming hours of operation found"}


    return timezone_offsets.get(tz, 0)