import gitlab
import os
import time

def connect(gitlab_instance, gitlab_token, api_version=4, ssl_verify=True):
    GL_CONN = gitlab.Gitlab(
        gitlab_instance, private_token=gitlab_token, api_version=api_version, ssl_verify=ssl_verify
    )
    GL_CONN.auth()

    return GL_CONN

def _projects_from_group(connection, group, statistics=True):
    gl = connection
    projects = []
    results = gl.groups.list(search=group, statistics=statistics, include_subgroups=True)
    if len(results) > 1:
        groups = [(g.id, g.name) for g in results]
        msg = 'Found more than one group matching "{}" [{}] - trying to resolve'.format(group, groups)
        print(msg)
        # mimick exact search
        exact_match = None
        for g in results:
            if g.name == group:
                exact_match = [g]
                break
        results = exact_match
    if not results:
        msg = 'Unable to find group matching "{}" - aborting'.format(group)
        raise NameError(msg)
    gl_group = results[0]
    # this never gives statistics
    projects_tmp = gl_group.projects.list(all=True, include_subgroups=True)
    # for each project, download full info
    for p in projects_tmp:
        projects.append(gl.projects.get(p.id, statistics=statistics))
    return projects

def _project_by_name(connection, name, statistics=True):
    gl = connection
    results = gl.projects.list(search=name, statistics=statistics)
    if len(results) > 1:
        print('Found more than one group matching "{}" - aborting'.format(name))
        return 1
    return results[0]

def projects(connection, names=None, groups=None, statistics=True):
    gl = connection
    results = []
    if groups is not None and not isinstance(groups, (list, tuple)):
        groups = [groups]
    if groups:
        for g in groups:
            results += _projects_from_group(gl, g, statistics)
        if names:
            results = list(filter(lambda x: x.name in names, results))
    else:
        if names:
            results = [_project_by_name(gl, name, statistics) for name in names]
        else:
            results = gl.projects.list(all=True, statistics=statistics)
    return results

def user_projects(connection, names=None, statistics=True):
    current_user = connection.users.get(connection.user.id)
    projects_tmp = current_user.projects.list(statistics=statistics)
    projects = []
    for p in projects_tmp:
        projects.append(connection.projects.get(p.id, statistics=statistics))
    if names:
        projects = list(filter(lambda x: x.name in names, projects))
    return projects

def export_project(project):
    print('Starting export process for project', project.name)
    export_file = '/tmp/{}.tgz'.format(project.name)
    if os.path.exists(export_file):
        print('Export file for project {} already exists: {}'.format(project.name, export_file))
        return export_file
    export = project.exports.create({})
    export.refresh()
    while export.export_status != 'finished':
        time.sleep(1)
        export.refresh()
    with open(export_file, 'wb') as f:
        export.download(streamed=True, action=f.write)
    return export_file

def find_group(connection, group, statistics=False):
    if '/' in group:
        tokens = group.split('/')
        current_group = None
        base_group = None
        for search_for in tokens:
            if current_group is None:
                current_group = connection.groups.list(
                    search=search_for, statistics=statistics, include_subgroups=True
                )[0]
                base_group = current_group
            else:
                current_group = base_group.subgroups.list(
                    search=search_for, statistics=statistics, include_subgroups=True
                )[0]
                base_group = connection.groups.get(current_group.id)
        # full API access only through groups.get
        current_group = connection.groups.get(current_group.id)
        return current_group
    else:
        current_group = connection.groups.list(search=group, statistics=statistics)[0]
        return current_group


def import_project(connection, project, destination):
    # print(dir(destination))
    # return
    export_file = export_project(project)
    print('Importing', project.name, 'to', destination.name)

    # new_project = connection.projects.create({'name':project.name, 'namespace_id': destination.id})
    try:
        with open(export_file, 'rb') as f:
            output = None
            if type(destination).__name__ == 'User':
                output = connection.projects.import_project(f, path=project.path, override=True)
            else:
                output = connection.projects.import_project(
                    f, path=project.path, namespace=destination.id, overwrite=True,
                )
            print(' >>>> Import in progress')
            project_import = connection.projects.get(output['id'], lazy=True).imports.get()
            while project_import.import_status not in ['finished', 'failed']:
                print(project_import.import_status)
                time.sleep(10)
                project_import.refresh()
            if project_import.import_status == 'failed':
                # TODO: remove failed project
                print('Unable to import project:', project_import.import_error)
    except gitlab.exceptions.GitlabHttpError as e:
        print(' >>>> Unable to import project', project.name, ':', e)
        return False
    return True
