import hashlib
import json
from time import time

# --- 1. CORE BLOCKCHAIN CLASSES ---

class Block:
    """Represents a single block in the chain, storing IDs."""
    def __init__(self, index, digital_ids, previous_hash):
        self.index = index
        self.timestamp = time()
        self.digital_ids = digital_ids  # List of PQC IDs created by id_system.py
        self.previous_hash = previous_hash
        self.nonce = 0 # Nonce is used for Proof-of-Work (Mining)
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Creates a SHA-256 hash of the block's contents."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.digital_ids,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        """
        Implements a simple Proof-of-Work. The hash must start with 'difficulty' number of zeros.
        """
        # This loop is computationally intensive, simulating "mining" or securing the block
        target_prefix = '0' * difficulty
        while not self.hash.startswith(target_prefix):
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block Mined! Hash: {self.hash}")


class Blockchain:
    """The full chain of blocks, managing transactions and chain integrity."""
    def __init__(self):
        self.chain = []
        self.pending_ids = []
        # Create the Genesis Block (the first block)
        self.create_genesis_block()
        
    def create_genesis_block(self):
        """The starting block of the chain."""
        genesis_block = Block(0, ["Genesis Block: System Initialized"], "0")
        self.chain.append(genesis_block)
        
    @property
    def last_block(self):
        """Convenience function to get the latest block."""
        return self.chain[-1]

    def register_id(self, digital_id):
        """Adds a newly created PQC Digital ID to the pending list."""
        self.pending_ids.append(digital_id)
        
    def mine_pending_ids(self, difficulty=3):
        """
        Mines a new block containing all pending IDs, adding it to the chain.
        """
        if not self.pending_ids:
            print("No new IDs to process.")
            return

        print(f"\n--- Mining Block {self.last_block.index + 1} with {len(self.pending_ids)} new IDs ---")
        
        # Create the new block
        new_block = Block(
            index=self.last_block.index + 1,
            digital_ids=self.pending_ids,
            previous_hash=self.last_block.hash
        )

        # Mine the block (secures the block)
        new_block.mine_block(difficulty)

        # Add the new block to the chain
        self.chain.append(new_block)
        self.pending_ids = []  # Clear the pending list

    def is_chain_valid(self):
        """
        Verifies the integrity of the entire chain by checking hash links.
        This is the ultimate check for data tampering.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # 1. Check if the hash of the current block is correct (Internal Integrity)
            if current_block.hash != current_block.calculate_hash():
                print(f"Chain INVALID: Block {i} hash is corrupted!")
                return False

            # 2. Check the hash link to the previous block (Chain Integrity)
            if current_block.previous_hash != previous_block.hash:
                print(f"Chain INVALID: Block {i} is not correctly linked!")
                return False
        
        return True


# --- 2. INTEGRATION TEST ---
if __name__ == '__main__':
    # Import the PQC ID generation function from your other file
    from id_system import generate_pqc_id

    # 1. Initialize the Blockchain
    gov_chain = Blockchain()

    # 2. Define IDs (Simulating users/devices)
    ids_to_create = [
        {'id': 'Citizen-001', 'purpose': 'Banking Access'},
        {'id': 'UAV-007', 'purpose': 'Secure Telemetry'},
        {'id': 'Satellite-A', 'purpose': 'Command Control'}
    ]

    # 3. Create and Register IDs
    for data in ids_to_create:
        pqc_id, _ = generate_pqc_id(data)
        gov_chain.register_id(pqc_id)
        print(f"Registered PQC ID: {data['id']}")

    # 4. Mine the IDs into a Block
    gov_chain.mine_pending_ids(difficulty=3)

    # 5. Check Integrity
    print(f"\n[Chain Integrity Check]: {gov_chain.is_chain_valid()}")
    
    # --- Tampering Test on the Block ---
    print("\n--- Tampering with a mined Block's data ---")
    
    # Tamper with the data of the first ID in the first non-genesis block
    tampering_block = gov_chain.chain[1]
    
    # Change the purpose of Citizen-001 in the stored block data
    tampering_block.digital_ids[0]['user_data']['purpose'] = 'ADMIN_OVERRIDE_TAMPERED!'
    
    # The block's stored hash is now incorrect since the data changed!
    print("ATTENTION: Block data was tampered after mining.")
    print(f"Chain Integrity Check NOW: {gov_chain.is_chain_valid()}")
    
    if not gov_chain.is_chain_valid():
        print("  ✅ SUCCESS: Blockchain integrity check failed, proving immutability (Data Integrity).")