from flask import abort, Flask, request
from github_webhook import Webhook
import os
import sys
from ipaddress import ip_address, ip_network
from functools import wraps
import requests
from os.path import join, dirname

app = Flask(__name__)
if not os.environ.get('GITHUB_TOKEN'):
    print('GITHUB_TOKEN not found')
    sys.exit()
elif not os.environ.get('CIRCLECI_TOKEN'):
    print('CIRCLECI_TOKEN not found')
    sys.exit()
webhook = Webhook(app, endpoint='/postreceive')
Repos = ['tejasshekokar/learn-express']
# Branch = 'refs/heads/master'
Branch = 'refs/heads/staging'
MASTER_BRANCH = 'refs/heads/master'
@webhook.hook(event_type='push')
def on_push(data):
    print('Lamda Tiggered')
    param = ''
    if MASTER_BRANCH == data['ref']:
        param = {'run_tests': 'true', 'smoke_tests': 'false'}
    else:
        param = {'run_tests': 'false', 'smoke_tests': 'true'}
    payload = {
        'repo': data['repository']['full_name'],
        'branch': data['ref'],
        'param': param
    }
    print('Payload: %s' % (payload))
    source_event = {'type': 'push', 'branch': Branch}
    gh_url = 'https://api.github.com/repos/%s/pulls?head=tejasshekokar:%s' % (
        Repos[0], payload['branch'])
    headers = {
        'Authorization': 'token %s' % (os.environ.get('GITHUB_TOKEN'))
    }
    try:
        response = requests.request(
            "GET", gh_url, headers=headers, data=payload)
        PR_COUNT = 0
        source_event['has_PR'] = len(response.json()) == PR_COUNT
    except Exception as ex:
        print(ex.message)
    # if payload['repo'] in Repos and payload['branch'] == source_event['branch']:
    #     circleci_new_build(source_event, payload)                r#only build master branch cnfig
    if payload['repo'] in Repos and payload['branch'] != source_event['branch'] and source_event['has_PR']:
        circleci_new_build(source_event, payload)


def circleci_new_build(source_event, payload):
    worker_token = os.environ.get('CIRCLECI_TOKEN')
    worker_repo = payload['repo']
    worker_branch = payload['branch']
    worker_branch = worker_branch.replace("refs/heads/", "")
    worker_param_one = payload['param']['run_tests']
    worker_param_two = payload['param']['smoke_tests']
    headers = {'Content-Type': 'application/json',
               'Circle-Token': '%s' % worker_token}
    # data = '{"branch": "master"}'            #It will trigger only master branch jobs
    data = '{"branch": "%s","parameters": {"run_tests": %s,"smoke_tests":%s} }' % (
        worker_branch, worker_param_one, worker_param_two)
    print(data)
    api_url = 'https://circleci.com/api/v2/project/gh/' + worker_repo + '/pipeline'
    try:
        response = requests.post(
            api_url, headers=headers, data=data)
        print(response.status_code)
        return
    except Exception as ex:
        print(ex.message)


if __name__ == "__main__":
    print('app is running')
    app.run(host="0.0.0.0", port="5000", debug=True)
