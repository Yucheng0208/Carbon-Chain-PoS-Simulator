from flask import Flask, render_template, request, jsonify
from blockchain import Blockchain
from wallet import Wallet
import threading
import time

app = Flask(__name__)
blockchain = Blockchain()

wallets = {}
for name in ['Alice', 'Bob', 'Charlie', 'Dave']:
    wallet = Wallet(name)
    wallets[wallet.name] = wallet
    blockchain.register_wallet(wallet)

auto_mining = False

@app.route('/')
def home():
    return render_template('index.html', wallets=wallets)

@app.route('/api/wallets', methods=['GET'])
def get_wallets():
    return jsonify({name: {"balance": w.balance, "stake": w.stake} for name, w in wallets.items()})

@app.route('/api/transaction', methods=['POST'])
def create_transaction():
    data = request.json
    sender = data['sender']
    receiver = data['receiver']
    amount = int(data['amount'])
    try:
        blockchain.add_transaction(sender, receiver, amount)
        return jsonify({'message': 'Transaction added.'}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

@app.route('/api/mine', methods=['POST'])
def mine():
    block = blockchain.mine_pending_transactions()
    if block:
        return jsonify({'message': f'Block {block.index} mined by {block.validator}.'}), 201
    else:
        return jsonify({'message': 'No validator selected.'}), 400

@app.route('/api/chain', methods=['GET'])
def full_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': [{'sender': tx.sender, 'receiver': tx.receiver, 'amount': tx.amount, 'hash': tx.hash} for tx in block.transactions],
            'previous_hash': block.previous_hash,
            'validator': block.validator,
            'hash': block.hash
        })
    return jsonify(chain_data)

@app.route('/api/auto_mine', methods=['POST'])
def toggle_auto_mine():
    global auto_mining
    auto_mining = not auto_mining
    return jsonify({'auto_mining': auto_mining})

@app.route('/api/wallet/<wallet_name>/transactions', methods=['GET'])
def get_wallet_transactions(wallet_name):
    if wallet_name not in wallets:
        return jsonify({'error': 'Wallet not found'}), 404
    transactions = [{
        'sender': tx.sender,
        'receiver': tx.receiver,
        'amount': tx.amount,
        'hash': tx.hash,
        'timestamp': tx.timestamp
    } for tx in wallets[wallet_name].transactions]
    return jsonify(transactions)

@app.route('/api/wallet/<wallet_name>/mined_blocks', methods=['GET'])
def get_wallet_mined_blocks(wallet_name):
    if wallet_name not in wallets:
        return jsonify({'error': 'Wallet not found'}), 404
    return jsonify(wallets[wallet_name].mined_blocks)

def auto_mine_thread():
    global auto_mining
    while True:
        if auto_mining:
            blockchain.mine_pending_transactions()
        time.sleep(10)

if __name__ == '__main__':
    threading.Thread(target=auto_mine_thread, daemon=True).start()
    app.run(debug=True)
