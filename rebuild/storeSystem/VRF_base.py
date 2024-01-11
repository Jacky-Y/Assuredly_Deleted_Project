import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

def overwrite_file(target_files, granularity, alg_param, level):
    """
    模拟覆写文件函数
    :param target_files: 要覆写的目标文件列表
    :param granularity: 覆写的粒度（特定字段名）
    :param alg_param: 用于覆写的随机数
    :param level: 覆写的次数
    """
    for _ in range(level):
        for file_path in target_files:
            try:
                # 读取 JSON 文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 根据 granularity 覆写特定字段或整个文件
                if granularity:
                    if granularity in data:  # 检查字段是否存在
                        data[granularity] = alg_param  # 覆写该字段
                    else:
                        print(f"Field '{granularity}' not found in {file_path}.")
                        continue  # 如果字段不存在，跳过此次覆写并处理下一个文件

                else:
                    # 如果没有指定 granularity，直接将文件内容覆写为 alg_param
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(alg_param)
                        continue  # 跳过下面的 JSON 写入步骤，直接处理下一个文件

                # 保存修改后的 JSON 数据
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error processing file {file_path}: {e}")



def key_generation():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

def compute_vrf(private_key, message):
    signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    digest = hashes.Hash(hashes.SHA256())
    digest.update(signature)
    vrf_output = digest.finalize()
    return vrf_output, signature


def verify_vrf(public_key, message, vrf_output, proof):
    try:
        public_key.verify(proof, message, ec.ECDSA(hashes.SHA256()))
        digest = hashes.Hash(hashes.SHA256())
        digest.update(proof)
        expected_vrf_output = digest.finalize()
        return expected_vrf_output == vrf_output
    except:
        return False


# 序列化密钥并保存到文件
def serialize_keys(private_key, public_key, private_file='private_key.pem', public_file='public_key.pem'):
    # 私钥序列化
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(private_file, 'wb') as f:
        f.write(private_pem)

    # 公钥序列化
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(public_file, 'wb') as f:
        f.write(public_pem)

# # 从文件中读取并反序列化密钥
# def deserialize_keys(private_file='private_key.pem', public_file='public_key.pem'):
#     # 从文件读取并反序列化私钥
#     with open(private_file, 'rb') as f:
#         private_key = serialization.load_pem_private_key(
#             f.read(),
#             password=None,
#         )
    
#     # 从文件读取并反序列化公钥
#     with open(public_file, 'rb') as f:
#         public_key = serialization.load_pem_public_key(
#             f.read(),
#         )

#     return private_key, public_key

# 从文件中读取并反序列化密钥
def deserialize_keys(private_file='private_key.pem'):
    # 从文件读取并反序列化私钥
    with open(private_file, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    return private_key


# # 从文件中读取并反序列化密钥
# def deserialize_keys(public_file='public_key.pem'):
    
#     # 从文件读取并反序列化公钥
#     with open(public_file, 'rb') as f:
#         public_key = serialization.load_pem_public_key(
#             f.read(),
#         )

#     return  public_key

if __name__=="__main__":
    # Test
    private_key, public_key = key_generation()

    # serialize_keys(private_key, public_key)

    message = b"Hello, VRF!"
    vrf_output, proof = compute_vrf(private_key, message)
    is_valid = verify_vrf(public_key, message, vrf_output, proof)

    print(private_key)
    print(public_key)
    print(f"Message: {message}")
    print(f"VRF Output: {vrf_output.hex()}")
    print(f"Proof: {proof.hex()}")
    print("VRF Output:",vrf_output)
    print("Proof:",proof)
    print(f"Is valid: {is_valid}")
                
print("out",type(vrf_output))
print("proof",type(proof))
# overwrite_file(["./storeSystem/test/0c1d2e3f4g5h.json"], "", "sdsdfadgagaga", 1)