import logging
import taskcluster
import os
import yaml

logger = logging.getLogger(__name__)

TASKCLUSTER_DEFAULT_URL = 'https://taskcluster.net'


class Configuration(object):
    config = {}

    def __init__(self, args):
        if args.secret:
            self.load_secret(args.secret)
        elif args.config:
            self.load_config(args.config)
        else:
            logger.warn('No configuration available')

    def __getattr__(self, key):
        if key in self.config:
            return self.config[key]
        raise KeyError

    def load_secret(self, name):
        options = taskcluster.optionsFromEnvironment()
        proxy_url = os.environ.get('TASKCLUSTER_PROXY_URL')

        if proxy_url is not None:
            # Always use proxy url when available
            options['rootUrl'] = proxy_url

        if 'rootUrl' not in options:
            # Always have a value in root url
            options['rootUrl'] = TASKCLUSTER_DEFAULT_URL

        secrets = taskcluster.Secrets(options)
        logging.info('Loading Taskcluster secret {}'.format(name))
        payload = secrets.get(name)
        assert 'secret' in payload, 'Missing secret value'
        self.config = payload['secret']

    def load_config(self, fileobj):
        self.config = yaml.safe_load(fileobj)
        assert isinstance(self.config, dict), 'Invalid YAML structure'

    def has_docker_auth(self):
        docker = self.config.get('docker')
        if docker is None:
            return False
        return 'repository' in docker \
               and 'username' in docker \
               and 'password' in docker