import torch

from eth_abi import encode_abi
from typing import Any

from pychain_utils.data_utils import torch_img_to_arweave

class DataType:
    @classmethod
    def parse_input_data(cls, input_data_location_type, input_str) -> Any:
        raise NotImplementedError

    @classmethod
    def format_output_data(cls, output_data_location_type, output_tensor) -> str:
        raise NotImplementedError


class ImageDataType(DataType):
    @classmethod
    def parse_input_data(cls, input_data_location_type, input_str) -> torch.Tensor:
        # Todo: actually implement
        raise NotImplementedError

    @classmethod
    def format_output_data(cls, output_data_location_type, output_tensor) -> str:
        # always save the data as an image on arweave
        arweave_path = torch_img_to_arweave(output_tensor)
        if output_data_location_type != 0:
            raise NotImplementedError
        return encode_abi(['string'], [arweave_path])


class TextDataType(DataType):
    # todo this is incomplete / not necessarily right
    TYPE_MAPPING = {
        "<type 'int'>": 'uint256',
        "<type 'str'>": 'string'
    }
    @classmethod
    def parse_input_data(cls, input_data_location_type, input_str) -> str:
        if input_data_location_type != 2:
            raise NotImplementedError
        return input_str

    @classmethod
    def format_output_data(cls, output_data_location_type, model_output) -> str:
        if output_data_location_type != 2:
            raise NotImplementedError
        classes = [TYPE_MAPPING.get(str(type(m))) for m in model_output]
        return encode_abi(classes, model_output)


class ModelClass():
    input_data_type = DataType
    output_data_type = DataType

    def run(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def test(cls, *args, **kwargs):
        raise NotImplementedError
