"""
Display GitLab server info

Usage:
    gitlab-server-info config.yml
"""
import os

import click
import pandas as pd

from . import config as cfg
from . import connection as glc

def inspect_project(project):
    headers = (
        'name', 'id', 'path_with_namespace', 'owner_is_group',
        'owner_is_user', 'storage_size', 'lfs_objects_size', 'job_artifacts_size',
        'repo_size',
    )
    values = [
        project.name,
        project.id,
        project.path_with_namespace,
        project.namespace['kind'] == 'group',
        project.namespace['kind'] == 'user',
    ]
    if hasattr(project, 'statistics'):
        values += [
            project.statistics['storage_size'],
            project.statistics['lfs_objects_size'],
            project.statistics['job_artifacts_size'],
            project.statistics['storage_size'] - project.statistics['job_artifacts_size'],
        ]
    else:
        values += [0, 0, 0]
    return headers, tuple(values)


def get_project_data(projects):
    projects = sorted(projects, key=lambda p: p.name)
    headers, _ = inspect_project(projects[0])

    results = [inspect_project(p)[1] for p in projects]
    df = pd.DataFrame.from_records(results, columns=headers)
    return df

@click.command(__doc__)
@click.argument('config_file', type=click.Path(exists=True), required=False)
@click.option('--output-file', type=click.Path(), default='repos.csv')
@click.option('--server', type=click.Choice(['source', 'destination']), default='source')
def cli(config_file, output_file, server):
    config = cfg.load(config_file)
    df = None
    gitlab_instance = config.servers[server].url
    gitlab_token = config.servers[server].auth_token

    print('Gathering info from', gitlab_instance)
    if not os.path.exists(output_file):
        gl = glc.connect(gitlab_instance, gitlab_token)
        projects = []
        groups = config.migrate.groups.keys()

        if groups:
            projects += glc.projects(gl, groups=groups, statistics=True)
        user = config.migrate.user
        if user:
            names = None
            if user['projects'] != '--all--':
                names = user['projects']
            projects += glc.user_projects(gl, names=names, statistics=True)

        df = get_project_data(projects)
        df.to_csv(output_file)
    else:
        df = pd.read_csv(output_file, index_col=0)

    totalSpaceUsed = df['storage_size'].sum() / 1024. / 1014.

    print('Found', len(df), 'repositories using {:.1f} MB of space.'.format(totalSpaceUsed))

    # df['user'] = df['path_with_namespace'].str.split('/').apply(lambda x: x[0])
    # user_repos = df[df.owner_is_user]
    # by_user = user_repos.groupby('user')
