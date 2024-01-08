from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir

# 生成 128 位（16 字节）的密钥
key = get_random_bytes(16)

# 使用 Shamir 的秘密分享算法生成分享
n = 5  # 分享总数
t = 3  # 最小阈值
shares = Shamir.split(t, n, key)

# 选取 t 个分享来重构秘密
selected_shares = shares[:t]
reconstructed_key = Shamir.combine(selected_shares)

print("Original Key:", key)
print("Reconstructed Key:", reconstructed_key)
