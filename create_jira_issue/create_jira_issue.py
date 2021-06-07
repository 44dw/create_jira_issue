import requests
import argparse
import yaml
import json
from urllib3.exceptions import InsecureRequestWarning
from url_normalize import url_normalize

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

TASK_ISSUE_TYPE = '3'


def populate_with_args(parser):
    parser.add_argument("-s", help="issue summary", type=str, required=True)
    parser.add_argument("-d", help="issue description", type=str, default="")
    parser.add_argument("-n", help="path to settings file in yaml", type=str, default="settings.yml")
    parser.add_argument("--sprint", help="put issue in current sprint", action="store_true")
    return parser


def read_settings(settings_path="settings.yml"):
    with open(settings_path, 'r') as settings_file:
        return yaml.full_load(settings_file)


def get_create_issue_data(settings, summary, description):
    return {
        'fields': {
            'issuetype': {'id': '3'},
            'project': {'key': settings['project']},
            'summary': summary,
            'priority': {'id': str(settings['priority_id'])},
            'assignee': {'name': settings['assignee']},
            'reporter': {'name': settings['reporter']},
            'description': description,
            'labels': settings['labels']
        }
    }


def process_create_task_response(response, jira_url):
    if response.status_code != 201:
        print(f'error creating jira issue! Response is {response.json()} ({response.status_code})')
    else:
        body = response.json()
        issue_key = body['key']
        issue_jira_url = f"{jira_url}browse/{issue_key}"
        print(f"issue with key: {issue_key} has been created\n\n{issue_jira_url}\n\n")
        return issue_key


def get_active_sprint(settings):
    get_sprint_id_url = f"{settings['jira_url']}rest/agile/1.0/board/{settings['board_id']}/sprint?state=active"
    response = requests.get(url_normalize(get_sprint_id_url),
                            headers={'Content-Type': 'application/json'},
                            auth=(settings['login'], settings['password']),
                            verify=False)
    if response.status_code != 201:
        print(f'error getting active sprint! Response is {response.json()} ({response.status_code})')
    else:
        body = response.json()
        sprint_id = body['values'][0]['id']
        return sprint_id


def add_to_sprint(issue_key, settings):
    sprint_id = get_active_sprint(settings)
    add_to_sprint_url = f"{settings['jira_url']}/rest/agile/1.0/sprint/{sprint_id}/issue"
    data = {
        'issues': [issue_key]
    }
    response = requests.post(url_normalize(add_to_sprint_url),
                             data=json.dumps(data),
                             headers={'Content-Type': 'application/json'},
                             auth=(settings['login'], settings['password']),
                             verify=False)
    if response.status_code == 204:
        print(f"putting issue {issue_key} to sprint is successful!")
    else:
        print(f"putting issue {issue_key} to sprint is NOT successful! Response message is {response.reason}")


def create_jira_issue(summary, description, settings_path, to_sprint):
    settings = read_settings(settings_path)
    create_issue_url = f"{settings['jira_url']}/rest/api/2/issue"
    data = get_create_issue_data(settings, summary, description)
    jsoned_data = json.dumps(data)
    response = requests.post(url_normalize(create_issue_url),
                             data=jsoned_data,
                             headers={'Content-Type': 'application/json'},
                             auth=(settings['login'], settings['password']),
                             verify=False)
    issue_key = process_create_task_response(response, settings['jira_url'])
    if bool(issue_key) & to_sprint:
        add_to_sprint(issue_key, settings)


def main():
    parser = populate_with_args(argparse.ArgumentParser())
    args = parser.parse_args()
    create_jira_issue(args.s, args.d, args.n, args.sprint)


if __name__ == '__main__':
    main()
