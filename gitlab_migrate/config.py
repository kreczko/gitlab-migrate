
import yaml

def load(config_file):
    with open(config_file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return Config(**config)

class Config(object):
    __slots__ = ['servers', 'migrate']
    def __init__(self, servers, migrate):
        self.servers = servers
        self.migrate = migrate
