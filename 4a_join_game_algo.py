from constants import get_potato_client, algorand
from constants import signer_2 as signer
from constants import address_2 as address
from algokit_utils import PaymentParams, AlgoAmount
from AlgoPotatoClient import PrimeGameVrfArgs, GameBoxName
from algosdk.abi import ABIType

algo_potato_client = get_potato_client(address, signer)
app_address = algo_potato_client.app_address
app_id = algo_potato_client.app_id

asset_deposit = algorand.create_transaction.payment(
    PaymentParams(
        sender=address,
        signer=signer,
        receiver=app_address,
        amount=AlgoAmount(algo=1)
    )
)


boxes = algorand.app.get_box_names(app_id)

game_box_name_coder = ABIType.from_string('(address,uint64)')

#The for loop has no authentication checks that a game is for an asset or algo
for box in boxes:
    box_name = box.name_raw
    player_1, counter = game_box_name_coder.decode(box_name)

print(f'Game from {player_1}')

game_box_name = GameBoxName(player_1, counter)

txn_response = algo_potato_client.send.prime_game_vrf(
    args=PrimeGameVrfArgs(
        game_box_name=game_box_name,
        asset_deposit=asset_deposit,
    ),
    send_params={
        'populate_app_call_resources': True
    }
)


tx_ids = txn_response.tx_ids
abi_results = txn_response.abi_return

print(f'Tx IDs: {tx_ids}')
print(f'ABI Results: {abi_results}')

