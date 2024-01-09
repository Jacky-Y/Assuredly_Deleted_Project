from secrets import randbelow
from typing import List, Tuple
from functools import reduce
# from Crypto.Util.py3compat import is_native_int
# from Crypto.Util import number
# from Crypto.Util.number import long_to_bytes, bytes_to_long
# from Crypto.Random import get_random_bytes as rng
from math import ceil
import binascii
import os
import shutil
import json
import copy
from random import choice
import struct
import sys

from overwirter_class import VideoOverwriter

class SecretShare(object):
    # 生成n个密钥分片
    @staticmethod
    def generate_shares(secret, t, n):
        if t == n:
            res = bytearray(16)
            res[:] = secret
            coeffs = [rng(16) for i in range(n - 1)]
            for i in range(0, n-1):
                for j in range(16):
                    res[j] = res[j] ^ coeffs[i][j]
            coeffs.append(bytes(res))
            return [(i, coeffs[i-1]) for i in range(1, n+1)]
        else:
            coeffs = [_Element(rng(16)) for i in range(t - 1)]
            coeffs.append(_Element(secret))

            # Each share is y_i = p(x_i) where x_i is the public index
            # associated to each of the n users.

            def make_share(user, coeffs):
                idx = _Element(user)
                share = _Element(0)
                for coeff in coeffs:
                    share = idx * share + coeff

                return share.encode()

            return [(i, make_share(i, coeffs)) for i in range(1, n + 1)]

    # 当得到不少于t个分片时，重建密钥
    @staticmethod
    def reconstruct_key(shares, t, n):
        k = len(shares)
        if k < t:
            print("分片不够！")
            return
        if t == n:
            res = bytearray(16)
            for x,y in shares:
                for i in range(16):
                    res[i] = res[i] ^ y[i]

            return bytes(res)
        else:
            gf_shares = []
            for x in shares:
                idx = _Element(x[0])
                value = _Element(x[1])
                if any(y[0] == idx for y in gf_shares):
                    raise ValueError("Duplicate share")

                gf_shares.append((idx, value))

            result = _Element(0)
            for j in range(k):
                x_j, y_j = gf_shares[j]

                numerator = _Element(1)
                denominator = _Element(1)

                for m in range(k):
                    x_m = gf_shares[m][0]
                    if m != j:
                        numerator *= x_m
                        denominator *= x_j + x_m
                result += y_j * numerator * denominator.inverse()
            return result.encode()

# 返回字节长度
def number_size (N):
    if N < 0:
        raise ValueError("Size in bits only available for non-negative numbers")
    return N.bit_length()

def is_native_int(x):
    return isinstance(x, (int, int))

