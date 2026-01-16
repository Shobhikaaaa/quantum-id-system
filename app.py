from flask import Flask, render_template, request, redirect, url_for
from blockchain import Blockchain
from id_system import generate_pqc_id, verify_pqc_id # Ensure these imports are correct
from time import time

app = Flask(__name__)

# Initialize the Blockchain (This instance will run in memory for the demo)
blockchain = Blockchain()

# --- WEB ROUTES ---

@app.route('/')
def index():
    """Renders the main dashboard showing the blockchain."""
    
    # Run the validity check every time the page loads
    is_valid = "CHAIN VALID" if blockchain.is_chain_valid() else "CHAIN INVALID - TAMPERING DETECTED!"
    
    return render_template(
        'index.html',
        chain=reversed(blockchain.chain), # Display newest block first
        chain_length=len(blockchain.chain),
        is_valid=is_valid
    )

@app.route('/create_and_mine', methods=['POST'])
def create_and_mine():
    """Handles the form submission to create a new ID and mine a block."""
    
    # 1. Get data from the simple form submission
    user_id = request.form.get('user_id')
    purpose = request.form.get('purpose')
    
    if user_id and purpose:
        user_data = {
            'id': user_id,
            'purpose': purpose,
            'timestamp': time() 
        }
        
        # 2. Generate PQC ID and register it
        pqc_id, _ = generate_pqc_id(user_data) 
        blockchain.register_id(pqc_id)
        
        print(f"Registered new PQC ID: {user_id}")
        
        # 3. Immediately mine the block
        blockchain.mine_pending_ids(difficulty=3)
    
    # 4. Redirect back to the main page to see the new block
    return redirect(url_for('index'))

@app.route('/tamper_chain')
def tamper_chain():
    """Endpoint to manually demonstrate a security breach."""
    if len(blockchain.chain) > 1:
        # Tamper with the data of the first block (index 1)
        tampering_block = blockchain.chain[1]
        
        # Change the data inside a block after it was mined
        tampering_block.digital_ids[0]['user_data']['purpose'] = 'HACKED_BY_ATTACKER!'
        print("!!! BLOCKCHAIN DATA HAS BEEN MANUALLY TAMPERED FOR DEMO !!!")

    return redirect(url_for('index'))


if __name__ == '__main__':
    # Use environment variable for port if available (standard for deployment)
    # We set a default of 5000 if not specified
    import os
    port = int(os.environ.get('PORT', 5001))
    
    print(f"Running Flask app on http://0.0.0.0:{port}/")
    
    # Run the app on all available interfaces (0.0.0.0)
    # This should resolve any local network/security conflicts on macOS.
    app.run(host='0.0.0.0', port=port, debug=True)