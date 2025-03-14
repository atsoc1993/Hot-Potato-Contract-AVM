from algokit_utils import AlgorandClient, AssetCreateParams
from constants import signer, address
from dotenv import load_dotenv, set_key

load_dotenv()

algorand = AlgorandClient.testnet()

asset_creation_tx = algorand.send.asset_create(
    AssetCreateParams(
        sender=address,
        signer=signer,
        total=1_000_000_000,
        asset_name='Test',
        unit_name='T1',
        decimals=0,
        manager=address,
        reserve=address,
    )
)

print(asset_creation_tx)
test_asset_id = asset_creation_tx.asset_id

set_key('.env', 'asset_id', str(test_asset_id))