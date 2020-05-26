import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'glue_db', 'sql_string', 'out_path'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Get job parameter include SQL string from DynamoDB
glue_db = args['glue_db']
sql_string = args['sql_string']
out_path = args['out_path']

# Define Glue catalog database as a hive metadata store
spark.sql('use {}'.format(glue_db))

# Execute sql
df_sql_result = spark.sql(sql_string)

# Convert DataFrame to DynamicFrame for s3 writing
ddf_sql_result = DynamicFrame.fromDF(df_sql_result, glueContext, 'df_to_ddf')

# Write DynamicFrame to S3
datasink4 = glueContext.write_dynamic_frame.from_options(frame=ddf_sql_result, connection_type='s3', connection_options={'path': out_path}, format='parquet', transformation_ctx='ctx_save_parquet')

job.commit()