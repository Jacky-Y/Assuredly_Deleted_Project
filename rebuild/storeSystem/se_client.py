import os
import json
import copy
from math import ceil
from random import choice
import pymysql

# SSE的客户端部分
class SEClient:
    # 声明SSE的密钥和本地状态计数器
    def __init__(self, isLoad=False):
        self.k_sm4 = bytearray(16)
        self.s = bytearray(16)
        self.count = {}

        self.isLoad = isLoad

        # 本地状态也存储到数据库中cnt表中
        self.db = 'edb'
        # 创建mysql连接对象
        try:
            self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456')
            # self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='password')
            # print("成功连接到MySQL服务器！")
        except Exception as e:
            print("无法连接到MySQL服务器：", str(e))
        # 获取游标对象
        self.cursor = self.conn.cursor()
        # 关闭自动提交事务
        self.conn.autocommit(False)

        self.setup(isLoad)

    # 销毁类的析构函数
    def __del__(self):
        # 如果非加载构建SE，保存密钥
        if self.isLoad is False:
            self.save_K()

        # 关闭mysql连接
        if self.cursor:
            self.cursor.close()
        if self.conn.open:
            self.conn.close()

        for it in self.count:
            del it

    # 创建edb数据库，创建cnt，cipher，grp表
    def db_init(self, isDel):
        if isDel is True:
            # 查看是否先启动的server
            sql = f"USE {self.db}"
            self.cursor.execute(sql)

            sql = f"SELECT * FROM cnt"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            # 如果server已经重建，则不用再建
            if result is None:
                return

            # 删除edb
            sql = f"DROP DATABASE {self.db}"
            self.cursor.execute(sql)

        # 再创建edb
        sql = f"CREATE DATABASE {self.db}"
        self.cursor.execute(sql)

        # 转到edb
        sql = f"USE {self.db}"
        self.cursor.execute(sql)

        self.conn.commit()

        # 创建cnt，cipher，grp共3张表
        try:
            # 创建cnt表
            sql = '''CREATE TABLE cnt (
                                Kw VARCHAR(64) PRIMARY KEY,
                                Sr INTEGER ,
                                Cn INTEGER )'''
            self.cursor.execute(sql)

            #创建cipher表
            sql = '''CREATE TABLE cipher (
                                L VARCHAR(64) PRIMARY KEY,
                                D TEXT,
                                C TEXT)'''
            self.cursor.execute(sql)

            # 创建grp表
            sql = '''CREATE TABLE grp (
                                Iw VARCHAR(64) PRIMARY KEY,
                                Cw LONGTEXT)'''
            self.cursor.execute(sql)
        except Exception as e:
            print("创建表格时发生错误:", str(e))
        self.conn.commit()


    # 初始化SSE的密钥和本地状态计数器
    def setup(self, isLoad=False):

        # 判断数据库edb是否存在
        self.cursor.execute("SHOW DATABASES")
        result = self.cursor.fetchall()
        dbs = [row[0] for row in result]

        # 如果数据库edb不存在，则创建edb及3张表
        if self.db not in dbs:
            # 创建edb及3张表
            self.db_init(False)
            # 数据库不存在时，SE密钥强制更换
            self.isLoad = False
            self.k_sm4 = os.urandom(16)
            self.s = os.urandom(16)
            return

        # 如果不加载，则删除并重建edb
        if isLoad is False:
            self.db_init(True)
            # 初始化密钥
            self.k_sm4 = os.urandom(16)
            self.s = os.urandom(16)
        else:
            self.set_K()
            # 直接加载edb
            sql = f"USE {self.db}"
            self.cursor.execute(sql)

            self.conn.commit()

    # 装载指定密钥
    def set_K(self, path="./se_key.pem"):
        try:
            fw = open(path, "rb")
            data = fw.read()
            self.k_sm4 = data[:16]
            self.s = data[16:]
        except Exception as e:
            print(path,"文件打开失败：", str(e))
        finally:
            fw.close()

    # 存储当前密钥
    def save_K(self, path="./se_key.pem"):
        # 密钥文件存在时，先删除
        if os.path.exists(path):
            os.remove(path)
        # 密钥存储到指定路径
        if path == "./se_key.pem":
            fw = os.open(path, os.O_WRONLY|os.O_CREAT)
            os.write(fw, self.k_sm4)
            os.write(fw, self.s)
            os.close(fw)
        else:
            try:
                fw = os.open(path, os.O_WRONLY|os.O_CREAT)
                os.write(fw, self.k_sm4)
                os.write(fw, self.s)
            except Exception as e:
                print(path, "文件打开失败：", str(e))
            finally:
                os.close(fw)

    # 存储当前本地状态
    def save_State(self, path="./local_state.json"):
        # 文件存在时，先删除
        if os.path.exists(path):
            os.remove(path)

        json_str = json.dumps(self.count)
        if path == "./local_state.json":
            fw = os.open(path, os.O_WRONLY|os.O_CREAT)
            os.write(fw, json_str.encode())
            os.close(fw)
        else:
            try:
                fw = os.open(path, os.O_WRONLY|os.O_CREAT)
                os.write(fw, json_str.encode())
            except Exception as e:
                print(path, "文件打开失败：", str(e))
            finally:
                os.close(fw)

    # 装载本地状态
    def load_State(self, path="./local_state.json"):
        try:
            fw = open(path, "r")
            self.count = json.load(fw)
        except Exception as e:
            print(path,"文件打开失败：", str(e))
        finally:
            fw.close()

    # 256-bit哈希，计算Group的索引
    def _hash_G(self, K, keyword, ind, out):
        _s = keyword + ind

        sm3_in = bytes_to_list(K + _s.encode())
        sm3_out = sm3_hash(sm3_in)

        out[:] = bytes.fromhex(sm3_out)

    # 512-bit哈希，计算L||D
    def _hash_H(self, K, c, out):
        buf1 = bytearray(32)

        buf1[:16] = K[:16]
        buf1[16:] = bytes("::" + str(c), 'utf-8')

        sm3_in1 = bytes_to_list(b'0#'+ buf1)
        sm3_in2 = bytes_to_list(b'1#'+ buf1)

        sm3_out1 = sm3_hash(sm3_in1)
        sm3_out2 = sm3_hash(sm3_in2)

        out[:32] = bytes.fromhex(sm3_out1)
        out[32:64] = bytes.fromhex(sm3_out2)

    # 加密文件存储地址
    def _encrypt_id(self, ind, _IV, c):
        iv = bytearray(16)
        buf1 = bytearray(64)

        buf1 = ind.encode('utf-8')

        iv = os.urandom(16)
        _IV[:] = iv[:16]

        sm4_enc = CryptSM4()

        sm4_enc.set_key(self.k_sm4, SM4_ENCRYPT)

        c[:] = sm4_enc.crypt_cbc(iv, buf1)

    # 解密文件存储地址
    def decrypt(self, enc_ind, result):
        # 先清空输出，防止结果被干扰
        result.clear()

        sm4_dec = CryptSM4()

        sm4_dec.set_key(self.k_sm4, SM4_DECRYPT)

        for a in enc_ind:
            iv = a[:16]

            decrypted_data = sm4_dec.crypt_cbc(iv, a[16:])
            _data = decrypted_data.decode()

            result.append(_data)

    # 计算PRF，基于HMAC与SM3设计
    def _prf_F(self, keyword, c, out, is_1=False):
        k_mac = bytearray(64)
        k_xor = bytearray(64)

        if is_1:
            buffer = "--111"
        else:
            buffer = "::" + str(c)

        msg = keyword + buffer
        hmac_in = msg.encode()

        # 密钥处理
        if len(self.s) > 64:
            sm3_in = bytes_to_list(self.s)
            sm3_out = sm3_hash(sm3_in)
            k_mac = bytes.fromhex(sm3_out)
        else:
            k_mac = self.s + b''.join((b'\x00',)*(64 - len(self.s)))

        # KEY XOR ipad
        for i in range(64):
            k_xor[i] = k_mac[i] ^ 0x36

        sm3_in = bytes_to_list(k_xor + hmac_in)
        sm3_out = sm3_hash(sm3_in)

        sm3_in2 = bytes.fromhex(sm3_out)

        # KEY XOR opad
        for i in range(64):
            k_xor[i] = k_mac[i] ^ 0x5C

        sm3_in = bytes_to_list(k_xor + sm3_in2)
        sm3_out = sm3_hash(sm3_in)

        out[:] = bytes.fromhex(sm3_out)

    # 添加/删除SSE密文
    def update(self, keyword, ind, op, L, D, _IV, C):
        K = bytearray(32)
        K_1 = bytearray(32)
        cip_id = bytearray(64)
        buf = bytearray(64)

        # 查询计数器状态
        sql = f"SELECT * FROM cnt WHERE Kw=%s"
        self.cursor.execute(sql, keyword)

        result = self.cursor.fetchone()

        if result is None:
            _sr = 0
            _cn = 1
            sql = f"INSERT INTO cnt (Kw, Sr, Cn) VALUES (%s,%s,%s)"
            self.cursor.execute(sql, (keyword, _sr, _cn))
        else:
            _sr = result[1]
            _cn = result[2] + 1
            sql = f"UPDATE cnt SET Sr=%s,Cn=%s WHERE Kw=%s"
            self.cursor.execute(sql, (_sr, _cn, keyword))
        self.conn.commit()

        # if keyword not in self.count:
        #     self.count[keyword] = {'cnt_srch': 0, 'cnt_upd': 0}

        # self.count[keyword]['cnt_upd'] += 1
        # cnt_upd = self.count[keyword]['cnt_upd']

        self._prf_F(keyword, _sr, K)
        self._prf_F(keyword, 0, K_1, True)

        self._hash_H(K, _cn, buf)
        L[:] = buf[:32]
        D[:] = buf[32:64]

        self._hash_G(K_1, keyword, ind, cip_id)
        if op == "Add":
            cip_id[0] = 0xff
        else:
            cip_id[0] = 0x00
        for i in range(32):
            D[i] ^= cip_id[i]

        self._encrypt_id(ind, _IV, C)

    # 生成SSE搜索令牌
    def trapdoor(self, keyword, cnt_upd, K, loc_grp):
        # c = {'cnt_srch': 0, 'cnt_upd': 0}
        K_1 = bytearray(32)

        # 查询计数器状态
        sql = f"SELECT * FROM cnt WHERE Kw=%s"
        self.cursor.execute(sql, keyword)

        result = self.cursor.fetchone()

        if result is None:
            print(keyword, "无匹配记录")
            cnt_upd[0] = -1
            return 0
        # if keyword not in self.count:
        #     return 0

        _sr = result[1]
        _cn = result[2]

        self._prf_F(keyword, _sr, K)
        self._prf_F(keyword, 0, K_1, True)

        _sr += 1
        cnt_upd[0] = _cn
        _cn = 0

        sql = f"UPDATE cnt SET Sr=%s,Cn=%s WHERE Kw=%s"
        self.cursor.execute(sql, (_sr, _cn, keyword))
        self.conn.commit()

        self._hash_G(K_1, keyword, "", loc_grp)

        return 1

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

