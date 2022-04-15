import base64
from worker.worker_celery import run_inference

config_path = 'https://arweave.net/IcQ1dcyGvOmeAZutDT5jqUQoRVA4mM-RXkG1wHUMqO0'
model_class_num = 0
prompt = "New York City, oil on canvas"
seed_bytes = str(123).encode()
seed_bytes = base64.b64encode(seed_bytes).decode('ascii')

job_id, output_path = run_inference(0, 
                                    model_class_num,
                                    seed_bytes,
                                    config_path,
                                    2,
                                    prompt,
                                    0,
                                    1)

print(job_id)
print(output_path)
