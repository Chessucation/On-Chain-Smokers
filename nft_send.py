from erdpy.accounts import Account, Address
from erdpy.proxy import ElrondProxy
from erdpy.transactions import Transaction
from erdpy import config
import requests

SEND_FROM = 3501
SEND_TO = 4000
COLLECTION_IDENTIFIER = "OCS-2926f0"
ADDRESS_TO_SEND_TO = "erd..."


def int_to_hex(number: int) -> str:
    hex_nr = hex(number)[2:]
    if len(hex_nr) % 2 != 0:
        hex_nr = "0" + hex_nr
    return hex_nr


proxy = ElrondProxy("https://gateway.elrond.com")
sender = Account(pem_file="wallet.pem")
sender.sync_nonce(proxy)

nfts = requests.get(
    f"https://api.elrond.com/accounts/{sender.address.bech32()}/nfts?size=10000&collections={COLLECTION_IDENTIFIER}"
).json()
print(nfts)

nfts_to_send = []
for nft in nfts:
    number = nft["name"].split("#")[1]
    if int(number) >= SEND_FROM and int(number) <= SEND_TO:
        nfts_to_send.append(nft)

real_size = len(nfts_to_send)

tx = Transaction()
tx.nonce = sender.nonce
tx.sender = sender.address.bech32()
tx.value = str(int(0.00 * pow(10, 18)))
tx.receiver = sender.address.bech32()
tx.receiver = sender.address.bech32()
tx.gasPrice = 1000000000
tx.gasLimit = min(1_500_000 * real_size, 600_000_000)
tx.data = (
    "MultiESDTNFTTransfer"
    + "@"
    + Address(ADDRESS_TO_SEND_TO).hex()
    + "@"
    + int_to_hex(real_size)
)
for i in range(real_size):
    tx.data += (
        "@"
        + COLLECTION_IDENTIFIER.encode().hex()
        + "@"
        + int_to_hex(nfts_to_send[i]["nonce"])
        + "@"
        + int_to_hex(1)
    )
tx.chainID = "1"  # 1 for main, T for test, D for dev
tx.version = config.get_tx_version()
tx.sign(sender)
tx.send(proxy)
