from algosdk.account import generate_account
from dotenv import load_dotenv, set_key

load_dotenv()

pk, address = generate_account()
pk_2, address_2 = generate_account()

set_key('.env', 'pk', pk)
set_key('.env', 'address', address)

set_key('.env', 'pk_2', pk_2)
set_key('.env', 'address_2', address_2)
