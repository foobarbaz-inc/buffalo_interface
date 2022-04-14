#import pathlib
#import os

#downloaded_config_dir = os.path.join(pathlib.Path(__file__).resolve().parent,
#                                     'downloaded_configs')

class ModelClass():
    def run(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def test(cls, *args, **kwargs):
        raise NotImplementedError


