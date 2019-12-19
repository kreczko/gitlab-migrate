import gitlab

GL_CONN = None

def connect(gitlab_instance, gitlab_token):
    global GL_CONN
    if GL_CONN is None:
        GL_CONN = gitlab.Gitlab(gitlab_instance, private_token=gitlab_token)
        GL_CONN.auth()

    return GL_CONN

def _projects_from_group(connection, group, statistics=True):
    gl = connection
    projects = []
    results = gl.groups.list(search=group, statistics=statistics)
    if len(results) > 1:
        print('Found more than one group matching "{}" - aborting'.format(search_for))
        return 1
    gl_group = results[0]
    # this never gives statistics
    projects_tmp = gl_group.projects.list(all=True, include_subgroups=True)
    # for each project, download full info
    for p in projects_tmp:
        projects.append(gl.projects.get(p.id, statistics=statistics))
    return projects

def _project_by_name(connection, name, statistics=True):
    gl = connection
    project = None
    results = gl.projects.list(search=name, statistics=statistics)
    if len(results) > 1:
        print('Found more than one group matching "{}" - aborting'.format(search_for))
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
            results = [_projects_by_name(gl, name, statistics) for name in names]
        else:
            results = gl.projects.list(all=True, statistics=statistics)
    return results
