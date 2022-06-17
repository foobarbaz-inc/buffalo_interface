from ..interface import ModelClass, TicTacToeInput, TicTacToeOutput

class RLAgent(ModelClass):
    input_data_type = TextDataType
    output_data_type = TextDataType

    def __init__(self, model_path):
        raise NotImplementedError

    def run(self, address, game_id, model_config, seed=123):
        """
            Outputs a move to play, given the game state
        """
        raise NotImplementedError
