import torch
from torch import nn
from torch.nn import functional as F
from torchvision import transforms
from torchvision.transforms import functional as TF
import numpy as np
import json

from pychain_utils.bundlr import download
from .interface import TextConditionalImageGeneration

import clip
from .diffusion import get_model, sampling, utils

def resize_and_center_crop(image, size):
    fac = max(size[0] / image.size[0], size[1] / image.size[1])
    image = image.resize((int(fac * image.size[0]), int(fac * image.size[1])), Image.LANCZOS)
    return TF.center_crop(image, size[::-1])


class CLIPGuidedDiffusion(TextConditionalImageGeneration):
    contributer = "0xEE5dF02b524215242e653b67Ec471FAB2491e21D"

    def __init__(self,
                 weights_path="",
                 eta=0,
                 method='plms',
                 size=None,
                 upscale=1,
                 steps=50,
                 prompt_weight=5,
                 device='cuda'):
        images = []
        self.batch_size = 1
        init = None
        model_name = 'cc12m_1_cfg'
        self.n = 1
        self.eta = eta
        self.method = method
        self.upscale = upscale
        self.steps = steps
        self.prompt_weight = prompt_weight

        # Download weights and load into model
        self.device = torch.device(device)
        print('Using device:', self.device)

        self.model = get_model(model_name)()
        _, self.side_y, self.side_x = self.model.shape
        if size:
            self.side_x, self.side_y = size

        local_weights_path = download(weights_path)
        self.model.load_state_dict(torch.load(local_weights_path, map_location='cpu'))

        if self.device.type == 'cuda':
            self.model = self.model.half()
        self.model = self.model.to(self.device).eval().requires_grad_(False)

        clip_model_name = self.model.clip_model \
                if hasattr(self.model, 'clip_model') else 'ViT-B/16'
        self.clip_model = clip.load(clip_model_name, jit=False, device=self.device)[0]
        self.clip_model.eval().requires_grad_(False)

    def step(self, x, steps, target_embeds, weights):
        def cfg_model_fn(x, t):
            n = x.shape[0]
            n_conds = len(target_embeds)
            x_in = x.repeat([n_conds, 1, 1, 1])
            t_in = t.repeat([n_conds])
            clip_embed_in = torch.cat([*target_embeds]).repeat_interleave(n, 0)
            vs = self.model(x_in, t_in, clip_embed_in).view([n_conds, n, *x.shape[1:]])
            v = vs.mul(weights[:, None, None, None, None]).sum(0)
            return v

        if self.method == 'ddpm':
            return sampling.sample(cfg_model_fn, x, steps, 1., {})
        if self.method == 'ddim':
            return sampling.sample(cfg_model_fn, x, steps, self.eta, {})
        if self.method == 'prk':
            return sampling.prk_sample(cfg_model_fn, x, steps, {})
        if self.method == 'plms':
            return sampling.plms_sample(cfg_model_fn, x, steps, {})
        if self.method == 'pie':
            return sampling.pie_sample(cfg_model_fn, x, steps, {})
        if self.method == 'plms2':
            return sampling.plms2_sample(cfg_model_fn, x, steps, {})
        assert False

    @torch.no_grad()
    def run(self, prompt, seed=123):
        torch.manual_seed(seed)
        np.random.seed(seed)
        
        # get target embeddings
        zero_embed = torch.zeros([1, self.clip_model.visual.output_dim], device=self.device)
        prompt_embed = self.clip_model.encode_text(clip.tokenize(prompt).to(self.device)).float()
        target_embeds = [zero_embed, prompt_embed]
        weights = [self.prompt_weight]
        weights = torch.tensor([1 - sum(weights), *weights], device=self.device)
        
        # perform diffusion
        x = torch.randn([self.n, 3, self.side_y, self.side_x], device=self.device)
        t = torch.linspace(1, 0, self.steps + 1, device=self.device)[:-1]
        steps = utils.get_spliced_ddpm_cosine_schedule(t)

        # run
        assert self.n == 1
        outs = self.step(x, steps, target_embeds, weights)

        # optionally resize image
        if self.upscale > 1:
            outs = TF.resize(outs,
                             (self.side_y*self.upscale, self.side_x*self.upscale),
                             interpolation=TF.InterpolationMode.BICUBIC)

        # outs is -1 to 1
        outs = (outs + 1) / 2

        return outs[0]

    @classmethod
    def test(cls):
        # For a few fixed model weights, verify that model output is within a tolerance
        # of expected
        pass
