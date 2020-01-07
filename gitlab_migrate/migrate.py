"""Print scikit-validate version"""
import click
import sys

from . import __version__

from . import config as cfg
from . import connection as glc

def print_version(plain):
    if plain:
        click.echo(__version__)
    else:
        click.echo("gitlab-migrate version: {}".format(__version__))


def migration_instructions(conn_src, conn_dst, migrate):
    instructions = []
    user_projects = []
    groups = migrate.groups
    user = migrate.user
    for group, content in groups.items():
        names = None
        if content['projects'] != '--all--':
            names = content['projects']
        projects = glc.projects(conn_src, names=names, groups=[group], statistics=False)

        search_for = content['destination']
        destination = glc.find_group(conn_dst, search_for)

        if not destination:
            print('Unabled to find destination "{}" - aborting'.format(search_for))
            return instructions, user_projects
        for project in projects:
            instructions.append((project, destination))
    if user:
        names = None
        if user['projects'] != '--all--':
            names = user['projects']
        user_projects = glc.user_projects(conn_src, names=names, statistics=False)
    return instructions, user_projects


@click.command(help=__doc__)
@click.argument('config_file', type=click.Path(exists=True), required=False)
@click.option('--version', is_flag=True)
@click.option('--plain', is_flag=True)
@click.option('--noop', is_flag=True)
def cli(config_file, version, plain, noop):
    if version:
        print_version(plain)
        return 0
    config = cfg.load(config_file)

    src_server = config.servers['source']
    dst_server = config.servers['destination']

    gl_src = glc.connect(src_server.url, src_server.auth_token)
    gl_dst = glc.connect(dst_server.url, dst_server.auth_token)

    group_instructions, user_instructions = migration_instructions(gl_src, gl_dst, config.migrate)

    # print(group_instructions, user_instructions)
    for project, destination in group_instructions:
        print(' >> Going to migrate project {} to {}/{}/{}'.format(
            project.name, dst_server.url, destination.name, project.name
        )
        )
        if not noop:
            print(' >>>> Importing project', project)
            glc.import_project(gl_dst, project, destination)

    dst_user = gl_dst.users.get(gl_dst.user.id)
    for project in user_instructions:
        print(' >> Going to migrate project {} to {}/{}'.format(
            project.name, dst_server.url, gl_dst.user.username
        )
        )
        if not noop:
            print(' >>>> Importing project', project)
            glc.import_project(gl_dst, project, dst_user)
    # print(group_instructions, user_instructions)

    # projects = glc.projects(gl, groups=groups, statistics=True)

    # for project in projects:
    #     print(dir(project))
    #     break
    #     glc.export_project(project)
    if not group_instructions and not user_instructions:
        sys.exit(1)

    if noop:
        print('Running with "--noop" nothing to do!')
        return

    if click.confirm('Do you want to archive (mark as read-only, reversible) all exported projects?'):
        print(' >> Archiving (marking as read-only) all exported projects')
        for project, _ in group_instructions:
            print('Archiving', project.name)
            project.archive()
        for project in user_instructions:
            print('Archiving', project.name)
            project.archive()

    else:
        print('All done!')
