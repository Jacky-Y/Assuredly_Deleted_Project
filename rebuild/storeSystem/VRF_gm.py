from gmssl import sm2, sm3, func

def key_generation():
    # 这里使用固定的私钥和公钥仅作为示例
    private_key = '00B9AB0B828FF68872F21A837FC303668428DEA11DCD1B24429D0C99E24EED83D5'
    public_key = 'B9C9A6E04E9C91F7BA880429273747D7EF5DDEB0BB2FF6317EB00BEF331A83081A6994B8993F3F5D6EADDDB81872266C87C018FB4162F5AF347B483E24620207'
    sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key=private_key)
    return private_key, public_key, sm2_crypt

def compute_vrf(private_key, message, sm2_crypt):
    
    # 确保消息是字节类型
    if not isinstance(message, bytes):
        message = message.encode()

    random_hex_str = func.random_hex(sm2_crypt.para_len)
    signature = sm2_crypt.sign(message, random_hex_str)
    vrf_output = sm3.sm3_hash(func.bytes_to_list(signature.encode()))
    return vrf_output, signature

def verify_vrf(public_key, message, vrf_output, proof, sm2_crypt):
    # 确保消息是字节类型
    if not isinstance(message, bytes):
        message = message.encode()

    is_valid_signature = sm2_crypt.verify(proof, message)
    expected_vrf_output = sm3.sm3_hash(func.bytes_to_list(proof.encode()))
    return is_valid_signature and expected_vrf_output == vrf_output


# 使用示例
private_key, public_key, sm2_crypt = key_generation()
message = 'Hello, VRF!'
vrf_output, proof = compute_vrf(private_key, message, sm2_crypt)
is_valid = verify_vrf(public_key, message, vrf_output, proof, sm2_crypt)

print(f"Private Key: {private_key}")
print(f"Public Key: {public_key}")
print(f"Message: {message}")
print(f"VRF Output: {vrf_output}")
print(f"Proof: {proof}")
print(f"Is valid: {is_valid}")