# 使用大端模式，将正整数转为字节串
def long_to_bytes(n, blocksize=0):
    if n < 0 or blocksize < 0:
        raise ValueError("Values must be non-negative")

    result = []
    pack = struct.pack

    # Fill the first block independently from the value of n
    bsr = blocksize
    while bsr >= 8:
        result.insert(0, pack('>Q', n & 0xFFFFFFFFFFFFFFFF))
        n = n >> 64
        bsr -= 8

    while bsr >= 4:
        result.insert(0, pack('>I', n & 0xFFFFFFFF))
        n = n >> 32
        bsr -= 4

    while bsr > 0:
        result.insert(0, pack('>B', n & 0xFF))
        n = n >> 8
        bsr -= 1

    if n == 0:
        if len(result) == 0:
            bresult = b'\x00'
        else:
            bresult = b''.join(result)
    else:
        # The encoded number exceeds the block size
        while n > 0:
            result.insert(0, pack('>Q', n & 0xFFFFFFFFFFFFFFFF))
            n = n >> 64
        result[0] = result[0].lstrip(b'\x00')
        bresult = b''.join(result)
        # bresult has minimum length here
        if blocksize > 0:
            target_len = ((len(bresult) - 1) // blocksize + 1) * blocksize
            bresult = b'\x00' * (target_len - len(bresult)) + bresult

    return bresult

# 字节串转为正整数
def bytes_to_long(s):
    acc = 0

    unpack = struct.unpack

    # Up to Python 2.7.4, struct.unpack can't work with bytearrays nor
    # memoryviews
    if sys.version_info[0:3] < (2, 7, 4):
        if isinstance(s, bytearray):
            s = bytes(s)
        elif isinstance(s, memoryview):
            s = s.tobytes()

    length = len(s)
    if length % 4:
        extra = (4 - length % 4)
        s = b'\x00' * extra + s
        length = length + extra
    for i in range(0, length, 4):
        acc = (acc << 32) + unpack('>I', s[i:i+4])[0]
    return acc

# 生成随机字节流
def rng(num):
    return os.urandom(num)

def _mult_gf2(f1, f2):
    """Multiply two polynomials in GF(2)"""

    # Ensure f2 is the smallest
    if f2 > f1:
        f1, f2 = f2, f1
    z = 0
    while f2:
        if f2 & 1:
            z ^= f1
        f1 <<= 1
        f2 >>= 1
    return z

def _div_gf2(a, b):
    """
    Compute division of polynomials over GF(2).
    Given a and b, it finds two polynomials q and r such that:

    a = b*q + r with deg(r)<deg(b)
    """

    if (a < b):
        return 0, a

    deg = number_size
    q = 0
    r = a
    d = deg(b)
    while deg(r) >= d:
        s = 1 << (deg(r) - d)
        q ^= s
        r ^= _mult_gf2(b, s)
    return (q, r)


class _Element(object):
    """Element of GF(2^128) field"""

    # The irreducible polynomial defining this field is 1+x+x^2+x^7+x^128
    irr_poly = 1 + 2 + 4 + 128 + 2 ** 128

    def __init__(self, encoded_value):
        """Initialize the element to a certain value.

        The value passed as parameter is internally encoded as
        a 128-bit integer, where each bit represents a polynomial
        coefficient. The LSB is the constant coefficient.
        """

        if is_native_int(encoded_value):
            self._value = encoded_value
        elif len(encoded_value) == 16:
            self._value = bytes_to_long(encoded_value)
        else:
            raise ValueError("The encoded value must be an integer or a 16 byte string")

    def __eq__(self, other):
        return self._value == other._value

    def __int__(self):
        """Return the field element, encoded as a 128-bit integer."""
        return self._value

    def encode(self):
        """Return the field element, encoded as a 16 byte string."""
        return long_to_bytes(self._value, 16)

    def __mul__(self, factor):

        f1 = self._value
        f2 = factor._value

        # Make sure that f2 is the smallest, to speed up the loop
        if f2 > f1:
            f1, f2 = f2, f1

        if self.irr_poly in (f1, f2):
            return _Element(0)

        mask1 = 2 ** 128
        v, z = f1, 0
        while f2:
            # if f2 ^ 1: z ^= v
            mask2 = int(bin(f2 & 1)[2:] * 128, base=2)
            z = (mask2 & (z ^ v)) | ((mask1 - mask2 - 1) & z)
            v <<= 1
            # if v & mask1: v ^= self.irr_poly
            mask3 = int(bin((v >> 128) & 1)[2:] * 128, base=2)
            v = (mask3 & (v ^ self.irr_poly)) | ((mask1 - mask3 - 1) & v)
            f2 >>= 1
        return _Element(z)

    def __add__(self, term):
        return _Element(self._value ^ term._value)

    def inverse(self):
        """Return the inverse of this element in GF(2^128)."""

        # We use the Extended GCD algorithm
        # http://en.wikipedia.org/wiki/Polynomial_greatest_common_divisor

        if self._value == 0:
            raise ValueError("Inversion of zero")

        r0, r1 = self._value, self.irr_poly
        s0, s1 = 1, 0
        while r1 > 0:
            q = _div_gf2(r0, r1)[0]
            r0, r1 = r1, r0 ^ _mult_gf2(q, r1)
            s0, s1 = s1, s0 ^ _mult_gf2(q, s1)
        return _Element(s0)

    def __pow__(self, exponent):
        result = _Element(self._value)
        for _ in range(exponent - 1):
            result = result * self
        return result

# 文件加密
# path_set 可以为 路径字符串 或者 集合
def file_enc(key, path, path_set):
    iv = bytearray(16)
    epath_set = []

    try:
        fr = open(path, "rb")
        data = fr.read()

        iv = os.urandom(16)

        sm4_enc = CryptSM4()
        sm4_enc.set_key(key, SM4_ENCRYPT)

        enc_data = sm4_enc.crypt_cbc(iv, data)

        if type(path_set) == type("1"):
            # 随机设定文件名
            flag = True
            while flag:
                rnd_name = random_hex(16)
                if os.path.exists(path_set + "/" + rnd_name + ".dat"):
                    flag = True
                else:
                    flag = False
            epath = path_set + "/" + rnd_name + ".dat"
            fw = open(epath, "wb")
            fw.write(iv)
            fw.write(enc_data)
            fw.close()
            epath_set.append(epath)
        else:
            # 随机设定文件名
            flag = True
            while flag:
                rnd_name = random_hex(16)
                if os.path.exists(path_set[0] + "/" + rnd_name + ".dat"):
                    flag = True
                else:
                    flag = False
            epath = path_set[0] + "/" + rnd_name + ".dat"

            fw = open(epath, "wb")
            fw.write(iv)
            fw.write(enc_data)
            fw.close()
            epath_set.append(epath)

            # 密文拷贝到副本位置
            for i in range(1,len(path_set)):
                flag = True
                while flag:
                    rnd_name = random_hex(16)
                    if os.path.exists(path_set[i] + "/" + rnd_name + ".dat"):
                        flag = True
                    else:
                        flag = False
                cpath = path_set[i] + "/" + rnd_name + ".dat"
                shutil.copy(epath, cpath)
                epath_set.append(cpath)
    except Exception as e:
        print("文件打开失败：", str(e))
    finally:
        fr.close()
        # 原文件删除 ***删除操作***
        os.remove(path)
        return epath_set

# 文件解密
def file_dec(key, path, fname, dpath="."):
    data = bytearray(256)
    iv = bytearray(16)
    try:
        fr = open(path, "rb")
        data = fr.read()

        iv = data[:16]

        sm4_dec = CryptSM4()
        sm4_dec.set_key(key, SM4_DECRYPT)
        dec_data = sm4_dec.crypt_cbc(iv, data[16:])

        fw = open(dpath+"/"+fname, "wb")
        fw.write(dec_data)
    except Exception as e:
        print("文件打开失败：", str(e))
    finally:
        fr.close()
        fw.close()

# 将密钥写入文件记录
def save_K(key, path):
    try:
        fw = open(path, "wb")
        fw.write(key)
    except Exception as e:
        print("文件打开失败：", str(e))
    finally:
        fw.close()

def read_K(path, key):
    try:
        fr = open(path, "rb")
        key[:] = fr.read()
    except Exception as e:
        print("密钥读取失败：", str(e))
    finally:
        fr.close()

# 删除文件 ***删除操作***
def del_file(path, del_method, vrf, level):
    # os.remove(path)
    overwriter=VideoOverwriter(vrf, level)
    if del_method=="overwrittenDelete":
        overwriter.overwrite_file([path])
        print(f"已经完成对{path}的覆写")

    elif del_method=="commandDelete":
        overwriter.command_delete([path])
        print(f"已经完成对{path}的删除")
        # other delete method

# 更新密文文件字段
def update_field(old_fkey, fkey, field, old_path_set, path_set, del_method, vrf, level):
    data = bytearray(256)
    _data = {}
    epath = path_set[0]
    path_set.remove(epath)

    # 解密
    try:
        fr = open(old_path_set[0], "rb")
        data = fr.read()

        iv = data[:16]

        sm4_dec = CryptSM4()
        sm4_dec.set_key(old_fkey, SM4_DECRYPT)
        dec_data = sm4_dec.crypt_cbc(iv, data[16:])

        _data = json.loads(dec_data.decode())

    except IOError as e:
        print(old_path_set[0], "文件打开失败：", str(e))
    finally:
        fr.close()

    # 删除字段
    if field in _data:
        del _data[field]
    else:
        print(field, "字段不存在！")

    # 加密并存储
    iv = os.urandom(16)

    sm4_enc = CryptSM4()
    sm4_enc.set_key(fkey, SM4_ENCRYPT)

    _enc_data = sm4_enc.crypt_cbc(iv, json.dumps(_data, indent=4).encode())
    fw = open(epath, "wb")
    fw.write(iv)
    fw.write(_enc_data)
    fw.close()

    # ***删除操作***
    for fp in old_path_set:
        del_file(fp,  del_method, vrf, level)
    # 存储副本
    for fp in path_set:
        shutil.copy(epath, fp)

xor = lambda a, b:list(map(lambda x, y: x ^ y, a, b))

rotl = lambda x, n:((x << n) & 0xffffffff) | ((x >> (32 - n)) & 0xffffffff)

get_uint32_be = lambda key_data:((key_data[0] << 24) | (key_data[1] << 16) | (key_data[2] << 8) | (key_data[3]))

put_uint32_be = lambda n:[((n>>24)&0xff), ((n>>16)&0xff), ((n>>8)&0xff), ((n)&0xff)]

pkcs7_padding = lambda data, block=16: data + [(16 - len(data) % block)for _ in range(16 - len(data) % block)]

zero_padding = lambda data, block=16: data + [0 for _ in range(16 - len(data) % block)]

pkcs7_unpadding = lambda data: data[:-data[-1]]

zero_unpadding = lambda data,i =1:data[:-i] if data[-i] == 0 else i+1

list_to_bytes = lambda data: b''.join([bytes((i,)) for i in data])

bytes_to_list = lambda data: [i for i in data]

random_hex = lambda x: ''.join([choice('0123456789abcdef') for _ in range(x)])

IV = [
    1937774191, 1226093241, 388252375, 3666478592,
    2842636476, 372324522, 3817729613, 2969243214,
]

T_j = [
    2043430169, 2043430169, 2043430169, 2043430169, 2043430169, 2043430169,
    2043430169, 2043430169, 2043430169, 2043430169, 2043430169, 2043430169,
    2043430169, 2043430169, 2043430169, 2043430169, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042, 2055708042, 2055708042,
    2055708042, 2055708042, 2055708042, 2055708042
]

def sm3_ff_j(x, y, z, j):
    if 0 <= j and j < 16:
        ret = x ^ y ^ z
    elif 16 <= j and j < 64:
        ret = (x & y) | (x & z) | (y & z)
    return ret

def sm3_gg_j(x, y, z, j):
    if 0 <= j and j < 16:
        ret = x ^ y ^ z
    elif 16 <= j and j < 64:
        #ret = (X | Y) & ((2 ** 32 - 1 - X) | Z)
        ret = (x & y) | ((~ x) & z)
    return ret

def sm3_p_0(x):
    return x ^ (rotl(x, 9 % 32)) ^ (rotl(x, 17 % 32))

def sm3_p_1(x):
    return x ^ (rotl(x, 15 % 32)) ^ (rotl(x, 23 % 32))

def sm3_cf(v_i, b_i):
    w = []
    for i in range(16):
        weight = 0x1000000
        data = 0
        for k in range(i*4,(i+1)*4):
            data = data + b_i[k]*weight
            weight = int(weight/0x100)
        w.append(data)

    for j in range(16, 68):
        w.append(0)
        w[j] = sm3_p_1(w[j-16] ^ w[j-9] ^ (rotl(w[j-3], 15 % 32))) ^ (rotl(w[j-13], 7 % 32)) ^ w[j-6]
        str1 = "%08x" % w[j]
    w_1 = []
    for j in range(0, 64):
        w_1.append(0)
        w_1[j] = w[j] ^ w[j+4]
        str1 = "%08x" % w_1[j]

    a, b, c, d, e, f, g, h = v_i

    for j in range(0, 64):
        ss_1 = rotl(
            ((rotl(a, 12 % 32)) +
             e +
             (rotl(T_j[j], j % 32))) & 0xffffffff, 7 % 32
        )
        ss_2 = ss_1 ^ (rotl(a, 12 % 32))
        tt_1 = (sm3_ff_j(a, b, c, j) + d + ss_2 + w_1[j]) & 0xffffffff
        tt_2 = (sm3_gg_j(e, f, g, j) + h + ss_1 + w[j]) & 0xffffffff
        d = c
        c = rotl(b, 9 % 32)
        b = a
        a = tt_1
        h = g
        g = rotl(f, 19 % 32)
        f = e
        e = sm3_p_0(tt_2)

        a, b, c, d, e, f, g, h = map(
            lambda x:x & 0xFFFFFFFF ,[a, b, c, d, e, f, g, h])

    v_j = [a, b, c, d, e, f, g, h]
    return [v_j[i] ^ v_i[i] for i in range(8)]

def sm3_hash(msg):
    # print(msg)
    len1 = len(msg)
    reserve1 = len1 % 64
    msg.append(0x80)
    reserve1 = reserve1 + 1
    # 56-64, add 64 byte
    range_end = 56
    if reserve1 > range_end:
        range_end = range_end + 64

    for i in range(reserve1, range_end):
        msg.append(0x00)

    bit_length = (len1) * 8
    bit_length_str = [bit_length % 0x100]
    for i in range(7):
        bit_length = int(bit_length / 0x100)
        bit_length_str.append(bit_length % 0x100)
    for i in range(8):
        msg.append(bit_length_str[7-i])

    group_count = round(len(msg) / 64)

    B = []
    for i in range(0, group_count):
        B.append(msg[i*64:(i+1)*64])

    V = []
    V.append(IV)
    for i in range(0, group_count):
        V.append(sm3_cf(V[i], B[i]))

    y = V[i+1]
    result = ""
    for i in y:
        result = '%s%08x' % (result, i)
    return result

def sm3_kdf(z, klen): # z为16进制表示的比特串（str），klen为密钥长度（单位byte）
    print("in", z)
    klen = int(klen)
    ct = 0x00000001
    rcnt = ceil(klen/32)
    tt = bytes.fromhex(z.decode('utf8'))
    print(tt.hex())
    print("!#", bytes.fromhex(z.decode('utf8')))
    zin = [i for i in bytes.fromhex(z.decode('utf8'))]
    ha = ""
    for i in range(rcnt):
        msg = zin  + [i for i in binascii.a2b_hex(('%08x' % ct).encode('utf8'))]
        ha = ha + sm3_hash(msg)
        ct += 1
    return ha[0: klen * 2]

# Expanded SM4 box table
SM4_BOXES_TABLE = [
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c,
    0x05, 0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86,
    0x06, 0x99, 0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed,
    0xcf, 0xac, 0x62, 0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa,
    0x75, 0x8f, 0x3f, 0xa6, 0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c,
    0x19, 0xe6, 0x85, 0x4f, 0xa8, 0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb,
    0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35, 0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25,
    0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87, 0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52,
    0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e, 0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38,
    0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1, 0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34,
    0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3, 0x1d, 0xf6, 0xe2, 0x2e, 0x82,
    0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f, 0xd5, 0xdb, 0x37, 0x45,
    0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51, 0x8d, 0x1b, 0xaf,
    0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8, 0x0a, 0xc1,
    0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0, 0x89,
    0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
    0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39,
    0x48,
]

# System parameter
SM4_FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]

