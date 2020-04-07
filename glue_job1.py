import datetime
import boto3
import time


now = datetime.datetime.now()
print('Job1 execution time : {}'.format(now), '\n')

s3client = boto3.client('s3')

result_list_objects = s3client.list_objects(Bucket='tuki-bkt-misc', Prefix='data/50g_split')
if result_list_objects['ResponseMetadata']['HTTPStatusCode'] == 200:
    print('Number of objects:', len(result_list_objects['Contents']))
