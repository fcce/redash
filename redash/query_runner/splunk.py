# -*- coding: UTF-8

from redash.query_runner import BaseQueryRunner, register, guess_type, TYPE_STRING
import json
from redash.utils import json_dumps

try:
    import splunklib.client as client
    import splunklib.results as results
    enabled = True
except ImportError:
    enabled = False


class Splunk(BaseQueryRunner):

    noop_query = "* | head 1"

    def run_query(self, query, user):
        HOST = self.configuration['host']
        PORT = self.configuration['port']
        USERNAME = self.configuration['username']
        PASSWORD = self.configuration['password']
        APP = self.configuration['app']

        search_query = '''search %s ''' % (query)

        # start_time = "2019-04-01"
        # end_time = "2020-05-31"
        columns = []
        rows = []
        json_data = []
        error = None
        try:
            service = client.connect(host=HOST,
                                     port=PORT,
                                     username=USERNAME,
                                     password=PASSWORD,
                                     app=APP)

            # search_kwargs = {
            #     'earliest_time': start_time + 'T00:00:00.000+08:00',
            #     'latest_time': end_time + 'T00:00:00.000+08:00'
            # }
            search_kwargs = {}

            job = service.jobs.oneshot(search_query, **search_kwargs)
            for result in results.ResultsReader(job):
                if len(columns) == 0:
                    for name in result.keys():
                        column = {
                            'friendly_name': name,
                            'name': name,
                            'type': TYPE_STRING
                        }
                        columns.append(column)
                    rows.append(result)
                else:
                    rows.append(result)

            data = {'columns': columns, 'rows': rows}
            json_data = json_dumps(data)
        except Exception as e:
            error = str(e)

        return json_data, error

    @classmethod
    def enabled(cls):
        return enabled

    @classmethod
    def name(cls):
        return "Splunk"

    @classmethod
    def annotate_query(cls):
        return False

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "default": "127.0.0.1"
                },
                "port": {
                    "type": "number",
                    "default": 8089
                },
                "username": {
                    "type": "string",
                    "default": "admin"
                },
                "password": {
                    "type": "string",
                    "default": "changeme"
                },
                "app": {
                    "type": "string",
                    "default": "search"
                }
            },
            "required": ["host", "port", "username", "password", "app"],
            "secret": ["password"]
        }


register(Splunk)
