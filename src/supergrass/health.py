import datetime
import re

class HealthCheck:
    def __init__(self):
        self.name = ''
        self.ok = False
        self.severity = 2
        self.impact = ''
        self.summary = ''
        self.panic_guide = ''
        self.check_output = ''
        self.updated = datetime.datetime.now().isoformat()

    def _normalised_name(self):
        return re.sub('[^0-9a-zA-Z]+', '-', self.name).lower()

    def dump(self):
        return {'id': self._normalised_name(),
                'name': self.name,
                'ok': self.ok,
                'severity': self.severity,
                'businessImpact': self.impact,
                'technicalSummary': self.summary,
                'panicGuide': self.panic_guide,
                'checkOutput': self.check_output,
                'lastUpdated': self.updated}

class HealthChecks:
    def __init__(self, checks=[]):
        self.schema = 1
        self.system_code = ''
        self.name = ''
        self.description = ''
        self.checks = checks

    def dump(self):
        return {'schemaVersion': self.schema,
                'systemCode': self.system_code,
                'name': self.name,
                'description': self.description,
                'checks': [ c.dump() for c in self.checks ]}
