import unittest
import requests
import io
import sys
import create_jira_issue.logic


class CreateJiraIssueTests(unittest.TestCase):
    def test_something(self):
        result = create_jira_issue.logic.to_test(2)
        self.assertEqual(result, 4)

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


if __name__ == '__main__':
    unittest.main()
