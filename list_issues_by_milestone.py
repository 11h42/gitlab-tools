from gitlab import Gitlab
from configparser import ConfigParser
import sys

__author__ = 'Cedric RICARD'

config = ConfigParser()
config.read_file(open('defaults.cfg'))


def connect_to_gitlab():
    gl = Gitlab(config.get('gitlab', 'url'), config.get('gitlab', 'key'))
    gl.auth()
    return gl


def list_issues(gl, project_name, state=None, group_by_milestone=True):
    tab = " " * 4
    gl_project_id = None
    gl_project = None

    for p in gl.Project(per_page=1000):
        # print(p.path_with_namespace)
        if p.path_with_namespace == project_name:
            gl_project_id = p.id
            gl_project = p
            break

    if gl_project:

        milestone_dict = {}
        labels = gl_project.Label(per_page=1000)
        milestones = gl_project.Milestone(per_page=1000)
        issues = gl_project.Issue(per_page=1000)
        for issue in issues:
            if state and issue.state == state:
                if group_by_milestone:
                    if issue.milestone:
                        milestone_dict.setdefault(issue.milestone.title, []).append(issue)
                else:
                    print(issue)

        if milestone_dict:
            for ms in milestones:
                print(ms.title)
                print("state: %s" % ms.state, "/ %d issues" % len(milestone_dict[ms.title]))
                print("expired at %s" % ms.due_date)
                print("details: ", ms.description)

                for issue in milestone_dict[ms.title]:
                    print(tab, "#%(id)d\t%(title)s" % issue.__dict__)
                print()


if __name__ == '__main__':
    # project_name = config.get('gitlab', 'project')
    project_name = sys.argv[1]
    issue_state = sys.argv[2]
    gl = connect_to_gitlab()
    list_issues(gl, project_name, state=issue_state)
