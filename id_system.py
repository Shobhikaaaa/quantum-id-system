import hashlib
import json
from time import time
from pqcrypto.sign.ml_dsa_44 import generate_keypair, sign, verify

# --- 1. CORE DIGITAL ID STRUCTURE AND PQC IMPLEMENTATION ---

# We choose ML-DSA-44 (NIST Level 2) for standard security
ML_DSA = 'ML-DSA-44' 

def generate_pqc_id(user_info: dict) -> dict:
    """
    Generates a Quantum-Resilient Digital ID.
    - Creates a PQC Key Pair (pk/sk).
    - Signs the hash of the user data using the secret key (sk).
    """
    # 1. Generate PQC Key Pair (sk is stored securely, pk is part of the ID)
    public_key, secret_key = generate_keypair()

    # 2. Serialize and Hash the User Data (Integrity Check)
    # The data we are signing/verifying must be a consistent format (bytes)
    user_data_str = json.dumps(user_info, sort_keys=True).encode('utf-8')
    data_hash = hashlib.sha256(user_data_str).digest()

    # 3. Create the Quantum-Resilient Digital Signature
    signature = sign(secret_key, data_hash)

    # 4. Construct the Digital ID Record
    digital_id = {
        'id_type': 'E-GOV_PQC_ID',
        'pqc_scheme': ML_DSA,
        'user_data': user_info,
        'public_key': public_key.hex(),  # Stored as hex for easy transport
        'signature': signature.hex(),    # Stored as hex
        'timestamp': time()
    }
    
    # We return the ID record and the secret key (sk is needed for future use/updates)
    return digital_id, secret_key.hex()

def verify_pqc_id(digital_id: dict) -> bool:
    """
    Verifies the integrity and authenticity of a Digital ID using the PQC signature.
    """
    try:
        # 1. Reconstruct Public Key and Signature from hex
        public_key = bytes.fromhex(digital_id['public_key'])
        signature = bytes.fromhex(digital_id['signature'])

        # 2. Recalculate the Data Hash
        user_data_str = json.dumps(digital_id['user_data'], sort_keys=True).encode('utf-8')
        data_hash = hashlib.sha256(user_data_str).digest()

        # 3. Perform PQC Verification
        # Returns True if the signature is valid for the hash using the public key
        return verify(public_key, data_hash, signature)

    except Exception as e:
        print(f"Verification Error: {e}")
        return False


# --- 2. QUICK TEST EXECUTION ---

if __name__ == '__main__':
    
    print(f"--- Starting PQC Digital ID Generation ({ML_DSA}) ---")
    
    # Define the critical identity data
    citizen_data = {
        'national_id': 'IND-123456789',
        'name': 'Manasi Sabnis',
        'clearance_level': 'E-GOV_SECURE_ACCESS',
        'device_serial': 'UAV-001' # Simulating a Defence Gadget ID
    }
    
    # GENERATE ID
    id_record, secret_key_hex = generate_pqc_id(citizen_data)
    
    print("\n[ID CREATED SUCCESSFULLY]")
    print(f"  Public Key Size: {len(id_record['public_key'])} bytes")
    print(f"  Signature Size: {len(id_record['signature'])} bytes")
    print(f"  PQC Scheme: {id_record['pqc_scheme']}")
    
    # VERIFY ID (Initial check)
    is_valid = verify_pqc_id(id_record)
    print(f"\n[VERIFICATION TEST 1]: ID is genuine? -> {is_valid}")
    
    # TAMPER TEST (Simulating Integrity Failure)
    print("\n--- Tampering Attempt (Defense-in-Depth check) ---")
    tampered_id = id_record.copy()
    # Attacker changes the clearance level in the data
    tampered_id['user_data']['clearance_level'] = 'ADMIN_OVERRIDE'
    
    is_valid_after_tamper = verify_pqc_id(tampered_id)
    print(f"  Tampered ID is valid? -> {is_valid_after_tamper}")
    
    if not is_valid_after_tamper:
        print("  ✅ SUCCESS: PQC Digital Signature detected data tampering (Integrity failed).")