from supergrass import app, health
import json
import time
import os

class SupergrassReporter(app.App):
    def report(self):
        healthchecks = health.HealthChecks()
        healthchecks.system_code = 393
        healthchecks.name = 'Flex'
        healthchecks.description = 'FT video team workflow and publishing engine'
        healthchecks.checks = []

        for m in [self.failure_proportion(),
                  self.bytes_per_second_proportion('project-workflow'),
                  self.bytes_per_second_proportion('ingest-workflow'),
                  self.bytes_per_second_proportion('publish-workflow')]:
            healthchecks.checks.append( m )

        return healthchecks.dump()

    def failure_proportion(self):
        h = health.HealthCheck()
        h.name = 'Workflow Failure Rates'
        h.severity = 3
        h.impact = 'Videos will not be archived and/or published automatically'
        h.summary = 'Tests the proportion of failed workflows to successful workflows'
        h.panic_guide = 'N/a'

        totals = self.workflows_by_time(3600)
        if totals['failed'] == 0:
            h.ok = True
            if totals['success'] == 0:
                h.check_output = 'No workflows seem to have run.'
            else:
                h.check_output = 'All workflows succeeding.'
        else:
            if totals['success'] == 0:
                h.check_output = 'Every workflow is failing.'
                h.ok = False
            else:
                percentage = ( float(totals['failed']) / float(totals['success']) ) * 100
                if percentage > 10:
                    h.check_output = 'More than 10% of workflows have failed.'
                    h.ok = False
                else:
                    h.check_output = 'Less than 10% of workflows failed.'
                    h.ok = True
        h.check_output +=  " Succesful Workflow Runs: {}, Failed Workflow Runs: {}".format(totals['success'], totals['failed'])

        return h

    def bytes_per_second_proportion(self, wf):
        h = health.HealthCheck()
        h.name = 'Processing time per kb for workflow: {}'.format(wf)
        h.severity = 3
        h.impact = 'Waiting time for videos will be higher than expected'
        h.summary = 'Tests that workflows are being completed in a timely manner'
        h.panic_guide = 'N/a'
        h.ok = True

        all_workflows = self.workflows.by_time(wf)
        recent_workflows = self.workflows.time_period(all_workflows, length=3600)

        if len(all_workflows) == 0 or len(recent_workflows) == 0:
            h.check_output = 'Not enough data to determine whether workflows take too long.'
        else:
            all_bytes_per_second = self.bytes_per_second(all_workflows)
            recent_bytes_per_second = self.bytes_per_second(recent_workflows)

            diff = recent_bytes_per_second / all_bytes_per_second
            if diff < 0.85:
                h.ok = False
                h.check_output = 'Throughput has dropped to {}% of previous values'.format(diff*100)
        return h

    def workflows_by_time(self, check_period=3600):
        failed = self.workflows.failed()
        success = self.workflows.successful()

        return {'failed': len(self.workflows.time_period(failed, length=check_period)),
                'success': len(self.workflows.time_period(success, length=check_period))}

    def bytes_per_second(self, workflows):
        time = 0
        size = 0
        for wf in workflows:
            if wf['Failed'] == False:
                next
            time += wf['ProcessTime']
            size += wf['AssetSize']

        return float(size) / float(time)

def load(event, context):
    mio = event.get('mio', 'http://localhost:9898')
    username = event.get('username', 'masteruser')
    password = event.get('password', os.environ.get('MIO_PASSWORD'))

    sr = SupergrassReporter(mio=mio,
                            username=username,
                            password=password)
    return sr.report()

if __name__ == '__main__':
    print json.dumps(load({},{}), ensure_ascii=False)
