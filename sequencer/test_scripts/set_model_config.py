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

if 'EVOLVINGNFT_ADDRESS' not in os.environ:
    raise ValueError('Missing environment variable EVOLVINGNFT_ADDRESS')

if 'RINKEBY_PRIVATE_KEY' not in os.environ:
    raise ValueError('Missing environment variable RINKEBY_PRIVATE_KEY')

w3 = Web3(Web3.HTTPProvider(os.environ['RINKEBY_HTTP_PROVIDER']))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

cd = pathlib.Path(__file__).resolve().parent
abi = load_abi_from_hardhat(f'{cd}/../../pychain_utils/contract_jsons/EvolvingNFT.json')
evolvingnft_address = os.environ['EVOLVINGNFT_ADDRESS']
contract_instance = w3.eth.contract(address=evolvingnft_address, abi=abi)

private_key = os.environ['RINKEBY_PRIVATE_KEY']
public_key = Account.from_key(private_key).address
print(public_key)

def submit_transaction(transaction):
    transaction.update({'nonce': w3.eth.get_transaction_count(public_key)})
    transaction.update({'gas': transaction['gas']*2})
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key)

    txn_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    return txn_receipt

def update_model(newModel):
    transaction = contract_instance.functions.updateModel(newModel)\
            .buildTransaction(transaction={'from': public_key})
    txn_receipt = submit_transaction(transaction)
    return txn_receipt

def get_model():
    return contract_instance.functions.model().call()

if __name__ == '__main__':
    #config_path = 'https://arweave.net/IcQ1dcyGvOmeAZutDT5jqUQoRVA4mM-RXkG1wHUMqO0'
    #txn_receipt = update_model(config_path)
    #print(txn_receipt)
    print(get_model())
