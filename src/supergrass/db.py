import boto3
from boto3.dynamodb.conditions import Key, Attr

class DB:
    def __init__(self, **kwargs):
        region = kwargs.get('region', 'eu-west-1')

        table_name = kwargs.get('table')

        self.db = {
            True: boto3.resource('dynamodb', region_name=region, endpoint_url="http://localhost:8000"),
            False: boto3.resource('dynamodb', region_name=region)
        }[kwargs.get('local', False)]
        self.table = self.db.Table(table_name)


    def insert(self, struct):
        return self.table.put_item(Item=struct)

    # Primary Key
    def search_by_uuid(self, uuid):
        workflows = self.table.query(
            KeyConditionExpression=Key('UUID').eq(uuid)
        )
        if workflows['Count'] == 0:
            return None
        return workflows['Items'][0]

    # Expensive, full table scans
    def query(self, key, value, last=None):
        outs = []

        if last:
            items = self.table.scan(
                FilterExpression=Key(key).eq(value),
                ExclusiveStartKey=last
            )
        else:
            items = self.table.scan(
                FilterExpression=Key(key).eq(value)
            )

        outs.extend(items['Items'])
        if 'LastEvaluatedKey' in items:
            outs.extend( self.query(key, value, items['LastEvaluatedKey']) )

        return outs

    # The following are, by and large, as per stored procedures
    def search_by_id_and_url(self, workflow, mio_url):
        workflows = self.table.query(
            ProjectionExpression='#u, WorkflowID, MioURL',
            ExpressionAttributeNames={'#u': 'UUID'},
            KeyConditionExpression=Key('WorkflowID').eq(str(workflow)),
            IndexName='WorkflowID-index'
        )
        for wf in workflows['Items']:
            wf_mio_url = self.search_by_uuid(wf['UUID'])['MioUrl']
            if wf_mio_url == mio_url:
                return wf['UUID']

        return None
