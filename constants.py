from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algokit_utils import AlgorandClient, AppFactory, AppFactoryParams
from AlgoPotatoClient import AlgoPotatoFactory, SourceMap
from algosdk.account import address_from_private_key
from dotenv import load_dotenv
from pathlib import Path
import json
import os

load_dotenv()

pk = os.getenv('pk')
address = address_from_private_key(pk)
signer = AccountTransactionSigner(pk)

pk_2 = os.getenv('pk_2')
address_2 = os.getenv('address_2')
signer_2 = AccountTransactionSigner(pk_2)
algo_potato_app_spec = (Path(__file__).parent / 'AlgoPotato.arc56.json').read_text()
algo_potato_approval_map = SourceMap(json.loads((Path(__file__).parent / 'AlgoPotato.approval.puya.map').read_text()))

algorand = AlgorandClient.testnet()

if os.getenv('asset_id'):
    test_asset = int(os.getenv('asset_id'))

def get_algo_potato_factory(address, signer):

    algo_potato_app_factory_params = AppFactoryParams(
        algorand=algorand,
        app_spec=algo_potato_app_spec,
        default_sender=address,
        default_signer=signer,
    )

    algo_potato_factory = AppFactory(
        params=algo_potato_app_factory_params
    )

    return algo_potato_factory

if os.getenv('app_id'):
    app_id = int(os.getenv('app_id'))

def get_potato_client(address, signer):

    algo_potato_client = algorand.client.get_typed_app_factory(
        typed_factory=AlgoPotatoFactory, 
        default_sender=address, 
        default_signer=signer
    ).get_app_client_by_id(
        app_id=app_id, 
        approval_source_map=algo_potato_approval_map
    )
    
    return algo_potato_client



    