# z为16进制表示的比特串（str），klen为密钥长度（单位byte）
def sm3_kdf(z, klen):
    klen = int(klen)
    ct = 0x00000001
    rcnt = ceil(klen/32)
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

# 系统参数
SM4_FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]

# 固定参数
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

# 国密SM4加密
class CryptSM4(object):

    def __init__(self, mode=SM4_ENCRYPT, padding_mode=PKCS7):
        self.sk = [0] * 32
        self.mode = mode
        self.padding_mode = padding_mode

    # 计算轮密钥
    # 输入：32bit无符号值
    # 输出：32字节的密钥
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

    # 输入：x0,x1,x2,x3是原内容，rk是加密/解密密钥
    # 计算并得到加密/解密内容
    @classmethod
    def _f(cls, x0, x1, x2, x3, rk):
        # "T 算法" == "L 算法" + "t 算法".
        # 输入：32 bits 无符号数值
        # 输出：c: c用线性算法"L"和非线性算法"t"计算
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

    # 初始化密钥
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

    # 一轮计算
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

    # ECB加密模式
    def crypt_ecb(self, input_data):

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

    # CBC加密模式
    def crypt_cbc(self, iv, input_data):

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

# 调试样例
# 正确输出为：Decrypted result: [b'/Users/xx/xx/xx/xx/xx/xx/xx/xx.json', b'/Users/xx/xx/xx/xx/xx/xx/xx/xx.json']
if __name__ == "__main__":
    client = SEClient(isLoad=False)
    # client.setup()

    L = bytearray(32)
    D = bytearray(32)
    _IV = bytearray(16)
    C = bytearray(64)
    tmp = bytearray(80)

    client.update("keyword", "/Users/xx/xx/xx/xx/xx/xx/xx/xx.json", "Add", L, D, _IV, C)
    print(len(L), "L:", L)
    print(len(D), "D:", D)
    print(len(_IV), "IV:", _IV)
    print(len(C), "C:", C)

    cnt_upd = [0]
    K = bytearray(32)
    loc_grp = bytearray(32)
    trapdoor_result = client.trapdoor("keyword", cnt_upd, K, loc_grp)
    print("Trapdoor result:", trapdoor_result)
    print(len(K), "K:", K)
    print(len(loc_grp), "loc_grp:", loc_grp)


    tmp[:16] = _IV
    tmp[16:80] = C
    enc_ind = [tmp,tmp]
    result = []
    client.decrypt(enc_ind, result)
    print("Decrypted result:", result)

    client.save_K();
    client.save_State();

    client.set_K();
    client.load_State();