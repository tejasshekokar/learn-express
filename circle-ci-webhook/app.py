from flask import abort, Flask, request
from github_webhook import Webhook
import os
import sys
from ipaddress import ip_address, ip_network
from functools import wraps
import requests
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
print('Inside app.py')
print(os.environ.get('CIRCLECI_TOKEN'))
if not os.environ.get('CIRCLECI_TOKEN'):
    print('Inside app.py')
    print('CIRCLECI_TOKEN is not set')
    sys.exit()
webhook = Webhook(app, endpoint='/postreceive')
Repos = ['tejasshekokar/learn-express']
Branch = ['refs/heads/master']
@webhook.hook(event_type='push')
def on_pull_request(data):
    print('Inside on_pull_request')
    print(data)
    payload = {
        'repo': data['repository']['full_name'],
        'branch': data['ref']
    }
    source_event = {'type': 'push', 'branch': Branch}
    if payload['repo'] in Repos and payload['branch'] in source_event['branch']:
        circleci_new_build(source_event, payload)


def circleci_new_build(source_event, payload):
    print('Inside circleci_new_build')
    print('Payload\n')
    print(payload)
    worker_token = os.environ.get('CIRCLECI_TOKEN')
    worker_repo = payload['repo']
    print(worker_token)
    headers = {'Content-Type': 'application/json',
               'Circle-Token': '%s' % worker_token}
    data = '{"branch": "master"}'
    # data = '{"branch": "%s"}' % (worker_branch)
    api_url = 'https://circleci.com/api/v2/project/gh/' + worker_repo + '/pipeline'
    print(api_url)
    try:
        response = requests.post(
            api_url, headers=headers, data=data)
        print(response.status_code)
        return
    except Exception as ex:
        print(ex.message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
