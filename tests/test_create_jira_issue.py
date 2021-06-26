import unittest
import requests
import requests_mock
import io
import sys
import create_jira_issue.logic
from mock import patch


class CreateJiraIssueTests(unittest.TestCase):
    def test_read_settings__success(self):
        result = create_jira_issue.logic.read_settings("./resources/settings.yml")
        self.assertIsNotNone(self, result)
        self.assertEqual(result['jira_url'], 'https://your.jira.url.com')
        self.assertEqual(result['password'], 'your_pass')
        self.assertEqual(result['project'], 'PROJECT')
        self.assertEqual(result['issuetype_id'], 3)
        self.assertEqual(result['priority_id'], 4)
        self.assertEqual(result['assignee'], 'assignee_login')
        self.assertEqual(result['reporter'], 'your_login')
        self.assertEqual(result['board_id'], 20801)
        self.assertEqual(result['labels'], ['new'])

    def test_read_settings__fail(self):
        with self.assertRaises(SystemExit):
            create_jira_issue.logic.read_settings("./resources/non_existent.yml")

    def test_get_create_issue_data(self):
        settings = {
            'issuetype_id': 3,
            'project': 'PROJECT',
            'priority_id': 4,
            'assignee': 'assignee',
            'reporter': 'reporter',
            'labels': ['new']
        }
        data = create_jira_issue.logic.get_create_issue_data(settings, 'This is summary', 'This is description')
        self.assertIsNotNone(self, data)
        fields = data['fields']
        self.assertEqual(fields['issuetype'], {'id': '3'})
        self.assertEqual(fields['project'], {'key': 'PROJECT'})
        self.assertEqual(fields['summary'], 'This is summary')
        self.assertEqual(fields['priority'], {'id': '4'})
        self.assertEqual(fields['assignee'], {'name': 'assignee'})
        self.assertEqual(fields['reporter'], {'name': 'reporter'})
        self.assertEqual(fields['description'], 'This is description')
        self.assertEqual(fields['labels'], ['new'])

    def test_process_create_task_response__success(self):
        response = requests.Response()
        response.status_code = 201
        response._content = b'{ "key": "PROJECT-999" }'
        captured_output = io.StringIO()
        sys.stdout = captured_output
        issue_key = create_jira_issue.logic.process_create_task_response(response, "www.jira.com/")
        self.assertEqual(issue_key, "PROJECT-999")
        self.assertEqual(" ".join(captured_output.getvalue().split()),
                         "issue with key: PROJECT-999 has been created www.jira.com/browse/PROJECT-999")

    def test_process_create_task_response__fail(self):
        response = requests.Response()
        response.status_code = 500
        response._content = b'{ "message": "error" }'
        captured_output = io.StringIO()
        sys.stdout = captured_output
        create_jira_issue.logic.process_create_task_response(response, "www.jira.com/")
        self.assertEqual(" ".join(captured_output.getvalue().split()),
                         "error creating jira issue! Response is {'message': 'error'} (500)")

    def test_get_active_sprint__success(self):
        settings = {
            'jira_url': 'www.jira.com/',
            'board_id': 12187,
            'login': 'login',
            'password': 'password'
        }
        with requests_mock.Mocker() as m:
            m.get("https://www.jira.com/rest/agile/1.0/board/12187/sprint?state=active",
                  status_code=200,
                  text="{\"values\":[{\"id\":1111}]}")
            sprint_id = create_jira_issue.logic.get_active_sprint(settings)
            self.assertEqual(1111, sprint_id)

    def test_get_active_sprint__fail(self):
        settings = {
            'jira_url': 'www.jira.com/',
            'board_id': 12187,
            'login': 'login',
            'password': 'password'
        }
        with requests_mock.Mocker() as m:
            captured_output = io.StringIO()
            sys.stdout = captured_output
            m.get("https://www.jira.com/rest/agile/1.0/board/12187/sprint?state=active",
                  status_code=500,
                  text="{\"reason\": \"error\"}")
            create_jira_issue.logic.get_active_sprint(settings)
            self.assertEqual(" ".join(captured_output.getvalue().split()),
                             "error getting active sprint! Response is {'reason': 'error'} (500)")

    @patch('create_jira_issue.logic.get_active_sprint')
    @requests_mock.Mocker()
    def test_add_to_sprint__success(self, mock_get_active_sprint, request_mock):
        mock_get_active_sprint.return_value = 9999
        settings = {
            'jira_url': 'www.jira.com/',
            'board_id': 12187,
            'login': 'login',
            'password': 'password'
        }
        captured_output = io.StringIO()
        sys.stdout = captured_output
        request_mock.post("https://www.jira.com/rest/agile/1.0/sprint/9999/issue", status_code=204)
        create_jira_issue.logic.add_to_sprint('PROJECT-999', settings)
        self.assertEqual(" ".join(captured_output.getvalue().split()),
                         "putting issue PROJECT-999 to sprint is successful!")

    @patch('create_jira_issue.logic.get_active_sprint')
    @requests_mock.Mocker()
    def test_add_to_sprint__error(self, mock_get_active_sprint, request_mock):
        mock_get_active_sprint.return_value = 9999
        settings = {
            'jira_url': 'www.jira.com/',
            'board_id': 12187,
            'login': 'login',
            'password': 'password'
        }
        captured_output = io.StringIO()
        sys.stdout = captured_output
        request_mock.post("https://www.jira.com/rest/agile/1.0/sprint/9999/issue", status_code=500)
        create_jira_issue.logic.add_to_sprint('PROJECT-999', settings)
        self.assertEqual(" ".join(captured_output.getvalue().split()),
                         "putting issue PROJECT-999 to sprint is NOT successful!")

    def prepare_create_issue(self,
                             mock_process_create_task_response,
                             mock_get_create_issue_data,
                             mock_read_settings,
                             request_mock):
        mock_read_settings.return_value = {
            'jira_url': 'www.jira.com/',
            'login': 'login',
            'password': 'password'
        }
        mock_get_create_issue_data.return_value = {
            'fields': {
                'some_field_key': 'some_field_value'
            }
        }
        request_mock.post('https://www.jira.com/rest/api/2/issue', status_code=201, text='{}')
        mock_process_create_task_response.return_value = 'PROJECT-9999'

    @patch('create_jira_issue.logic.read_settings')
    @patch('create_jira_issue.logic.get_create_issue_data')
    @patch('create_jira_issue.logic.process_create_task_response')
    @requests_mock.Mocker()
    def test_create_jira_issue(self,
                               mock_process_create_task_response,
                               mock_get_create_issue_data,
                               mock_read_settings,
                               request_mock):
        self.prepare_create_issue(mock_process_create_task_response,
                                  mock_get_create_issue_data,
                                  mock_read_settings,
                                  request_mock)
        create_jira_issue.logic.create_jira_issue('summary', 'descr', '/settings.yml', False)

    @requests_mock.Mocker()
    @patch('create_jira_issue.logic.add_to_sprint')
    @patch('create_jira_issue.logic.read_settings')
    @patch('create_jira_issue.logic.get_create_issue_data')
    @patch('create_jira_issue.logic.process_create_task_response')
    def test_create_jira_issue__add_to_sprint(self,
                                              request_mock,
                                              mock_process_create_task_response,
                                              mock_get_create_issue_data,
                                              mock_read_settings,
                                              *_):
        self.prepare_create_issue(mock_process_create_task_response,
                                  mock_get_create_issue_data,
                                  mock_read_settings,
                                  request_mock)
        create_jira_issue.logic.create_jira_issue('summary', 'descr', '/settings.yml', False)


if __name__ == '__main__':
    unittest.main()
