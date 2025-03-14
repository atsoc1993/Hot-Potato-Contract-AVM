from constants import get_potato_client, algorand, address, signer, test_asset
from algokit_utils import AssetTransferParams, PaymentParams, AlgoAmount, CommonAppCallParams
from AlgoPotatoClient import CreateGameArgs, AssetOptInArgs

algo_potato_client = get_potato_client(address, signer)

app_address = algo_potato_client.app_address

asset_deposit = algorand.create_transaction.asset_transfer(
    AssetTransferParams(
        sender=address,
        signer=signer,
        receiver=app_address,
        asset_id=test_asset,
        amount=1_000,
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

new_app_group_tx = algo_potato_client.new_group()

contract_opted_into_asset = False
contract_assets = algorand.client.algod.account_info(app_address)['assets']
for asset in contract_assets:
    if asset['asset-id'] == test_asset:
        contract_opted_into_asset = True
    
if contract_opted_into_asset == False:
    opt_in_fee = algorand.create_transaction.payment(
        PaymentParams(
            sender=address,
            signer=signer,
            receiver=app_address,
            amount=AlgoAmount(algo=0.1)
        )
    )

    new_app_group_tx.asset_opt_in(
        AssetOptInArgs(
            asset=test_asset,
            mbr_payment=opt_in_fee,
        ),
        params=CommonAppCallParams(
            max_fee=AlgoAmount(algo=0.01)
        )
    )

new_app_group_tx.create_game(
    args=CreateGameArgs(
        asset_deposit=asset_deposit,
        mbr_fee=mbr_fee,
    ),
    params=CommonAppCallParams(
        max_fee=AlgoAmount(algo=0.01)
    )
)

txn_response = new_app_group_tx.send(
    send_params={
        'populate_app_call_resources': True,
        'cover_app_call_inner_transaction_fees': True
    }
)
tx_ids = txn_response.tx_ids
abi_results = txn_response.returns

print(f'Tx IDs: {tx_ids}')
print(f'ABI Results: {abi_results[0].raw_value}')

