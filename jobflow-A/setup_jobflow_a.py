#!/usr/bin/env python
# coding: utf-8

# # 1. Create jobflow-a by cloudFormation
# This template includes state machines, glue jobs and lambda functions

# In[ ]:


# Create cloudFormation stack or update if exists
def create_or_update_stack(stack_name, template_url, caps, params):
    cfn_client = boto3.client('cloudformation')
    response = cfn_client.list_stacks()
    if 'StackSummaries' in response:
        stack_names = [x['StackName'] for x in response['StackSummaries'] if x['StackStatus'] != 'DELETE_COMPLETE']
        

    if 'StackSummaries' in response and stack_name in stack_names:
        print('Update stack {}'.format(stack_name))
        cfn_client.update_stack(StackName=stack_name, TemplateURL=template_url, Capabilities=caps, Parameters=params)
    else:
        print('Create stack {}'.format(stack_name))
        cfn_client.create_stack(StackName=stack_name, TemplateURL=template_url, Capabilities=caps, Parameters=params)


# In[ ]:


# Set stack name and template location
stack_name = 'jobflow-a'
template_url = 'https://aws-glue-scripts-m3d1pb.s3-ap-northeast-1.amazonaws.com/scripts/master.yaml'
caps = ['CAPABILITY_NAMED_IAM']
params = [
    {'ParameterKey': 'S3bucket', 'ParameterValue': 'aws-glue-scripts-m3d1pb'}, 
    {'ParameterKey': 'S3bucketData', 'ParameterValue': 'aws-glue-data-m3d1pb'}]

# Execute stack creation or updation
create_or_update_stack(stack_name, template_url, caps, params)


# # 2. Create JobDate control table in dynamoDB

# In[ ]:


import boto3
import time

ddb = boto3.client('dynamodb')
tabname = 'JobDate'
pkey = [{'AttributeName': 'index', 'KeyType': 'HASH'}]
pcapacity={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
attribute_def = [{'AttributeName': 'index', 'AttributeType': 'N'}]

# recreate dynamoDB table
tables = ddb.list_tables()
if tabname in tables['TableNames']:
    # Delete table here
    ddb.delete_table(TableName=tabname)
    time.sleep(10)

ddb.create_table(
    TableName=tabname,
    KeySchema=pkey,
    AttributeDefinitions=attribute_def,
    ProvisionedThroughput=pcapacity
)


# # 3. Set job date for jobflow-A

# In[ ]:


# Set job date which is used to generate an execution name of state machine.
# job date must be unique for each jobflow execution (except for re-run)
JobDateData = {'index': {'N': '0'}, 'JobDate': {'S': '20200606'}}

ddb.delete_item(TableName=tabname, Key={'index': {'N': '0'}})
ddb.put_item(TableName=tabname, Item=JobDateData)
ddb.get_item(
    TableName=tabname, 
    Key={'index':{'N': '0'}})


# # 4. Execute jobflow-a (state machine)

# In[ ]:


sm_client = boto3.client('stepfunctions')

# Generate state machine arn of jobflow-a
region = boto3.session.Session().region_name
account_id = boto3.client('sts').get_caller_identity()['Account']
sm_arn = 'arn:aws:states:{}:{}:stateMachine:JobFlow'.format(region, account_id)

# Execute 
sm_client.start_execution(stateMachineArn=sm_arn)

