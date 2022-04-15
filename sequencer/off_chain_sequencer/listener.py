from web3 import Web3
import json
import base64
import redis
import requests
from celery import Celery
from celery.execute import send_task

from pychain_utils.chainai import get_job, update_status

listener_app = Celery('listener', broker='pyamqp://guest@localhost//')
redis = redis.StrictRedis(host='localhost', port='6379')

query = '''
{
  jobs(orderBy: id) {
    id
    modelCategory
    seed
    modelConfigLocation
    inputDataLocationType
    input
    outputDataLocationType
    outputDataFormat
    createdTimestamp
  }
}
'''
endpoint = 'https://api.studio.thegraph.com/query/23114/chainai-notifier/v0.0.4'

redis_initiated_str = 'job_id_initiated'
def get_redis_status():
    job_id_to_redis_status = {}
    all_keys = list(redis.keys())

    # first get the keys for when the job is initiated
    for key in all_keys:
        key_name = key.decode('utf-8')
        if redis_initiated_str not in key_name:
            continue

        job_id = int(key_name.split(' ')[-1])
        job_id_to_redis_status[job_id] = 'INITIATED'
    
    # then get the keys for when the job has been added to the backend properly
    for key in all_keys:
        key_name = key.decode('utf-8')
        if redis_initiated_str in key_name:
            continue
        redis_task = redis.get(key)
        redis_task = json.loads(redis_task.decode('utf-8'))
        if 'kwargs' not in redis_task:
            continue
        job_id = redis_task['kwargs']['job_id']
        status = redis_task['status']
        job_id_to_redis_status[job_id] = status

    return job_id_to_redis_status

def redis_id_to_contract_job_id(task_id):
    all_keys = list(redis.keys())
    for key in all_keys:
        key_name = key.decode('utf-8')
        if redis_initiated_str in key_name:
            continue
        redis_task = redis.get(key)
        redis_task = json.loads(redis_task.decode('utf-8'))
        if 'kwargs' not in redis_task:
            continue

        if redis_task['task_id'] == task_id:
            job_id = redis_task['kwargs']['job_id']
            return job_id
    
    return None

def run_job(job):
    job_id = int(job['id'])
    
    # need to convert e.g. '0x313233' to bytes and then serialize the bytes
    seed_bytes = bytes.fromhex(job['seed'][2:])
    seed_bytes = base64.b64encode(seed_bytes).decode('ascii')

    kwargs = {
        'job_id': job_id,
        'model_class_num': job['modelCategory'],
        'seed_bytes_base64': seed_bytes,
        'model_config_location': job['modelConfigLocation'],
        'input_data_location_type': job['inputDataLocationType'],
        'input_str': job['input'],
        'output_data_location_type': job['outputDataLocationType'],
        'output_data_format': job['outputDataFormat']
    }

    # send the task to workers
    send_task('run_inference', kwargs=kwargs, queue='inference', link=update_contract.s(),
            link_error=worker_error.s())

    # set the redis indicator that we've handled this
    redis.set(f'{redis_initiated_str} {job_id}', '')

@listener_app.task(name='check_for_new_job')
def check_for_new_job():
    # get all jobs ever created
    request = requests.post(endpoint, json={'query': query})
    jobs = request.json()['data']['jobs']
    print('Received jobs from subgraph:')
    print(jobs)

    # get all redis tasks and their status
    job_id_to_redis_status = get_redis_status()
    print('Found existing redis jobs:')
    print(job_id_to_redis_status)

    for job in jobs:
        # find the jobs that have not yet finished
        job_id = int(job['id'])
        current_job_data = get_job(job_id)
        current_status = current_job_data[0][0]

        # if the job is already finished, there is nothing to do
        if current_status != 'Created':
            continue

        # if the job is currently running or waiting to run, there is nothing to do
        if job_id in job_id_to_redis_status:
            continue
        
        # otherwise, this is a new job that needs to be handled
        print(f'Found a job that needs to be initiated: {job_id}')
        run_job(job)

@listener_app.task()
def update_contract(worker_output):
    job_id, result_path = worker_output
    print(f'Got successful response for job_id {job_id}. Output path is {result_path}.')
    update_status(job_id, 'Succeeded', result_path)

@listener_app.task()
def worker_error(result_id):
    job_id = redis_id_to_contract_job_id(result_id)
    print(f'Encountered error with redis id {result_id} job_id {job_id}')
    update_status(job_id, 'Failed', '')

@listener_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30, check_for_new_job.s())

def delete_all():
    for key in redis.keys():
        redis.delete(key)

if __name__ == '__main__':
    delete_all()
    print(get_redis_status())
