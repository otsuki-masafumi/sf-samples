import datetime
import boto3
import time
import sys
from awsglue.utils import getResolvedOptions

# State Machineから渡された引数（bucket_name）を変数に格納
args = getResolvedOptions(sys.argv, ['bucket_name'])
print('arg Bucket Name: {}'.format(args['bucket_name']))


now = datetime.datetime.now()
print('Job4 execution time : {}'.format(now), '\n')

s3client = boto3.client('s3')

result_list_objects = s3client.list_objects(Bucket='tuki-bkt-misc', Prefix='data/50g_split')
if result_list_objects['ResponseMetadata']['HTTPStatusCode'] == 200:
    print('Number of objects:', len(result_list_objects['Contents']))

