from ..interface import ModelClass, TextDataType, ImageDataType

class TextConditionalImageGeneration(ModelClass):
    input_data_type = TextDataType
    output_data_type = ImageDataType

    def __init__(self, model_path):
        raise NotImplementedError

    def run(self, prompt, seed=123):
        """
            Outputs an image tensor of size [B, C, H, W] scaled to [0, 1)
        """
        raise NotImplementedError
