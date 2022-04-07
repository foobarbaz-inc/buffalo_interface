from buffalo_models import ModelClass

class UnconditionalImageGeneration(ModelClass):
    def __init__(self, model_path):
        raise NotImplementedError

    def run(self, seed=123):
        raise NotImplementedError
