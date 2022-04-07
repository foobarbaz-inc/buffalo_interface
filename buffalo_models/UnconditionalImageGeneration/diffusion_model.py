import torch
import numpy as np

from .interface import UnconditionalImageGeneration

class DiffusionModel(UnconditionalImageGeneration):
    contributer = "0xEE5dF02b524215242e653b67Ec471FAB2491e21D"

    def __init__(self, model_path, device='cuda'):
        # Download weights and load into model
        pass

    def run(self, seed=123):
        torch.manual_seed(seed)
        np.random.seed(seed)
        out = self.model()

    @classmethod
    def test(cls):
        # For a few fixed model weights, verify that model output is within a tolerance
        # of expected
        pass
