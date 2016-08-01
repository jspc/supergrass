import datetime
import time
import uuid
from operator import itemgetter

from random import randint

class Model:
    def __init__(self, **kwargs):
        self.db = kwargs.get('db')
        self.mio = kwargs.get('mio')

    def uuid(self, obj_id):
        object_uuid = self.db.search_by_id_and_url(obj_id, self.mio.url)

        if object_uuid:
            return object_uuid

        new_uuid = str(uuid.uuid4())
        print "Minting UUID '{}'.".format(new_uuid)
        return new_uuid

    def timestamp(self, uuid):
        return int( time.time() - randint(30,86400) )

        obj = self.db.search_by_uuid(uuid)
        if obj and 'Timestamp' in obj:
            return obj['Timestamp']

        return int(time.time())

    def process_time(self, start, end):
        # This kind of mungery is because PYTHON IS FUCKING AWFUL
        if end == None:
            return 0

        fmt = '%d %b %Y %X +0000'
        start_obj = datetime.datetime.strptime(start, fmt)
        end_obj = datetime.datetime.strptime(end, fmt)

        return (end_obj - start_obj).seconds

    def sort(self, **kwargs):
        key = kwargs.get('key')
        value = kwargs.get('value')
        sort_on = kwargs.get('sort_on')
        desc = kwargs.get('desc', False)

        values = self.db.query(key, value)
        sorted_items = sorted(values, key=itemgetter(sort_on))

        if desc:
            sorted_items.reverse()
        return sorted_items

    def time_period(self, items, **kwargs):
        key = kwargs.get('key', 'Timestamp')
        length = kwargs.get('length', 300)
        end_time = kwargs.get('end', int(time.time()))

        start_time = end_time - length
        elems = []

        # We work with the assumption that items is a sorted
        # array from self.sort(). If not, this may return
        # fewer elements than expected
        for item in items:
            if start_time <= item[key] <= end_time:
                elems.append(item)
            else:
                break
        return elems

class Workflow(Model):
    def asset_size(self, asset_url):
        asset = self.mio.get(asset_url)

        if asset['objectType']['name'] == 'group-asset':
            size = 1
        else:
            size = asset['assetContext']['formatContext']['fileSize']
        return size

    def create(self, struct):
        struct['MioUrl'] = self.mio.url
        struct['WorkflowID'] = str(struct['WorkflowID'])

        return self.db.insert(struct)

    def get_all(self, last_workflow=None):
        return self.mio.workflows(last_workflow)

    def failed(self):
        return self.sort(key='Failed', value=True,
                         sort_on='Timestamp', desc=True)

    def successful(self):
        return self.sort(key='Failed', value=False,
                         sort_on='Timestamp', desc=True)

    def by_time(self, wf):
        return self.sort(key='WorkflowDefName', value=wf,
                    sort_on='Timestamp', desc=True)

class Job(Model):
    pass
