import os
import json
import boto3
import gzip
from time import sleep, time


def deploy_trail():
    """Create s3 bucket and cloudtrail via cfn"""
    print("Deploying Cloudtrail")
    my_dir = os.path.dirname(__file__)
    client = boto3.client("cloudformation", region_name="us-east-1")
    cfn_template_body = open(os.path.join(my_dir, "bucket.yml")).read()
    response = client.create_stack(
        StackName="bucket-stack",
        TemplateBody=cfn_template_body,
    )

    # Wait for bucket stack to finish deploying to deploy trail
    response = client.describe_stacks(StackName="bucket-stack")
    while response["Stacks"][0]["StackStatus"] == "CREATE_IN_PROGRESS":
        sleep(2)
        response = client.describe_stacks(StackName="bucket-stack")

    cfn_template_body = open(os.path.join(my_dir, "trail.yml")).read()
    response = client.create_stack(
        StackName="trail-stack",
        TemplateBody=cfn_template_body,
    )

    # Wait for trail to deploy to finish
    response = client.describe_stacks(StackName="trail-stack")
    while response["Stacks"][0]["StackStatus"] == "CREATE_IN_PROGRESS":
        sleep(2)
        response = client.describe_stacks(StackName="trail-stack")

    # NOTE - Cloudtrail weird, give it a sec to settle
    sleep(3)


def generate_trail_events():
    # Since trail listens for any s3 write event, lets make a bucket and add a file
    print("Generating trail event")
    bucket_name = "test-data-bucket435432322"
    s3_client = boto3.client("s3", region_name="us-east-1")
    s3_client.create_bucket(Bucket=bucket_name)
    encoded_string = "Hi peeps".encode("utf-8")
    file_name = "test.txt"
    # NOTE may need this line instead when executing in localstack
    # s3 = boto3.resource("s3", verify=False)
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=file_name, Body=encoded_string)


def get_trail_events():
    """Look for cloudtrail events"""
    print("Getting trail events")
    client = boto3.client("sts")
    account_id = client.get_caller_identity()["Account"]
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("test-bucket-logging432432")

    objs = list(bucket.objects.filter(Prefix=f"AWSLogs/{account_id}/CloudTrail/us-east-1"))
    while len(objs) == 0:
        sleep(15)
        objs = list(bucket.objects.filter(Prefix=f"AWSLogs/{account_id}/CloudTrail/us-east-1"))

    log_files = [log_file.key for log_file in bucket.objects.all() if ".gz" in log_file.key]
    print(f"Log Files Found: {len(log_files)}")
    print(log_files)
    print("Downloading log files")

    s3 = boto3.client("s3")
    for log_file in log_files:
        filename = f"test{time()}.gz"
        s3.download_file("test-bucket-logging432432", log_file, filename)
        f = gzip.open(filename, "rb")
        file_content = f.read()
        data = json.loads(file_content)
        print(data)
        f.close()


if __name__ == "__main__":
    deploy_trail()
    generate_trail_events()
    get_trail_events()
