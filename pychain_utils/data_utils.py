import numpy as np
from PIL import Image
import io

from pychain_utils.bundlr import upload_data

def torch_img_to_arweave(img_tensor):
    # tensor is a [B, C, H, W] tensor scaled to [0, 1)
    img = img_tensor.clamp(0, 1).detach().cpu().numpy()
    img = (img*255).transpose(1, 2, 0).astype(np.uint8)
    img = Image.fromarray(img)
    output_bytes = io.BytesIO()
    img.save(output_bytes, format='JPEG', quality=95)
    output_location = upload_data(output_bytes.getvalue())
    return output_location
