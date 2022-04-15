from pychain_utils.chainai import add_sequencer

def main():
    txn_receipt = add_sequencer()
    print(txn_receipt['transactionHash'].hex().lower())

if __name__ == '__main__':
    main()
