import subprocess
import base58
import binascii
import os
import requests

from pychain_utils.wallets import create_solana_wallet

host = 'http://node1.bundlr.network'

fund_amount_MB = 500
def upload(local_filename, root=None):
    private_key, public_key = create_solana_wallet(root=root)

    # check file size in MB
    file_size = os.path.getsize(local_filename)/1024/1024

    if file_size*1.2 > fund_amount_MB:
        raise ValueError(f'file exceeds limit of {fund_amount_MB} MB')

    # check balance in MB
    balance_in_sol = check_balance(root=root)
    balance_in_MB = sol_to_MB(balance_in_sol)
    if balance_in_MB < file_size*1.2:
        print(f'Low funds in bundlr wallet, funding from solana wallet...')
        fund(fund_amount_MB, root=root)

    cmd = f'bundlr upload {local_filename} -h {host} -w {private_key} -c solana'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    web_address = result.stdout.decode('utf-8').strip().split(' ')[-1]
    return web_address

def upload_data(data, root=None):
    output_id = base58.b58encode(os.urandom(20)).decode('utf-8')
    output_path = f'outputs/{output_id}'
    if root is not None:
        output_path = os.path.join(root, output_path)

    with open(output_path, 'wb') as f:
        f.write(data)

    return upload(output_path, root=root)

def download(arweave_path, root=None):
    arweave_id = arweave_path.split('/')[-1]
    output_path = f'downloads/{arweave_id}'

    if root is not None:
        output_path = os.path.join(root, output_path)
    
    if os.path.exists(output_path):
        print(f'Reading {arweave_path} from cache')
        return output_path

    print(f'Downloading file from {arweave_path}')

    with requests.get(arweave_path, stream=True) as r:
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024*50): # 50 MB chunks
                f.write(chunk)

    return output_path

lamports_per_sol = 1000000000
def check_balance(root=None):
    private_key, public_key = create_solana_wallet(root=root)
    cmd = f'bundlr balance {public_key} -h {host} -c solana'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    sol_val = float(result.stdout.decode('utf-8').strip().split(' ')[-2].strip('()'))
    return sol_val

def sol_to_MB(sol_val):
    lamports_for_1mb = check_price(1)
    val_in_MB = sol_val*lamports_per_sol/lamports_for_1mb
    return val_in_MB

def check_price(megabytes):
    price_cmd = f'bundlr price {int(megabytes*1024*1024)} -h {host} -c solana'
    result = subprocess.run(price_cmd, shell=True, stdout=subprocess.PIPE)
    lamports = int(result.stdout.decode('utf-8').strip().split(' ')[7])
    return lamports

def fund(megabytes, root=None):
    private_key, public_key = create_solana_wallet(root=root)
    lamports = check_price(megabytes)
    print(f'Current price of bundlr: {lamports/lamports_per_sol} sol for {megabytes} MB')

    fund_cmd = f'yes | bundlr fund {lamports} -h {host} -c solana -w {private_key}'
    #print(fund_cmd)
    result = subprocess.run(fund_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    output = result.stdout.decode('utf-8').strip()
    error = result.stderr.decode('utf-8').strip()

    if 'insufficient lamports' in error:
        raise ValueError('insufficient lamports in solana to fund bundlr wallet')

    print(output)
    print(error)

if __name__ == '__main__':
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent
    #print(root)
    #print(check_price(200)/lamports_per_sol)
    #print(check_balance(root=root))
    #fund(1, root=root)
    #print(check_balance(root=root))
    print(upload('../buffalo_models/TextConditionalImageGeneration/configs/v-diffusion_CC12M_1_CFG.json', root=root))
    #download('https://arweave.net/0W-lfJyrouaa7VwsjMIbamKyVzvDNycM3rcjsH992mQ', root=root)
