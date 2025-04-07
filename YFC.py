import json
import logging
from web3 import Web3
import base64  

logging.basicConfig(level=logging.INFO)

w3 = Web3(Web3.HTTPProvider('http://51.250.44.22:8545'))

contract_address = '0x584ff4869645Eb61e412ef0391979D644B8891A9'
contract_abi = [
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_temperature",
                "type": "uint256"
            }
        ],
        "name": "recordTemperature",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "index",
                "type": "uint256"
            }
        ],
        "name": "getTemperatureRecord",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "temperature",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getRecordCount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

from_address = '0xb04b3bd831466dDb7B29b6CB1275cb9cC851EC6a'
private_key = '0xe5a1242e7d5a410843253dd186655235a7af4ff5a9cd18a8f436d8489eace24a'


def record_temperature(event, context):
    try:
        logging.info(f"Full event received: {json.dumps(event)}")
        print(json.dumps(event))
        
        raw_body = None
        if 'body' in event:
            raw_body = event.get('body', '')
            logging.info(f"Found 'body' key (raw integration): '{raw_body}'")
        elif 'messages' in event and len(event['messages']) > 0:
            message = event['messages'][0]
            encoded_payload = message.get('details', {}).get('payload', '')
            logging.info(f"Found IoT Core message payload: '{raw_body}'")
            try:
                decoded_bytes = base64.b64decode(encoded_payload)
                raw_body = decoded_bytes.decode('utf-8')  # строка JSON
                logging.info(f"Decoded payload: '{raw_body}'")
            except Exception as e:
                logging.error(f"Failed to decode payload: {str(e)}")
                return f"Error: Failed to decode payload: {str(e)}"
        else:
            logging.error("No valid data found in event (neither 'body' nor 'messages')")
            return "Error: No valid data found in event"

        if not raw_body:
            logging.error("Body/payload is empty")
            return "Error: Body/payload is empty"

        try:
            data = json.loads(raw_body)
            logging.info(f"Parsed data: {data}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse body as JSON: {str(e)}")
            return f"Error: Failed to parse body as JSON: {str(e)}"

        temperature = data.get("temperature")
        if temperature is None:
            logging.error("Temperature data is missing")
            return "Error: Temperature data is missing"

        try:
            temperature_float = float(temperature)
            if temperature_float < 0:
                logging.error("Temperature must be non-negative for uint")
                return "Error: Temperature must be non-negative"
            temperature_uint = int(temperature_float * 100)
            logging.info(f"Converted temperature: {temperature_uint}")
        except ValueError as e:
            logging.error(f"Invalid temperature value: {str(e)}")
            return f"Error: Invalid temperature value: {str(e)}"

        if not w3.is_connected():
            logging.error("Blockchain node is not available")
            return "Error: Blockchain node is not available"

        chain_id = w3.eth.chain_id
        nonce = w3.eth.get_transaction_count(from_address)
        logging.info(f"Chain ID: {chain_id}, Nonce: {nonce}")

        transaction = contract.functions.recordTemperature(temperature_uint).build_transaction({
            'from': from_address,
            'gas': 200000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce,
            'chainId': chain_id
        })
        logging.info(f"Transaction built: {transaction}")

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        logging.info(f"Transaction signed: {signed_txn}")

        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        logging.info(f"Transaction sent: {tx_hash.hex()}")

        return f"Temperature recorded successfully, tx_hash: {tx_hash.hex()}"

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
