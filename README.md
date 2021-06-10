# create_jira_issue

## Description
This command line app will help you to create issues from console
## Usage
```shell
cjiss -s "Your issue summary" -d "your issue description" -n "./settings.yml" --sprint
```
## Arguments
_s_ - [MANDATORY] issue summary

_d_ - issue description

_n_ - path to your issue settings in yaml (see below). If not provided, file with name "settings.yml" will be looked in
the current directory

_sprint_ - issue will be added to current sprint.

## Settings
```yaml
# fill this to make the script work

# your jira url
jira_url: https://your.jira.url.com
# login in jira
login: your_login
# pass in jira
password: your_pass
# project you work in
project: PROJECT
# jira issue type (epic, issue, etc) id
# 3 stands for issue
issuetype_id: 3
# default priority id
priority_id: 4
# default assignee
assignee: assignee_login
# default assignee
reporter: your_login
# your jira board id
board_id: 20801
# labels to add
labels:
  - new
```