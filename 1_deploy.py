from algokit_utils import PaymentParams, AlgoAmount
from constants import address, signer, algorand, get_algo_potato_factory
from dotenv import set_key, load_dotenv


load_dotenv()

algo_potato_factory = get_algo_potato_factory(address, signer)

algo_potato_client, response = algo_potato_factory.send.bare.create()

app_id = algo_potato_client.app_id
app_address = algo_potato_client.app_address

print(f'App created: {app_id}')

set_key('.env', key_to_set='app_id', value_to_set=str(app_id))

algorand.send.payment(
    PaymentParams(
        sender=address,
        signer=signer,
        receiver=app_address,
        amount=AlgoAmount(algo=0.1)
    )
)