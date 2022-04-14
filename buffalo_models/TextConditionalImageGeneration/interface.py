from buffalo_models import ModelClass

class TextConditionalImageGeneration(ModelClass):
    def __init__(self, model_path):
        raise NotImplementedError

    def run(self, prompt, seed=123):
        raise NotImplementedError
