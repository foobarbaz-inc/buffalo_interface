from buffalo_models import build_model_from_config
from pychain_utils.data_utils import torch_img_to_arweave

config_path = 'https://arweave.net/1OEFoIevhpO3VZt2YJt14beE4mJSA5Gl0zHRChtWBDM'

model = build_model_from_config(0, config_path)
img_tensor = model.run("New York City, oil on canvas", seed=123)
output_arweave_path = torch_img_to_arweave(img_tensor)
print(output_arweave_path)
