#!/usr/bin/env python

from supergrass import app
import os

class SupergrassScheduler(app.App):

    def populate_workflows(self):
        for wf in self.workflows.get_all():
            if 'asset' in wf.keys():
                size = self.workflows.asset_size(wf['asset']['href'])
            else:
                size = 1

            diff = self.workflows.process_time(wf['start'], wf['end'])

            uuid = self.workflows.uuid(wf['id'])
            timestamp = self.workflows.timestamp(uuid)
            self.workflows.create({
                "UUID": uuid,
                "WorkflowID": wf["id"],
                "WorkflowDefName": wf["name"],
                "AssetSize": size,
                "ProcessTime": diff,
                "Complete": wf["running"] != True,
                "Failed": wf["status"] == "Failed",
                "Timestamp": timestamp
            })


def load(event, context):
    mio = event.get('mio', 'http://localhost:9898')
    username = event.get('username', 'masteruser')
    password = event.get('password', os.environ.get('MIO_PASSWORD'))

    ss = SupergrassScheduler(mio=mio,
                             username=username,
                             password=password)
    ss.populate_workflows()


if __name__ == '__main__':
    load({},{})
