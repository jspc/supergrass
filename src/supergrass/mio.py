import requests

class Mio:
    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.url = kwargs.get('url')

        self.headers = {'content-type': 'application/vnd.nativ.mio.v1+json'}

    def workflows(self, last):
        r = self.get( self.full_path('workflows') )

        if last:
            returner = []
            for wf in r['workflows']:
                if wf['id'] != last:
                    returner.append(wf)
            return returner

        return r['workflows']


    def full_path(self, basename):
        print basename
        return "/".join([self.url, basename])

    def get(self, href):
        try:
            r = requests.get(href,
                             auth=(self.username, self.password),
                             headers=self.headers)
            return r.json()
        except Exception, e:
            print e.message
            exit
