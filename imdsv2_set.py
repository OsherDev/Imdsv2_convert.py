import boto3
import json

#Boto3 clients
ec2_client = boto3.client('ec2')

def list_instances():
    response = ec2_client.describe_instances()
    return response["Reservations"]
def revert_imdsv2(reservations):
    for reservation in reservations:
        for instance in reservation["Instances"]:   
            instance_metadata_options = instance["MetadataOptions"]["HttpTokens"]
            instance_id = instance["InstanceId"]
            if instance_metadata_options == "required":
                try:
                    response = ec2_client.modify_instance_metadata_options(InstanceId=instance_id,HttpTokens='optional')
                    print(f"Updated instance to not require HTTP Tokens: {instance_id}")
                except Exception as e:
                    return f"The following exception occured: {e}"
            elif instance_metadata_options == "optional":
                print(f"Instance is already not required to use HTTP Tokens: {instance_id}")

def update_imdsv2(reservations):
    instance_tags = []
    for reservation in reservations:
        is_ecs = False
        for instance in reservation["Instances"]:   
            instance_metadata_options = instance["MetadataOptions"]["HttpTokens"]
            instance_id = instance["InstanceId"]
            if "Tags" in instance:
                instance_tags = instance["Tags"]
            for tag in instance_tags:
                if "Name" in tag["Key"]:
                    if "ecs" in tag["Value"].lower():
                        is_ecs = True
            if instance_metadata_options == "optional":
                if is_ecs:
                    print(f"Skipping ECS Instance {instance_id}")
                    continue
                try:
                    response = ec2_client.modify_instance_metadata_options(InstanceId=instance_id,HttpTokens='required')
                    print(f"Updated instance to use IMDSv2: {instance_id}")
                except Exception as e:
                    return f"The following exception occured: {e}"
            elif instance_metadata_options == "required":
                print(f"Instance is already requiring IMDSv2: {instance_id}")

def lambda_handler(event, context):
  
    instances = list_instances()
    update_imdsv2(instances)
    #revert_imdsv2(instances)
