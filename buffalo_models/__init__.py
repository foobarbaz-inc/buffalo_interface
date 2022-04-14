import json

from .TextConditionalImageGeneration \
        import architectures as TextConditionalImageGeneration_architectures
from pychain_utils.bundlr import download

architecture_index = [
    TextConditionalImageGeneration_architectures
]
architecture_names = [[cls.__name__ for cls in architectures] \
                        for architectures in architecture_index]

def build_model_from_config(model_class_num, config_path):
    local_config_path = download(config_path)
    with open(local_config_path, 'r') as f:
        config = json.load(f)

    architecture_name = config['architecture']
    del config['architecture']

    architecture_idx = architecture_names[model_class_num].index(architecture_name)
    model_class = architecture_index[model_class_num][architecture_idx]
    return model_class(**config)
