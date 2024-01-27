import threshold_enc_file
from threshold_enc_file import SecretShare
from se_client import SEClient
from se_server import SEServer
from flask import Flask, request, jsonify
from random import choice
import random
import os
import shutil
import sys
from math import ceil
import binascii

random_hex = lambda x: ''.join([choice('0123456789abcdef') for _ in range(x)])

class CipherCTR:
    # 初始化
    # SE实例
    # SE相关中间变量
    def __init__(self, key_paths = ['./c', './d', './e', './f'], isLoad = False, isLazyDel=False):
        self.client = SEClient(isLoad)
        self.server = SEServer(isLoad)
        self.key_paths = key_paths
        self.L = bytearray(32)
        self.D = bytearray(32)
        self.IV = bytearray(16)
        self.C = bytearray(64)
        self.Kw = bytearray(32)
        self.Iw = bytearray(32)
        self.isLazyDel = isLazyDel
        self.lazy_cnt = 0
        self.lazy_ids = {}

        # 判断可选密钥分片存储集合是否存在
        # 不存在，则创建
        #        创建失败则删除
        for kp in self.key_paths:
            if os.path.isdir(kp) is False:
                try:
                    isTF = os.makedirs(kp)
                    if isTF is False:
                        print(kp+"目录不存在，且创建失败!")
                        if kp in self.key_paths:
                            self.key_paths.remove(kp)
                    else:
                        print(kp+"目录不存在，但创建成功!")
                except Exception as e:
                    print(kp+"目录不存在，且创建失败：", str(e))
                    if kp in self.key_paths:
                        self.key_paths.remove(kp)

    # 添加文件，数据存储系统 加密后存储
    # keywords 用户可指定，支持用户搜索
    # path 明文文件
    # path_set 副本位置
    # info_id 文件唯一标识
    def add_file(self, keywords, path, info_id, path_set, threshold = 1, num_participants=1):
        fkey = bytearray(16)
        # 读取明文的文件名
        f_name = os.path.basename(path)

        # info_id与对应密钥分片位置添加到SE
        # 同时在对应位置存储
        if num_participants > len(self.key_paths):
            print("分片量过大！请小于", num_participants)
            return
        if threshold == 1 and num_participants > 1:
            print("t = 1 and n = 1或者 t >=2, n >= 2 !")
            return

        # 保存t:n:fname到SE
        tnf = str(threshold) + ":" + str(num_participants) + ":" + f_name
        # print(tnf)
        self.client.update(info_id+"#n", tnf, "Add", self.L, self.D, self.IV, self.C)
        self.server.save(self.L, self.D, self.IV, self.C)
        # print("t,n,fname 存入SE")

        kpath_set = []
        # 生成一个密钥并存储
        if threshold == 1 and num_participants == 1:
            # 生成随机密钥
            rkey = threshold_enc_file.rng(16)
            # print("生成随机密钥成功")

            # 随机选择存储位置
            rnd = random.randint(0, len(self.key_paths)-1)
            # 随机设定文件名
            flag = True
            while flag:
                key_name = random_hex(16)
                if os.path.exists(self.key_paths[rnd]+"/"+key_name+".1.pem"):
                    flag = True
                else:
                    flag = False
            key_path = self.key_paths[rnd]+"/"+key_name+".1.pem"
            # 密钥存入文件
            threshold_enc_file.save_K(rkey, key_path)
            kpath_set.append(key_path)
            # 密钥文件地址存入SE
            self.client.update(info_id+"#k", key_path, "Add", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)

            fkey[:] = rkey
        else:
            # 生成随机密钥
            secret_share = SecretShare()
            rkey = threshold_enc_file.rng(16)
            # print("生成随机密钥成功")
            shares = secret_share.generate_shares(rkey, threshold, num_participants)
            # print("生成密钥分片成功")

            # 随机选择存储位置
            rnd_paths = random.sample(self.key_paths, num_participants)
            for i,key in shares:
                # 随机设定文件名
                flag = True
                while flag:
                    key_name = random_hex(16)
                    if os.path.exists(rnd_paths[i-1]+"/"+key_name+"."+str(i)+".pem"):
                        flag = True
                    else:
                        flag = False
                key_path = rnd_paths[i-1]+"/"+key_name+"."+str(i)+".pem"
                # 密钥存入文件
                threshold_enc_file.save_K(key, key_path)
                kpath_set.append(key_path)
                # 密钥文件地址存入SE
                self.client.update(info_id+"#k", key_path, "Add", self.L, self.D, self.IV, self.C)
                self.server.save(self.L, self.D, self.IV, self.C)
            fkey[:] = rkey
        # print("fkey生成成功")

        # keywords中每个(keyword, info_id)添加到SE
        # 记录每个文件已有keywords到SE
        for keyword in keywords:
            self.client.update(keyword, info_id, "Add", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)

            self.client.update(info_id+"#w", keyword, "Add", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
        # print("keyword记录成功")

        # 加密文件
        epath_set = threshold_enc_file.file_enc(fkey, path, path_set)
        # print("加密文件成功")
        # print(epath_set)

        # info_id与对应副本位置添加到SE
        for ef_path in epath_set:
            self.client.update(info_id+"#p", ef_path, "Add", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
        # print("副本位置添加成功")

        # 将加密后副本位置与文件位置返回
        ret = {}
        ret['InfoID'] = info_id
        ret['Paths'] = epath_set
        ret['Keys'] = kpath_set
        return ret

    # 获取密钥分片的所有位置
    def search_by_infoid(self, infoID):
        cnt_upd = [0]
        ebuf = []
        kpaths = []

        # 获取文件密钥分片位置
        self.client.trapdoor(infoID+"#k", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(infoID+"#n", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print(infoID, "keys 无匹配文件！")
            return
        self.client.decrypt(ebuf, kpaths)
        ebuf.clear()

        return kpaths

    # 获取密文文件的所有副本位置
    def search_duplocation(self, infoID):
        cnt_upd = [0]
        ebuf = []
        fpath = []
        # 获取文件密文副本位置
        self.client.trapdoor(infoID+"#p", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(infoID+"#p", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print(infoID, "paths 无匹配文件！")
            return
        self.client.decrypt(ebuf,fpath)
        ebuf.clear()

        return fpath

    # 用户根据关键字查找对应文件
    # 输入一个关键字
    # 返回对应文件，解密为明文，存放在dpath
    def keyword_search(self, keyword, dpath="."):
        key = bytearray(16)
        cnt_upd = [0]
        ebuf = []
        tnf = []
        ids = []
        fpath = []
        fps = []
        kpaths = []
        fks = []

        # 查找对应文件info_id
        self.client.trapdoor(keyword, cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(keyword, "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)

        if ebuf == []:
            print(keyword, "无匹配文件！")
            return
        self.client.decrypt(ebuf, ids)
        ebuf.clear()

        # 查找文件存储位置
        for id in ids:
            # 解析t，n，fname
            self.client.trapdoor(id+"#n", cnt_upd, self.Kw, self.Iw)
            if cnt_upd[0] == -1:
                print(info_id+"#n", "SE中无记录")
                return
            self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
            if ebuf == []:
                print(id, "(t,n),fname 无匹配文件！")
                return
            self.client.decrypt(ebuf, tnf)
            ebuf.clear()
            # 解析出 (t,n)门限值 和 原文件名
            tnfs = tnf[0].split(":")
            t = int(tnfs[0])
            n = int(tnfs[1])

            # 获取文件密文副本位置
            self.client.trapdoor(id+"#p", cnt_upd, self.Kw, self.Iw)
            if cnt_upd[0] == -1:
                print(info_id+"#p", "SE中无记录")
                return
            self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
            if ebuf == []:
                print(id, "paths 无匹配文件！")
                return
            self.client.decrypt([ebuf[0]],fpath)
            ebuf.clear()
            fps.append((fpath[0],tnfs[2]))
            tnf.clear()
            fpath.clear()

            # 获取文件密钥分片位置
            self.client.trapdoor(id+"#k", cnt_upd, self.Kw, self.Iw)
            if cnt_upd[0] == -1:
                print(info_id+"#k", "SE中无记录")
                return
            self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
            if ebuf == []:
                print("keys 无匹配文件！")
                return
            self.client.decrypt(ebuf, kpaths)
            ebuf.clear()

            # 取t片密钥分片，恢复出密钥
            shares = []
            for i in range(t):
                threshold_enc_file.read_K(kpaths[i], key)
                s_num = kpaths[i].split(".")[-2]
                shares.append((int(s_num), bytes(key)))
            fkey = SecretShare.reconstruct_key(shares, t, n)
            fks.append(fkey)
            kpaths.clear()

        # 解密所有满足文件到指定路径
        for j in range(len(fps)):
            threshold_enc_file.file_dec(fks[j], fps[j][0], fps[j][1], dpath)

    # 删除文件
    def del_file(self, info_id, del_method, vrf, level):
        ebuf = []
        tnf = []
        kpaths = []
        fpaths = []
        ws = []
        cnt_upd = [0]

        # 解析t，n，fname
        self.client.trapdoor(info_id+"#n", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(info_id+"#n", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print(info_id, "(t,n),fname 无匹配文件！")
            return
        self.client.decrypt(ebuf, tnf)
        ebuf.clear()
        # 解析出 (t,n)门限值 和 原文件名
        tnfs = tnf[0].split(":")
        t = int(tnfs[0])
        n = int(tnfs[1])

        # 删除SE中(t,n),fname对应记录
        self.client.update(info_id+"#n", tnf[0], "Del", self.L, self.D, self.IV, self.C)
        self.server.save(self.L, self.D, self.IV, self.C)
        # 搜一次确保SE中物理删除
        self.client.trapdoor(info_id+"#n", cnt_upd, self.Kw, self.Iw)
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        ebuf.clear()

        # 获取密钥分片位置
        self.client.trapdoor(info_id+"#k", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(info_id+"#k", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print(info_id, "keys 无匹配文件！")
            return
        self.client.decrypt(ebuf, kpaths)
        ebuf.clear()
        # print("Keys:", kpaths)

        # # 删除最小密钥分量
        # self.del_min_keys(info_id, t, n, kpaths, del_method, vrf, level)

        # # 删除剩余密钥分量
        # self.del_rest_keys(info_id, kpaths, del_method, vrf, level)
        # # 搜一次确保SE中物理删除
        # self.client.trapdoor(info_id+"#k", cnt_upd, self.Kw, self.Iw)
        # self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        # ebuf.clear()

        # # 删除密文文件及所有副本
        # self.del_replica(info_id, del_method, vrf, level)

        # # 闲时删除设置
        # if self.isLazyDel is True:
        #     self.lazy_ids[self.lazy_cnt] = [info_id, del_method, vrf, level]
        #     self.lazy_cnt += 1
        #     if self.lazy_cnt == 10:
        #         self.del_lazy()
        #         self.lazy_cnt = 0
        #         self.lazy_ids.clear()
         # 删除最小密钥分量
        self.del_min_keys(info_id, t, n, kpaths, del_method, vrf, level)

        # 如果启用闲时删除功能，则之后再删剩余密钥分量与密文文件
        if self.isLazyDel is False:
            # 删除剩余密钥分量
            self.del_rest_keys(info_id, kpaths, del_method, vrf, level)
            # 搜一次确保SE中物理删除
            self.client.trapdoor(info_id+"#k", cnt_upd, self.Kw, self.Iw)
            self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
            ebuf.clear()

            # 删除密文文件及所有副本
            self.del_replica(info_id, del_method, vrf, level)

        # 闲时删除设置
        if self.isLazyDel is True:
            print(len(kpaths),"个密钥分片延迟删除",kpaths)
            # 获取文件密文副本位置
            self.client.trapdoor(info_id+"#p", cnt_upd, self.Kw, self.Iw)
            if cnt_upd[0] == -1:
                print(info_id+"#p", "SE中无记录")
                return
            self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
            if ebuf == []:
                print(info_id, "paths 无匹配文件！")
                return
            self.client.decrypt(ebuf,fpaths)
            print("文件副本延迟删除", fpaths)

            self.lazy_ids[self.lazy_cnt] = [info_id, del_method, vrf, level]
            self.lazy_cnt += 1
            if self.lazy_cnt == 3:
                print("--开始延迟删除--")
                self.del_lazy()
                print("--结束延迟删除--")
                self.lazy_cnt = 0
                self.lazy_ids.clear()

        # 删除SE中 keyword 与 info_id 记录
        self.client.trapdoor(info_id+"#w", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(info_id+"#w", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print(info_id, "无关键字记录！")
            return
        self.client.decrypt(ebuf, ws)
        ebuf.clear()
        for w in ws:
            # 删除 (info_id, w)
            self.client.update(info_id+"#w", w, "Del", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)

            # 删除 (w, info_id)
            self.client.update(w, info_id, "Del", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
            # 搜一次确保物理删除SE中w-id对应记录
            self.client.trapdoor(w, cnt_upd, self.Kw, self.Iw)
            self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
            ebuf.clear()
        # 搜一次确保SE中物理删除id-{w}对应记录
        self.client.trapdoor(info_id+"#w", cnt_upd, self.Kw, self.Iw)
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        ebuf.clear()

    # 根据(t,n)门限值，删除最少的分片数量
    def del_min_keys(self, info_id, t, n, kpaths, del_method, vrf, level):
        # 如果 t = n, 随机删除 1 个密钥分片
        if t == n:
            rnd = random.randint(0, len(kpaths)-1)
            delpath = kpaths[rnd]
            threshold_enc_file.del_file(delpath, del_method, vrf, level)
            kpaths.remove(delpath)

            # 删SE中密钥分片路径记录
            self.client.update(info_id+"#k", delpath, "Del", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
        else:
            # 如果 t < n, 随机删除 n - t + 1 个密钥分片
            for i in range(n-t+1):
                rnd = random.randint(0, len(kpaths)-1)
                delpath = kpaths[rnd]
                threshold_enc_file.del_file(delpath, del_method, vrf, level)
                kpaths.remove(delpath)

                # 删SE中密钥分片路径记录
                self.client.update(info_id+"#k", delpath, "Del", self.L, self.D, self.IV, self.C)
                self.server.save(self.L, self.D, self.IV, self.C)

    # 删除余下的密钥分量
    def del_rest_keys(self, info_id, kpaths, del_method, vrf, level):
        # 删除剩余密钥分量
        for delpath in kpaths:
            threshold_enc_file.del_file(delpath, del_method, vrf, level)

            # 删SE中密钥分片路径记录
            self.client.update(info_id+"#k", delpath, "Del", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)

    # 删除密文文件及所有副本
    def del_replica(self, info_id, del_method, vrf, level):
        ebuf =[]
        cnt_upd = [0]
        fpaths = []

        # 获取文件密文副本位置
        self.client.trapdoor(info_id+"#p", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(info_id+"#p", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print(info_id, "paths 无匹配文件！")
            return
        self.client.decrypt(ebuf,fpaths)
        ebuf.clear()

        # 删除密文文件副本
        for fp in fpaths:
            threshold_enc_file.del_file(fp, del_method, vrf, level)
            # 删除SE中密文文件路径记录
            self.client.update(info_id+"#p", fp, "Del", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)

        # 搜一次确保SE中物理删除
        self.client.trapdoor(info_id+"#p", cnt_upd, self.Kw, self.Iw)
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        ebuf.clear()

    # 闲时删除设置，每删lazy_cnt执行一次
    def del_lazy(self):
        for info_in in self.lazy_ids.values():
            # 删除密文文件
            self.del_replica(info_in[0], info_in[1], info_in[2], info_in[3])
            # 查询并删除剩余密钥分量
            cnt_upd = [0]
            self.client.trapdoor(info_in[0]+"#k", cnt_upd, self.Kw, self.Iw)
            if cnt_upd[0] == -1:
                print(info_in[0]+"#k", "SE中无记录")
                return
            ebuf = []
            self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
            # 应该是t=1
            if ebuf == []:
                continue
            kpaths = []
            self.client.decrypt(ebuf, kpaths)
            ebuf.clear()
            self.del_rest_keys(info_in[0], kpaths, info_in[1], info_in[2], info_in[3])
            # 搜一次确保SE中物理删除
            self.client.trapdoor(info_in[0]+"#k", cnt_upd, self.Kw, self.Iw)
            self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
            ebuf.clear()

    # 删除文件中一个字段
    def del_field(self, info_id, field, del_method, vrf, level):
        fkey = bytearray(16)
        ekey = bytearray(16)
        ebuf = []
        tnf = []
        fpaths = []
        kpaths = []
        path_set = []
        cnt_upd = [0]

        # 解析t，n，fname
        self.client.trapdoor(info_id+"#n", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(info_id+"#n", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print("tnf 无匹配文件！")
            return
        self.client.decrypt(ebuf, tnf)
        ebuf.clear()
        # 解析出 (t,n)门限值 和 原文件名
        tnfs = tnf[0].split(":")
        t = int(tnfs[0])
        n = int(tnfs[1])
        fname = tnfs[2]

        if fname[-5:] != ".json":
            print(fname, "文件类型不是json！")
            return

        # 获取文件密文副本位置
        self.client.trapdoor(info_id+"#p", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(info_id+"#p", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print(info_id, "paths 无匹配文件！")
            return
        self.client.decrypt(ebuf,fpaths)
        ebuf.clear()

        # 更新文件名
        for _fn in fpaths:
            # 随机设定文件名
            flag = True
            while flag:
                rnd_name = random_hex(16)
                if os.path.exists(_fn[:-20] + rnd_name + ".dat"):
                    flag = True
                else:
                    flag = False
            epath = _fn[:-20] + rnd_name + ".dat"
            self.client.update(info_id+"#p", _fn, "Del", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
            self.client.update(info_id+"#p", epath, "Add", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
            path_set.append(epath)
        # 搜一次确保SE中旧地址物理删除
        self.client.trapdoor(info_id+"#p", cnt_upd, self.Kw, self.Iw)
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        ebuf.clear()

        # 获取文件密钥分片位置
        self.client.trapdoor(info_id+"#k", cnt_upd, self.Kw, self.Iw)
        if cnt_upd[0] == -1:
            print(info_id+"#k", "SE中无记录")
            return
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        if ebuf == []:
            print(info_id, "keys 无匹配文件！")
            return
        self.client.decrypt(ebuf, kpaths)
        ebuf.clear()
        # print("Old Keys:", kpaths)

        shares = []
        # 恢复出旧密钥
        for i in range(t):
            threshold_enc_file.read_K(kpaths[i], ekey)
            s_num = kpaths[i].split(".")[-2]
            shares.append((int(s_num), bytes(ekey)))
        seccret_share = SecretShare()
        old_fkey = seccret_share.reconstruct_key(shares, t, n)

        # 删除旧密钥分片
        # 1）删除最小密钥分量
        # 如果 t = n, 随机删除 1 个密钥分片
        if t == n:
            rnd = random.randint(0, len(kpaths)-1)
            delpath = kpaths[rnd]
            threshold_enc_file.del_file(delpath, del_method, vrf, level)
            kpaths.remove(delpath)
            # 删SE中密钥分片路径记录
            self.client.update(info_id+"#k", delpath, "Del", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
        else:
            # 如果 t < n, 随机删除 n - t + 1 个密钥分片
            for i in range(n-t+1):
                rnd = random.randint(0, len(kpaths)-1)
                delpath = kpaths[rnd]
                threshold_enc_file.del_file(delpath, del_method, vrf, level)
                kpaths.remove(delpath)
                # 删SE中密钥分片路径记录
                self.client.update(info_id+"#k", delpath, "Del", self.L, self.D, self.IV, self.C)
                self.server.save(self.L, self.D, self.IV, self.C)

        # 2）删除剩余密钥分量
        for delpath in kpaths:
            threshold_enc_file.del_file(delpath, del_method, vrf, level)
            # 删SE中密钥分片路径记录
            self.client.update(info_id+"#k", delpath, "Del", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
        # 搜一次确保SE中物理删除
        self.client.trapdoor(info_id+"#k", cnt_upd, self.Kw, self.Iw)
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        ebuf.clear()

        nkpaths = []
        # 生成新密密钥
        # 生成一个密钥并存储
        if t == 1 and n == 1:
            # 生成随机密钥
            rkey = threshold_enc_file.rng(16)

            # 随机选择存储位置
            rnd = random.randint(0, len(self.key_paths)-1)
            # 随机设定文件名
            flag = True
            while flag:
                key_name = random_hex(16)
                if os.path.exists(self.key_paths[rnd]+"/"+key_name+".1.pem"):
                    flag = True
                else:
                    flag = False
            key_path = self.key_paths[rnd]+"/"+key_name+".1.pem"
            # 密钥存入文件
            threshold_enc_file.save_K(rkey, key_path)
            # 密钥文件地址存入SE
            self.client.update(info_id+"#k", key_path, "Add", self.L, self.D, self.IV, self.C)
            self.server.save(self.L, self.D, self.IV, self.C)
            nkpaths.append(key_path)

            fkey[:] = rkey
        else:
            # 生成随机密钥
            secret_share = SecretShare()
            rkey = threshold_enc_file.rng(16)

            shares = secret_share.generate_shares(rkey, t, n)

            # 随机选择存储位置
            rnd_paths = random.sample(self.key_paths, n)
            for i,tkey in shares:
                # 随机设定文件名
                flag = True
                while flag:
                    key_name = random_hex(16)
                    if os.path.exists(rnd_paths[i-1]+"/"+key_name+"."+str(i)+".pem"):
                        flag = True
                    else:
                        flag = False
                key_path = rnd_paths[i-1]+"/"+key_name+"."+str(i)+".pem"
                # 密钥存入文件
                threshold_enc_file.save_K(tkey, key_path)
                # 密钥文件地址存入SE
                self.client.update(info_id+"#k", key_path, "Add", self.L, self.D, self.IV, self.C)
                self.server.save(self.L, self.D, self.IV, self.C)
                nkpaths.append(key_path)

            fkey[:] = rkey

        self.client.trapdoor(info_id+"#k", cnt_upd, self.Kw, self.Iw)
        self.server.search(cnt_upd[0], self.Kw, self.Iw, ebuf)
        ebuf.clear()
        # print("New Keys:", nkpaths)

        # 更新密文文件字段，解密删除字段后再加密，然后拷贝副本
        threshold_enc_file.update_field(old_fkey, fkey, field, fpaths, path_set, del_method, vrf, level)

        # 将新生成的加密后副本位置与文件位置返回
        ret = {}
        ret['InfoID'] = info_id
        ret['Paths'] = path_set
        ret['Keys'] = nkpaths
        return ret

    # 更新（添加）密钥可选密钥分片存储集合
    def add_key_paths(self, path):
        if type(path) == type("1"):
            if os.path.isdir(path) is False:
                try:
                    isTF = os.makedirs(path)
                    if isTF is False:
                        print(kp+"目录不存在，且创建失败!")
                    else:
                        print(kp+"目录不存在，但创建成功!")
                except Exception as e:
                    print(kp+"目录不存在，且创建失败：", str(e))
            else:
                if path in self.key_paths:
                    print(path+"已存在可选集合！")
                else:
                    self.key_paths.append(path)
                    print(path+"目录添加成功！")
        else:
            print("目录不是字符串")

    # 更新（删除）密钥可选密钥分片存储集合
    # 删除目录及下面密钥文件
    def del_key_paths(self, path):
        if path in self.key_paths:
            try:
                # 遍历文件夹内容并删除每个文件或子文件夹
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        os.remove(file_path)

                    for folder in dirs:
                        folder_path = os.path.join(root, folder)
                        os.rmdir(folder_path)

                # 最后删除空文件夹
                os.rmdir(path)

                print("成功删除文件夹"+path+"及其下的所有文件！")
            except Exception as e:
                print(path+"目录删除失败:", str(e))
        else:
            print(path+"不在可选集合！")

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
if __name__ == "__main__":
    # 初始化类
    cipher_CTR = CipherCTR()
    print("CipherCTR()初始化成功！")

    # 确保预置测试文件存在
    # 拷贝一份，作为本系统输入明文文件
    file_in = "./9w0x1y2z3a4b.json"

    if os.path.exists('./test_sample.json'):
        shutil.copy('./test_sample.json', file_in)
    else:
        print("请准备'./test_sample.json'文件！")
        sys.exit(1)
    print("输入文件./9w0x1y2z3a4b.json生成成功！")
    cmd_in = input("测试文件生成，输入任意字符继续")

    # 两处副本目录
    copy_paths = ["./c", "./e"]
    # 输入关键字集合
    keywords = ["Male"]


    # 添加文件，关键字Male，门限(2,3)
    kp_dict = cipher_CTR.add_file(keywords, file_in, "9w0x1y2z3a4b", copy_paths, 2, 3)
    print(kp_dict['Paths'])
    print(kp_dict['Keys'])
    cmd_in = input("文件添加成功，输入任意字符继续")

    file_in = "./4w0x1y2z3a4a.json"
    shutil.copy('./test_sample.json', file_in)

    # 添加文件，关键字Male，门限(2,3)
    kp_dict = cipher_CTR.add_file(keywords, file_in, "4w0x1y2z3a4a", copy_paths, 2, 3)
    print(kp_dict['Paths'])
    print(kp_dict['Keys'])
    cmd_in = input("文件添加成功，输入任意字符继续")

    # 搜索获取明文文件
    cipher_CTR.keyword_search("Male")
    cmd_in = input("搜索成功，输入任意字符继续")

    del_method = "overwrittenDelete", 
    vrf = "1111111111111"
    level = 1

    # 删除 Phone 字段
    kp_dict = cipher_CTR.del_field("9w0x1y2z3a4b", "Phone",  del_method, vrf, level)
    print(kp_dict['Paths'])
    print(kp_dict['Keys'])
    cmd_in = input("删除字段成功，输入任意字符继续")

    # 查看字段删除效果
    cipher_CTR.keyword_search("Male")
    cmd_in = input("再次搜索成功，输入任意字符继续")

    # 删除整个文件
    cipher_CTR.del_file("9w0x1y2z3a4b",del_method, vrf, level)
    cmd_in = input("删除文件成功，输入任意字符继续")
    cipher_CTR.del_file("4w0x1y2z3a4a",del_method, vrf, level)
    cmd_in = input("删除文件成功，输入任意字符继续")

    threshold_enc_file.del_file("./9w0x1y2z3a4b.json", del_method, vrf, level)
    threshold_enc_file.del_file("./4w0x1y2z3a4a.json", del_method, vrf, level)