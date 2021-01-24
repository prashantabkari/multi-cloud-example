import json
import boto3
import io

from google.cloud import vision

s3_client = boto3.resource('s3')

def lambda_handler(event, context):
    # TODO implement
    client = vision.ImageAnnotatorClient()
    
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket='gcp-image', Key='front.jpg')
    image_bytes = response['Body'].read()
    print(image_bytes)
    
    image = vision.Image(content=image_bytes)

    response = client.label_detection(image=image)
    labels = response.label_annotations
    print('Labels:')
    for label in labels:
        print(label.description)

    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
