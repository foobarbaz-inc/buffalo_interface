import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import pathlib
import os

def load_abi_from_hardhat(path):
    with open(path, 'r') as f:
        data = json.load(f)
        abi = data['abi']
        abi = json.dumps(abi)
    return abi

# environment data
if 'RINKEBY_HTTP_PROVIDER' not in os.environ:
    raise ValueError('Missing environment variable RINKEBY_HTTP_PROVIDER')

if 'CHAINAI_ADDRESS' not in os.environ:
    raise ValueError('Missing environment variable CHAINAI_ADDRESS')

if 'RINKEBY_PRIVATE_KEY' not in os.environ:
    raise ValueError('Missing environment variable RINKEBY_PRIVATE_KEY')

w3 = Web3(Web3.HTTPProvider(os.environ['RINKEBY_HTTP_PROVIDER']))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

cd = pathlib.Path(__file__).resolve().parent
abi = load_abi_from_hardhat(f'{cd}/contract_jsons/ChainAIV2.json')
chainai_address = os.environ['CHAINAI_ADDRESS']
contract_instance = w3.eth.contract(address=chainai_address, abi=abi)

private_key = os.environ['RINKEBY_PRIVATE_KEY']
public_key = Account.from_key(private_key).address

# enums
int_to_status = ['Created', 'Failed', 'Succeeded']
status_to_int = {status: i for i, status in enumerate(int_to_status)}

def get_job(job_id):
    data = contract_instance.functions.jobs(job_id).call()
    data[0] = list(data[0])
    data[0][0] = int_to_status[data[0][0]]
    return data

def get_sequencer(address):
    result = contract_instance.functions.sequencers(address).call()
    return result

def submit_transaction(transaction):
    transaction.update({'nonce': w3.eth.get_transaction_count(public_key)})
    transaction.update({'gas': transaction['gas']*2})
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key)

    txn_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    return txn_receipt

def start_text_conditional_image_generation(
        modelConfigLocation,
        prompt,
        callbackId,
        seed,
        outputDataFormat):
    transaction = contract_instance.functions.textConditionalImageGeneration(
        modelConfigLocation,
        prompt,
        callbackId,
        seed,
        outputDataFormat
    ).buildTransaction()
    txn_receipt = submit_transaction(transaction)
    return txn_receipt

def update_status(job_id, jobStatus, resultsLocation):
    # jobStatus is the string version
    jobStatus = status_to_int[jobStatus]
    transaction_fn = contract_instance.functions.updateJobStatus(job_id,
            jobStatus, resultsLocation)
    transaction = transaction_fn.buildTransaction(transaction=
                    {'from': public_key})
    txn_receipt = submit_transaction(transaction)
    return txn_receipt

def add_sequencer():
    transaction_fn = contract_instance.functions.addSequencer(public_key)
    transaction = transaction_fn.buildTransaction(transaction=
                    {'from': public_key})
    txn_receipt = submit_transaction(transaction)
    return txn_receipt

if __name__ == '__main__':
    print(get_sequencer(public_key))
    for i in range(1, 100000000):
        job_data = get_job(i)
        createdTimestamp = job_data[0][2]
        if createdTimestamp == 0:
            break
        print(job_data)

