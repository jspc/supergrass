import os

from supergrass import db, mio, models

class App:
    LOCAL=os.environ.get('LOCAL', False) == 'TRUE'
    WORKFLOW_TABLE='Workflows'
    JOB_TABLE='Jobs'

    def __init__(self, **kwargs):
        mio_url = kwargs.get('mio')
        username = kwargs.get('username')
        password = kwargs.get('password')

        mio_obj = mio.Mio(username=username, password=password, url=mio_url)

        wf_db_obj = db.DB(local=self.LOCAL, table=self.WORKFLOW_TABLE)
        job_db_obj = db.DB(local=self.LOCAL, table=self.JOB_TABLE)

        self.workflows = models.Workflow(db=wf_db_obj, mio=mio_obj)
        self.jobs = models.Workflow(db=job_db_obj, mio=mio_obj)
