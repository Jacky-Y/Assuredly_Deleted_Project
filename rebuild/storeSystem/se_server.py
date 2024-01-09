import hashlib
from typing import List, Dict, Union
import pymysql
from math import ceil
import binascii
import json

class SECipher:
    # SSE的密文结构
    def __init__(self):
        self.D = bytes(32)
        self.IV = bytes(16)
        self.C = bytes(64)

class SEServer:
    # 声明SSE的服务器EDB
    def __init__(self, isdel=True):
        self.cipher_db: Dict[bytes, SECipher] = {}
        self.GRP: Dict[bytes, Dict[bytes, bytes]] = {}
        self.if_cleaning = False
        self.p_clean_thread = None
        self.db = 'edb'
        # 创建连接对象
        try:
            self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456')
            # self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='password')
            print("成功连接到MySQL服务器！")
        except Exception as e:
            print("无法连接到MySQL服务器：", str(e))
        # 获取游标对象
        self.cursor = self.conn.cursor()
        # 关闭自动提交事务
        self.conn.autocommit(False)

        self.setup(isdel)

    # 销毁类的析构函数
    def __del__(self):
        for a in self.cipher_db.values():
            del a
        self.cipher_db.clear()
        self.GRP.clear()

        self.cursor.close()
        if self.conn.open:
            self.conn.close()

    # 清空mysql的EDB包括cipher和group两张表
    # 存在就删除，不存在不做
    def drop_edb(self):
        # 判断数据库edb是否存在
        self.cursor.execute("SHOW DATABASES")
        result = self.cursor.fetchall()
        dbs = [row[0] for row in result]

        # 如果数据库edb存在，删除
        if self.db in dbs:
            sql = f"DROP DATABASE {self.db}"
            # 删除edb
            self.cursor.execute(sql)
            sql = f"CREATE DATABASE {self.db}"

    # 初始化EDB
    def setup(self, isdel=True) -> int:
        for a in self.cipher_db.values():
            del a
        self.cipher_db.clear()
        self.GRP.clear()

        self.if_cleaning = False

        if isdel is True:
            self.drop_edb()

            # 新建edb
            sql = f"CREATE DATABASE {self.db}"
            self.cursor.execute(sql)
            self.conn.commit()
            # 使用edb数据库
            sql = f"USE {self.db}"
            # 执行 SQL 语句
            self.cursor.execute(sql)

            # 设置字符集为Latin-1
            # self.cursor.execute("SET NAMES 'latin1'")
            # 提交事务
            self.conn.commit()
        else:
            # 判断数据库edb是否存在
            self.cursor.execute("SHOW DATABASES")
            result = self.cursor.fetchall()
            dbs = [row[0] for row in result]
            # 如果edb不存在，新建
            if self.db not in dbs:
                sql = f"CREATE DATABASE {self.db}"
                # 执行 SQL 语句
                self.cursor.execute(sql)

            # 如果存在，即直接使用edb数据库
            sql = f"USE {self.db}"
            # 执行 SQL 语句
            self.cursor.execute(sql)

        sql = "SHOW TABLES LIKE 'cipher'"
        self.cursor.execute(sql)
        self.conn.commit()
        result = self.cursor.fetchone()

        if result is None:
            # 创建EDB的cipher部分，条目L，D，C
            try:
                sql = '''CREATE TABLE cipher (
                                L VARCHAR(64) PRIMARY KEY,
                                D TEXT,
                                C TEXT)'''
                self.cursor.execute(sql)
                self.conn.commit()
            except Exception as e:
                print("创建表格时发生错误:", str(e))

        sql = "SHOW TABLES LIKE 'grp'"
        self.cursor.execute(sql)
        self.conn.commit()
        result = self.cursor.fetchone()

        if result is None:
            # 创建EDB的group部分，条目Iw，{X，C}
            try:
                sql = '''CREATE TABLE grp (
                                Iw VARCHAR(64) PRIMARY KEY,
                                Cw LONGTEXT)'''
                self.cursor.execute(sql)
                self.conn.commit()
            except Exception as e:
                print("创建表格时发生错误:", str(e))

        return 1

    # 服务器端执行搜索
    def search(self, cnt_upd: int, K: bytes, loc_grp: bytes, ret: List[bytes]) -> int:
        H_rslt = bytearray(36)
        buf = bytearray(80)
        _l = bytes(64)
        D = set()
        T = []
        L = []
        # _l_grp = bytes(loc_grp)
        # grp = self.GRP.get(_l_grp, {})

        grp_name = loc_grp.hex()

        sql = f"SELECT * FROM grp WHERE Iw='{grp_name}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()

        if result is None:
            _grp = {}
            sql = f"INSERT INTO grp (Iw,Cw) VALUES ('{grp_name}', '')"
            self.cursor.execute(sql)
            self.conn.commit()
        else:
            # print(result)
            _grp = json.loads(result[1])

        for i in range(cnt_upd, 0, -1):
            self._hash_H(K, i, buf)

            _l = buf[:32]
            # if _l not in self.cipher_db:
            #     print("l is not in cipher_db")
            #     return 0
            #
            # p_c = self.cipher_db[_l]
            _L = _l.hex()
            sql = f"SELECT * FROM cipher WHERE L='{_L}'"
            self.cursor.execute(sql)
            #获取一行的值
            row = self.cursor.fetchone()

            if row is None:
                print("ERROR: l is not in cipher_db")
                return 0

            _D = bytes.fromhex(row[1])
            _C = row[2]

            # for j in range(32):
            #     H_rslt[j] = p_c.D[j] ^ buf[j + 32]
            for j in range(32):
                H_rslt[j] = _D[j] ^ buf[j + 32]

            # 解析是添加/删除操作
            if H_rslt[0] == 0x00:
                # del 记录删除token，并删除group中对应密文
                _l1 = bytes(H_rslt[1:32])
                _X = _l1.hex()
                D.add(_l1)
                # grp.pop(_l1, None)

                # 删除grp中对应内容，如果存在
                if _X in _grp.keys():
                    del _grp[_X]
            elif H_rslt[0] == 0xff:
                # add 记录上次搜索后的有效密文
                _l1 = bytes(H_rslt[1:32])
                _X = _l1.hex()
                if _l1 not in D:
                    # _c = SECipher()
                    # _c.D = bytes(H_rslt[1:32])
                    # _c.C = p_c.C[:]
                    # _c.IV = p_c.IV[:]
                    T.append((_X, _C))
            else:
                print("search process error, data damaged")
                return 0

            # del self.cipher_db[_l]
            # del p_c
            sql = f"DELETE FROM cipher WHERE L='{_L}'"
            self.cursor.execute(sql)
            self.conn.commit()


        # group中剩余密文为有效结果
        # for it in grp.values():
        #     ret.append(it)
        for _x,_c in _grp.items():
            _c_out = bytes.fromhex(_c)
            ret.append(_c_out)

        # 更新group，有效结果还包含上次搜索后的密文
        for _x,_c in T:
            _c_out = bytes.fromhex(_c)
            ret.append(_c_out)
            # 添加本次查询到group
            _grp[_x] = _c
            # _l = it.D[:31]
            # buf[:16] = it.IV[:]
            # buf[16:] = it.C[:]
            # ret.append(buf)
            # grp[_l] = buf
        n_grp = json.dumps(_grp)
        sql = f"UPDATE grp SET Cw='{n_grp}' WHERE Iw='{grp_name}'"
        self.cursor.execute(sql)
        self.conn.commit()

        for it in T:
            del it

        return 1

    # 计算512-bit哈希，计算L||D'
    @staticmethod
    def _hash_H(K: bytes, c: int, out: bytearray) -> int:
        buf1 = bytearray(32)

        buf1[:16] = K[:16]
        buf1[16:] = bytes("::" + str(c), 'utf-8')

        sm3_in1 = bytes_to_list(b'0#'+ buf1)
        sm3_in2 = bytes_to_list(b'1#'+ buf1)

        sm3_out1 = sm3_hash(sm3_in1)
        sm3_out2 = sm3_hash(sm3_in2)

        out[:32] = bytes.fromhex(sm3_out1)
        out[32:64] = bytes.fromhex(sm3_out2)

        return 1

    # 存储添加/删除的SSE密文
    def save(self, L: bytes, D: bytes, IV: bytes, C: bytes) -> int:
        # _l = bytes(L)
        # _c = SECipher()
        #
        # _c.D = D[:]
        # _c.IV = IV[:]
        # _c.C = C[:]

        if self.if_cleaning:
            self.p_clean_thread.join()
        self.if_cleaning = False

        # if _l in self.cipher_db:
        #     del self.cipher_db[_l]
        # self.cipher_db[_l] = _c
        _L = L.hex()
        # 判断是否存在
        sql = f"SELECT * FROM cipher WHERE L = '{_L}'"
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        # 如果存在，先删除该条目
        if row is not None:
            sql = f"DELETE FROM cipher WHERE L = '{_L}'"
            self.cursor.execute(sql)
            self.conn.commit()

        _D = D.hex()
        _C = (IV+C).hex()

        sql = f"INSERT INTO cipher (L,D,C) VALUES ('{_L}','{_D}','{_C}')"
        self.cursor.execute(sql)
        self.conn.commit()

        return 1

