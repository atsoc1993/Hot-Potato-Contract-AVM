from constants import algorand, app_id
from algosdk.abi import ABIType
from algosdk.encoding import encode_address

boxes = algorand.app.get_box_names(app_id)

game_box_name_coder = ABIType.from_string('(address,uint64)')
game_box_value_coder = ABIType.from_string('(address,address,uint64,uint64,uint64,uint64,uint64)')

for box in boxes:
    #box_name = box.name_raw
    #box_name_decoded = game_box_name_coder.decode(box_name)

    player_1, player_2, player_1_round, player_2_round, vrf_round, asset, asset_amount = algorand.app.get_box_value_from_abi_type(app_id, box.name_raw, game_box_value_coder)
    #box_value_decoded = algorand.app.get_box_value_from_abi_type(app_id, box_name, game_box_value_coder)

    #print(f'Box Name Decoded: {box_name_decoded}')
    #print(f'Box Value Decoded: {box_value_decoded}')
    print(player_2)
    print(f'Player 1: {player_1}\nPlayer 2: {player_2 if encode_address(bytes(32)) != player_2 else None}\nPlayer 1 Round: {player_1_round}\nPlayer 2 Round: {player_2_round if player_2_round != 0 else None}\nVRF Round: {None if vrf_round == 0 else vrf_round}\nAsset: {'Algorand' if asset == 0 else asset}\nAmount: {asset_amount:,.0f}')
    print('\n')

'''

player_1: Address
player_2: Address
player_1_round: arc4.UInt64
player_2_round: arc4.UInt64
vrf_round: arc4.UInt64
asset: arc4.UInt64
asset_amount: arc4.UInt64

'''