from constants import get_potato_client, algorand, address, signer
from algokit_utils import PaymentParams, AlgoAmount
from AlgoPotatoClient import CreateGameArgs

algo_potato_client = get_potato_client(address, signer)

app_address = algo_potato_client.app_address

asset_deposit = algorand.create_transaction.payment(
    PaymentParams(
        sender=address,
        signer=signer,
        receiver=app_address,
        amount=AlgoAmount(algo=1)
    )
)

mbr_fee = algorand.create_transaction.payment(
    PaymentParams(
        sender=address,
        signer=signer,
        receiver=app_address,
        amount=AlgoAmount(micro_algo=60_100)        
    )
)
txn_response = algo_potato_client.send.create_game(
    args=CreateGameArgs(
        asset_deposit=asset_deposit,
        mbr_fee=mbr_fee,
    ),
    send_params={
        'populate_app_call_resources': True
    }
)


tx_ids = txn_response.tx_ids
abi_results = txn_response.abi_return

print(f'Tx IDs: {tx_ids}')
print(f'ABI Results: {abi_results}')

