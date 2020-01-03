
import yaml

def load(config_file):
    with open(config_file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return Config(**config)

class Config(object):
    __slots__ = ['servers', 'migrate']

    def __init__(self, servers, migrate):
        self.servers = {name: Server(config) for name, config in servers.items()}
        self.migrate = Migrate(**migrate)

class Server(object):
    __slots__ = ['url', 'auth_token', 'api_version', 'group']

    def __init__(self, server):
        self.url = server['url']
        self.auth_token = server['auth_token']
        self.api_version = server['api_version'] if 'api_version' in server else 4
        self.group = server['group'] if 'group' in server else None


class Migrate(object):
    __slots__ = ['groups', 'user']

    def __init__(self, groups=None, user=None):
        self.groups = groups
        self.user = user
