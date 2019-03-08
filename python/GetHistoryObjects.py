#
# Fetch objects from 46elks API with optional filters
#
# Works with: sms, calls, mms, numbers, recordings, images and conversations
#
# Example:
#
# username = **********************************
# password = **********************************
# ensure = {'direction': 'outgoing'}
# for sms in GetHistoryObjects('sms', username, password, ensure):
#     print(sms)
#
import requests
import json
import datetime

class GetHistoryObjects:
    def __init__(self, endpoint, username, secret, ensure={}, start=datetime.datetime(year=3000, month=1, day=1), end=datetime.datetime(year=1970, month=1, day=1)):
        self.auth = (username, secret)
        self.objects = []
        self.start = start
        self.end = end
        self.has_more = True
        self.ensure = ensure
        self.endpoint = endpoint

    def get_objects(self, batchsize=100):
        p = {'limit': batchsize, 'start': self.start.strftime(
            "%Y-%m-%dT%H:%M:%S.%f"), 'end': self.end.strftime("%Y-%m-%dT%H:%M:%S.%f")}
        result = requests.get(
            "https://api.46elks.com/a1/{}".format(self.endpoint), params=p, auth=self.auth)
        if result.status_code != 200:
            raise Exception("API request failed with status {} and message: {}".format(
                result.status_code, result.text))

        data = json.loads(result.text)

        if 'next' in data:
            self.start = datetime.datetime.strptime(
                data['next'], '%Y-%m-%dT%H:%M:%S.%f')
        else:
            self.has_more = False
        self.objects = data['data']

    def __iter__(self):
        while True:
            if len(self.objects) == 0:
                if self.has_more:
                    self.get_objects()
                else:
                    return
            o = self.objects.pop()
            matches = True
            for key in self.ensure.keys():
                if key in o.keys():
                    if o[key] != self.ensure[key]:
                        matches = False
                        break
                else:
                    matches = False
                    break

            if matches:
                yield o
