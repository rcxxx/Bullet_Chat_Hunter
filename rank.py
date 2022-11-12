#  coding:utf-8

import os
import time

while True:
    fans_dict = {}
    file = open('data/dict.txt', 'r')
    for line in file.readlines():
        line = line.strip()
        k = line.split(' ')[0]
        v = int(line.split(' ')[1])
        fans_dict[k] = v

    file.close()

    f = sorted(fans_dict.items(), key=lambda d:d[1], reverse = True)
    rank = 0
    clear = os.system('clear')
    for user in f:
        if rank == 0:
            print('\033[45;41m' + '榜一大哥' + '\033[0m' + ' :', user[0], '\t-- 已积累功德: ', user[1])
            rank += 1
        elif rank == 1:
            print('\033[34;45m' + '榜二大哥' + '\033[0m' + ' :', user[0], '\t-- 已积累功德: ', user[1])
            rank += 1
        elif rank == 2:
            print('\033[32;46m' + '榜三大哥' + '\033[0m' + ' :', user[0], '\t-- 已积累功德: ', user[1])
            rank += 1
        elif rank < 10:
            print('继续努力: ', user[0], '\t-- 已积累功德: ', user[1])
            rank += 1
        else:
            continue

    time.sleep(1)
