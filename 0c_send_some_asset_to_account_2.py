from constants import address, signer, address_2, signer_2, algorand, test_asset
from algokit_utils import AssetOptInParams, AssetTransferParams

new_group = algorand.new_group()

new_group.add_asset_opt_in(
    AssetOptInParams(
        sender=address_2,
        signer=signer_2,
        asset_id=test_asset,
    )
)

new_group.add_asset_transfer(
    AssetTransferParams(
        sender=address,
        signer=signer,
        receiver=address_2,
        asset_id=test_asset,
        amount=10_000
    )
)

tx_ids = new_group.send().tx_ids
print(tx_ids)