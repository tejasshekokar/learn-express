from flask import abort, Flask, request
from github_webhook import Webhook
import os
import sys
from ipaddress import ip_address, ip_network
from functools import wraps
import requests
from os.path import join, dirname

app = Flask(__name__)
if not os.environ.get('CIRCLECI_TOKEN'):
    sys.exit()
webhook = Webhook(app, endpoint='/postreceive')
Repos = ['tejasshekokar/learn-express']
Branch = ['refs/heads/master']
@webhook.hook(event_type='push')
def on_pull_request(data):
    payload = {
        'repo': data['repository']['full_name'],
        'branch': data['ref']
    }
    source_event = {'type': 'push', 'branch': Branch}
    if payload['repo'] in Repos and payload['branch'] in source_event['branch']:
        circleci_new_build(source_event, payload)


def circleci_new_build(source_event, payload):
    worker_token = os.environ.get('CIRCLECI_TOKEN')
    worker_repo = payload['repo']
    headers = {'Content-Type': 'application/json',
               'Circle-Token': '%s' % worker_token}
    data = '{"branch": "master"}'
    # data = '{"branch": "%s"}' % (worker_branch)
    api_url = 'https://circleci.com/api/v2/project/gh/' + worker_repo + '/pipeline'
    try:
        response = requests.post(
            api_url, headers=headers, data=data)
        print(response.status_code)
        return
    except Exception as ex:
        print(ex.message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
