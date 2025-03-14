from constants import get_potato_client, algorand, address, signer
from algokit_utils import AlgoAmount, CommonAppCallParams
from AlgoPotatoClient import CancelGameArgs, GameBoxName
from algosdk.abi import ABIType

algo_potato_client = get_potato_client(address, signer)
app_address = algo_potato_client.app_address
app_id = algo_potato_client.app_id

boxes = algorand.app.get_box_names(app_id)

game_box_name_coder = ABIType.from_string('(address,uint64)')

#The for loop has no authentication checks that a game has no active player 2
for box in boxes:
    box_name = box.name_raw
    player_1, counter = game_box_name_coder.decode(box_name)

game_box_name = GameBoxName(player_1, counter)

txn_response = algo_potato_client.send.cancel_game(
    args=CancelGameArgs(
        game_box_name=game_box_name,
    ),
    params=CommonAppCallParams(
        max_fee=AlgoAmount(micro_algo=2000)
    ),
    send_params={
        'populate_app_call_resources': True,
        'cover_app_call_inner_transaction_fees': True
    }
)


tx_ids = txn_response.tx_ids
abi_results = txn_response.abi_return

print(f'Tx IDs: {tx_ids}')
print(f'ABI Results: {abi_results}')

