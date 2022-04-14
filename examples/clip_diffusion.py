from worker.worker_celery import run_inference

config_path = 'https://arweave.net/1OEFoIevhpO3VZt2YJt14beE4mJSA5Gl0zHRChtWBDM'
model_class_num = 0
prompt = "New York City, oil on canvas"
seed = str(123).encode()

job_id, output_path = run_inference(0, 
                                    model_class_num,
                                    seed,
                                    config_path,
                                    2,
                                    prompt,
                                    0,
                                    0)

print(job_id)
print(output_path)

#model = build_model_from_config(0, config_path)
#img_tensor = model.run("New York City, oil on canvas", seed=123)
#output_arweave_path = torch_img_to_arweave(img_tensor)
#print(output_arweave_path)
