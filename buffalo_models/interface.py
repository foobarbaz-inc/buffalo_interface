import torch

from typing import Any

from pychain_utils.data_utils import torch_img_to_arweave

class DataType:
    @classmethod
    def parse_input_data(input_str, input_data_location_type) -> Any:
        raise NotImplementedError

    @classmethod
    def format_output_data(output_tensor, output_data_location_type) -> str:
        raise NotImplementedError

class ImageDataType(DataType):
    @classmethod
    def parse_input_data(input_str, input_data_location_type) -> torch.Tensor:
        # Todo: actually implement
        raise NotImplementedError

    @classmethod
    def format_output_data(output_tensor, output_data_location_type) -> str:
        # always save the data as an image on arweave
        arweave_path = torch_img_to_arweave(output_tensor)
        if output_data_location_type != 0:
            raise NotImplementedError
        return arweave_path

class TextDataType(DataType):
    @classmethod
    def parse_input_data(input_str, input_data_location_type) -> str:
        if input_data_location_type != 2:
            raise NotImplementedError
        return input_str

    @classmethod
    def format_output_data(model_output, output_data_location_type) -> str:
        raise NotImplementedError

class ModelClass():
    input_data_type = DataType
    output_data_type = DataType

    def run(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def test(cls, *args, **kwargs):
        raise NotImplementedError

