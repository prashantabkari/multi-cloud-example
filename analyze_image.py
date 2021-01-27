import os
from google.cloud import vision
from azure.cosmos import exceptions,CosmosClient,PartitionKey
import io
import boto3
import urllib.parse
import json

class ImageClassifier:
    gcpVisionClient= None
    azureClient= None
    azureContainer = None
    awsClient= None

    def __init__(self):
        self.InitializeGCPVision()
        self.InitializeAWS()
        self.InitializeAzureClient()


    def InitializeGCPVision(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"
        self.gcpVisionClient = vision.ImageAnnotatorClient()


    def InitializeAzureClient(self):
        azureClient = CosmosClient(url='https://image-classifier-account.documents.azure.com:443/',
                              credential='awLJ29b0qWxFtFntdmIy2KbVty5jFkprpV3HGWFz9UNUSrzugH3MWQ2pFm1eQVcjH8o8GqQbJqSTXKlGPYa0SQ==')

        database_name = "mc_image_db"
        try:
            database = azureClient.create_database(id=database_name)
        except exceptions.CosmosResourceExistsError:
            database = azureClient.get_database_client(database=database_name)

        container_name = "images"
        try:
            self.azureContainer = database.create_container(
                id=container_name, partition_key=PartitionKey(path="/logo_name")
            )
        except exceptions.CosmosResourceExistsError:
            self.azureContainer = database.get_container_client(container_name)

    def InitializeAWS(self):
        # Get URL and Credential from SSM Parameter
        self.awsClient = boto3.client('s3')


    def GetLogoAnnotations(self,bucket, key):

        print("Bucket : Name", bucket)
        print("Key", key)
        try:
            response = self.awsClient.get_object(Bucket=bucket, Key=key)
        except Exception as e:
            print(e)
            print(
                'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                    key, bucket))
            raise e

        image_bytes = response['Body'].read()
        image = vision.Image(content=image_bytes)

        # Performs logo detection on the image file
        label_response = self.gcpVisionClient.logo_detection(image=image)
        labels = label_response.logo_annotations
        print(labels)
        return labels

    def StoreLogoAnnotations(self,annotations):
        for label in annotations:
            self.azureContainer.upsert_item({
                'logo_name': label.description,
                'score': label.score
            })

def lambda_handler(event, context):

    image_classifier = ImageClassifier()

    #Parse the S3 Event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    annotations = image_classifier.GetLogoAnnotations(bucket,key)
    image_classifier.StoreLogoAnnotations(annotations)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

