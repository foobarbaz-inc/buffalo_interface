from pychain_utils.chainai import start_text_conditional_image_generation

def main():
    txn_receipt = start_text_conditional_image_generation(
        modelConfigLocation='https://arweave.net/IcQ1dcyGvOmeAZutDT5jqUQoRVA4mM-RXkG1wHUMqO0',
        prompt='New York City, oil on canvas',
        callbackId=0,
        seed=str(123).encode(),
        outputDataFormat=1
    )
    print(txn_receipt['transactionHash'].hex().lower())

if __name__ == '__main__':
    main()
