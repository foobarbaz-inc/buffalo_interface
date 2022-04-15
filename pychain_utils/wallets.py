import os
import base58
from functools import partial

import web3
from eth_account import Account
from solana.keypair import Keypair

from . import root

supported_currency = ['eth', 'sol']
def create_wallet(currency):
    # Create an eth/sol wallet if one does not exist
    if currency not in supported_currency:
        raise NotImplementedError('Supported currencies are {supported_currency}')

    private_key_path = f'keys/private_key.{currency}'
    public_key_path = f'keys/public_key.{currency}'

    private_key_path = os.path.join(root, private_key_path)
    public_key_path = os.path.join(root, public_key_path)

    if not (os.path.exists(private_key_path) and os.path.exists(public_key_path)):
        if currency == 'eth':
            acct = Account.create('o;iasudgyfkhijohugyftdrf')
            private_key = acct.privateKey.hex().lower()
            public_key = acct.address
        elif currency == 'sol':
            keypair = Keypair()
            private_key = base58.b58encode(keypair.secret_key).decode('ascii')
            public_key = str(keypair.public_key)
        with open(private_key_path, 'w') as f:
            f.write(private_key)
        with open(public_key_path, 'w') as f:
            f.write(public_key)
    else:   
        with open(private_key_path, 'r') as f:
            private_key = f.read().strip()
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()

    return private_key, public_key

create_solana_wallet = partial(create_wallet, 'sol')
create_eth_wallet = partial(create_wallet, 'eth')
