import ecdsa
import base64


def validate_signature(public_key, signature, message):
    """Verify if the signature is correct. This is used to prove if
    it's you (and not someon else) trying to do a transaction with your
    address. Called when a user try to submit a new transaction.
    """
    public_key = (base64.b64decode(public_key)).hex()
    signature = base64.b64decode(signature)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
    try:
        return vk.verify(signature, message.encode())
    except:
        return False


def create_key():
    sk = ecdsa.SigningKey.generate()  # uses NIST192p
    vk = sk.get_verifying_key()
    return sk.to_string(), vk.to_string()