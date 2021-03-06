import time
import base64
import hashlib
from celery import Celery

from buffalo_models import build_model_from_config
from pychain_utils.data_utils import convert_to_NFT

app = Celery('worker_celery', backend='redis://localhost', broker='pyamqp://guest@localhost//')
app.conf.result_extended = True

@app.task(name='run_inference')
def run_inference(job_id,
                  model_class_num,
                  seed_bytes_base64,
                  model_config_location,
                  input_data_location_type,
                  input_str,
                  output_data_location_type,
                  output_data_format):
    # convert seed from bytes to int
    seed_bytes = base64.b64decode(seed_bytes_base64)
    seed = int.from_bytes(hashlib.sha256(seed_bytes).digest()[:3], 'big')
    print(seed)

    # load the model
    model = build_model_from_config(model_class_num, model_config_location)

    # handle data formats and run the model
    if len(input_str) > 2:
        input = bytes.fromhex(input_str[2:])
    else:
        input = ''
    input_data = model.input_data_type.parse_input_data(
        input_data_location_type, input)
    model_output = model.run(input_data, seed=seed)
    output_data = model.output_data_type.format_output_data(
        output_data_location_type, model_output)

    # if needed, convert the output to NFT format
    #if output_data_format == 1:
    #    output_data = convert_to_NFT(output_data, seed, input_str)
    return job_id, output_data.hex()
