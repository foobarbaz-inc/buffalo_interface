import torch
import numpy as np

from .interface import TextConditionalImageGeneration
from pychain_utils.bundlr import download

class CLIPGuidedDiffusion(TextConditionalImageGeneration):
    contributer = "0xEE5dF02b524215242e653b67Ec471FAB2491e21D"

    def __init__(self, config_path, device='cuda'):
        # Download weights and load into model
        local_config_path = download(config_path)
        with open(local_config_path, 'r') as f:
            config = json.load(f)
        print(config)

    def run(self, prompt, seed=123):
        torch.manual_seed(seed)
        np.random.seed(seed)
        out = self.model()

    @classmethod
    def test(cls):
        # For a few fixed model weights, verify that model output is within a tolerance
        # of expected
        pass