# fixed parameter
SM4_CK = [
    0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
    0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
    0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
    0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
    0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
    0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
    0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
    0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
]

SM4_ENCRYPT = 0
SM4_DECRYPT = 1

PKCS7 = 0
ZERO = 1

class CryptSM4(object):

    def __init__(self, mode=SM4_ENCRYPT, padding_mode=PKCS7):
        self.sk = [0] * 32
        self.mode = mode
        self.padding_mode = padding_mode
    # Calculating round encryption key.
    # args:    [in] a: a is a 32 bits unsigned value;
    # return: sk[i]: i{0,1,2,3,...31}.

    @classmethod
    def _round_key(cls, ka):
        b = [0, 0, 0, 0]
        a = put_uint32_be(ka)
        b[0] = SM4_BOXES_TABLE[a[0]]
        b[1] = SM4_BOXES_TABLE[a[1]]
        b[2] = SM4_BOXES_TABLE[a[2]]
        b[3] = SM4_BOXES_TABLE[a[3]]
        bb = get_uint32_be(b[0:4])
        rk = bb ^ (rotl(bb, 13)) ^ (rotl(bb, 23))
        return rk

    # Calculating and getting encryption/decryption contents.
    # args:    [in] x0: original contents;
    # args:    [in] x1: original contents;
    # args:    [in] x2: original contents;
    # args:    [in] x3: original contents;
    # args:    [in] rk: encryption/decryption key;
    # return the contents of encryption/decryption contents.
    @classmethod
    def _f(cls, x0, x1, x2, x3, rk):
        # "T algorithm" == "L algorithm" + "t algorithm".
        # args:    [in] a: a is a 32 bits unsigned value;
        # return: c: c is calculated with line algorithm "L" and nonline
        # algorithm "t"
        def _sm4_l_t(ka):
            b = [0, 0, 0, 0]
            a = put_uint32_be(ka)
            b[0] = SM4_BOXES_TABLE[a[0]]
            b[1] = SM4_BOXES_TABLE[a[1]]
            b[2] = SM4_BOXES_TABLE[a[2]]
            b[3] = SM4_BOXES_TABLE[a[3]]
            bb = get_uint32_be(b[0:4])
            c = bb ^ (
                rotl(
                    bb,
                    2)) ^ (
                    rotl(
                        bb,
                        10)) ^ (
                    rotl(
                        bb,
                        18)) ^ (
                    rotl(
                        bb,
                        24))
            return c
        return (x0 ^ _sm4_l_t(x1 ^ x2 ^ x3 ^ rk))

    def set_key(self, key, mode):
        key = bytes_to_list(key)
        MK = [0, 0, 0, 0]
        k = [0] * 36
        MK[0] = get_uint32_be(key[0:4])
        MK[1] = get_uint32_be(key[4:8])
        MK[2] = get_uint32_be(key[8:12])
        MK[3] = get_uint32_be(key[12:16])
        k[0:4] = xor(MK[0:4], SM4_FK[0:4])
        for i in range(32):
            k[i + 4] = k[i] ^ (
                self._round_key(k[i + 1] ^ k[i + 2] ^ k[i + 3] ^ SM4_CK[i]))
            self.sk[i] = k[i + 4]
        self.mode = mode
        if mode == SM4_DECRYPT:
            for idx in range(16):
                t = self.sk[idx]
                self.sk[idx] = self.sk[31 - idx]
                self.sk[31 - idx] = t

    def one_round(self, sk, in_put):
        out_put = []
        ulbuf = [0] * 36
        ulbuf[0] = get_uint32_be(in_put[0:4])
        ulbuf[1] = get_uint32_be(in_put[4:8])
        ulbuf[2] = get_uint32_be(in_put[8:12])
        ulbuf[3] = get_uint32_be(in_put[12:16])
        for idx in range(32):
            ulbuf[idx + 4] = self._f(ulbuf[idx],
                                     ulbuf[idx + 1],
                                     ulbuf[idx + 2],
                                     ulbuf[idx + 3],
                                     sk[idx])

        out_put += put_uint32_be(ulbuf[35])
        out_put += put_uint32_be(ulbuf[34])
        out_put += put_uint32_be(ulbuf[33])
        out_put += put_uint32_be(ulbuf[32])
        return out_put

    def crypt_ecb(self, input_data):
        # SM4-ECB block encryption/decryption
        input_data = bytes_to_list(input_data)
        if self.mode == SM4_ENCRYPT:
            if self.padding_mode == PKCS7:
                input_data = pkcs7_padding(input_data)
            elif self.padding_mode == ZERO:
                input_data = zero_padding(input_data)

        length = len(input_data)
        i = 0
        output_data = []
        while length > 0:
            output_data += self.one_round(self.sk, input_data[i:i + 16])
            i += 16
            length -= 16
        if self.mode == SM4_DECRYPT:
            if self.padding_mode == PKCS7:
                return list_to_bytes(pkcs7_unpadding(output_data))
            elif self.padding_mode == ZERO:
                return list_to_bytes(zero_unpadding(output_data))
        return list_to_bytes(output_data)

    def crypt_cbc(self, iv, input_data):
        # SM4-CBC buffer encryption/decryption
        i = 0
        output_data = []
        tmp_input = [0] * 16
        iv = bytes_to_list(iv)
        if self.mode == SM4_ENCRYPT:
            input_data = pkcs7_padding(bytes_to_list(input_data))
            length = len(input_data)
            while length > 0:
                tmp_input[0:16] = xor(input_data[i:i + 16], iv[0:16])
                output_data += self.one_round(self.sk, tmp_input[0:16])
                iv = copy.deepcopy(output_data[i:i + 16])
                i += 16
                length -= 16
            return list_to_bytes(output_data)
        else:
            length = len(input_data)
            while length > 0:
                output_data += self.one_round(self.sk, input_data[i:i + 16])
                output_data[i:i + 16] = xor(output_data[i:i + 16], iv[0:16])
                iv = copy.deepcopy(input_data[i:i + 16])
                i += 16
                length -= 16
            return list_to_bytes(pkcs7_unpadding(output_data))

def gen_key():
    rnd = os.urandom(8)
    key = int.from_bytes(rnd, byteorder='big')
    return key

if __name__ == "__main__":
    # 测试
    secret_share = SecretShare()
    # 生成 128 位（16 字节）的密钥
    key = rng(16)
    print("原密钥：", key.hex())

    t = 2
    n = 3
    # 生成密钥分片
    shares = secret_share.generate_shares(key,t, n )
    print(shares)

    # 重构密钥
    n_key = secret_share.reconstruct_key(shares[:t], t, n)
    print("重构的密钥1：", n_key.hex())

    t_shares = []
    t_shares.append((1,shares[1][1]))
    t_shares.append((2,shares[2][1]))
    print(t_shares)
    t_key = secret_share.reconstruct_key(t_shares, t, n)
    print("重构的密钥2：", t_key.hex())
