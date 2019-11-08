import json
import boto3

class firstaid: 
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = "first-aid-date"
        self.resources_file = "resources.txt"

    def get_file_from_s3(self, file_name):
        self.file = self.s3_client.get_object(
            Bucket = self.bucket_name, 
            Key = file_name)
        response = self.s3_client.get_object(
            Bucket = self.bucket_name, 
            Key = file_name
        )
        content = response.get()['Body'].read().decode('utf-8')
        json_content = json.loads(content)
             
    def list_burn_categories(self): 
        response = self.s3_client.get_object(Bucket = self.bucket_name, Key = self.resources_file)
        content = response['Body'].read().decode('utf-8')
        print(content)