rotl = lambda x, n:((x << n) & 0xffffffff) | ((x >> (32 - n)) & 0xffffffff)

bytes_to_list = lambda data: [i for i in data]

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

# 调试样例
# 正确输出为：Search result: [b'n\x88\xa9!.\x8co\xd8\x19\x0b\x02\x12\x041\x8f\x9bj\x0b\x901\x9b\xe22%w`\xb1\x84D\xec\x18^\xf9\x127\xb8\xcc\x9f\x16\x97E\x10\xca\nU\xd4\nBz~\xe5\x92\x81@\x961\xcdfi>\xb0\x9b\xf51']
if __name__ == "__main__":
    server = SEServer()
    # server.setup()

    L = b'x\xfa\x86\xb1L\xd7\xdf\x89/\xdf\xa7\xd6\xf5\x8e\x82\x03N|o\xac\xe2\xb6r\xdb]\xc2\xb8^\x8b\x1a-.'
    D = b'c\x0c*R\xae4?\xaa\xceF\x9aA\xe8\x92~\xe3E\x8ew\x80\x08h8\xe5(\\\x7f\x86\x11K\xf0m'
    _IV = b'n\x88\xa9!.\x8co\xd8\x19\x0b\x02\x12\x041\x8f\x9b'
    C = b'j\x0b\x901\x9b\xe22%w`\xb1\x84D\xec\x18^\xf9\x127\xb8\xcc\x9f\x16\x97E\x10\xca\nU\xd4\nBz~\xe5\x92\x81@\x961\xcdfi>\xb0\x9b\xf51'

    server.save(L, D, _IV, C)

    K = b'q\xc9\x17qN\x9a\xce\xc1\xf7t\xe8\x82\x95v#\xa0\t%qTY\xb8\xf8\xaa\xdc\xfa\x0c\x95#\xcf\xd4\xeb'
    loc_grp = b'?z@>M<\xc3\xbeS\xfb\x13\x1a\x9e\x8a\n\xe0l\xe2\x1c\xe4\xdf>]\x01\xbf\xe9a\xe7<\xe1g\x10'
    result = []
    server.search(1, K, loc_grp, result)
    print("Search result:", result)