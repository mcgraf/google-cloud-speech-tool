import os
import yaml
from google.cloud import storage
from google.cloud import speech

_cwd = os.getcwd()


class Config(dict):
    def __init__(self, config, filename):
        super(Config, self).__init__(config)
        self.filename = filename
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = \
            self.get_resource_path(self.google_cloud['credentials_file'])

    def __getattr__(self, item):
        return self.get(item, None)

    def get_resource_path(self, rel_path):
        if rel_path.startswith('/'):
            return rel_path
        return os.path.join(os.path.dirname(self.filename), rel_path)

    def get_bucket(self):
        return storage.Client().get_bucket(self.google_cloud['storage']['bucket'])

    def get_bucket_source_uri(self, remote_path):
        return '/'.join(['gs:/', self.google_cloud['storage']['bucket'], remote_path])

    def get_speech(self):
        return speech.Client()


def load(filename):
    if not filename.startswith('/'):
        filename = os.path.join(_cwd, filename)
    with open(filename) as f:
        return Config(yaml.load(f), filename)
