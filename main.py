#  coding:utf-8

import asyncio
import zlib
import json

import serial

from aiowebsocket.converses import AioWebSocket

remote = 'ws://broadcastlv.chat.bilibili.com:2244/sub'
heart_beat_msg = '00 00 00 10 00 10 00 01  00 00 00 02 00 00 00 01'
heart_beat_interval = 30

g_wooden_fish_num = 0

ser = serial.Serial(port='',
                    baudrate=115200,
                    timeout=0.5)
key = '积功德'

key_kun = '只因功德'

key_list = ['0001','0010','0011','0100',
            '0101','0110','0111','1000',
            '1001','1010','1011','1100',
            '1101','1110','1111']

fans_dict = {}

file = open('data/dict.txt', 'r')
for line in file.readlines():
    line = line.strip()
    k = line.split(' ')[0]
    v = int(line.split(' ')[1])
    fans_dict[k] = v

file.close()
print(fans_dict)


def writeSer(_w_data = '', _single=True):
    if _single:
        global g_wooden_fish_num
        print(g_wooden_fish_num)
        ser.write(str(g_wooden_fish_num).encode('utf-8'))
        g_wooden_fish_num = (g_wooden_fish_num+1)%4
    else:
        print(_w_data)
        ser.write(str(_w_data).encode('utf-8'))

async def startUp(_room_id):
    data_raw = '000000{Header}0010000100000007000000017b22726f6f6d6964223a{ID}7d'
    data_raw = data_raw.format(Header=hex(27 + len(_room_id))[2:],
                                         ID=''.join(map(lambda x: hex(ord(x))[2:], list(_room_id))))

    async with AioWebSocket(remote) as aws:
        converse = aws.manipulator
        await converse.send(bytes.fromhex(data_raw))
        tasks = [receivePackage(converse), sendHearBeat(converse)]
        await asyncio.wait(tasks)

async def sendHearBeat(_webscoket):
    while True:
        await asyncio.sleep(heart_beat_interval)
        await _webscoket.send(bytes.fromhex(heart_beat_msg))
        # print('[Notice] Sent HeartBeat.')

async def receivePackage(_webscoket):
    while True:
        recv_text = await _webscoket.receive()

        if recv_text == None:
            recv_text = b'\x00\x00\x00\x1a\x00\x10\x00\x01\x00\x00\x00\x08\x00\x00\x00\x01{"code":0}'

        parseData(recv_text)

def parseData(_data):
    # 获取数据包的长度，版本和操作类型
    packet_len = int(_data[:4].hex(), 16)
    ver = int(_data[6:8].hex(), 16)
    op = int(_data[8:12].hex(), 16)

    if (len(_data) > packet_len):
        parseData(_data[packet_len:])
        _data = _data[:packet_len]
    if (ver == 2):
        _data = zlib.decompress(_data[16:])
        parseData(_data)
        return
    if (ver == 1):
        return

    if (op == 5):
        try:
            jd = json.loads(_data[16:].decode('utf-8', errors='ignore'))
            if (jd['cmd'] == 'DANMU_MSG'):
                # print('[DANMU] ', jd['info'][2][1], ': ', jd['info'][1])
                add_user = False
                msg = jd['info'][1]
                user = jd['info'][2][1]
                if jd['info'][1] == '功德+1':
                    add_user = True
                    print(user, ': 功德+1')
                    writeSer()
                elif key in msg:
                    state = str(msg).replace(key, '')
                    if state in key_list:
                        print(user, ': 功德+n')
                        add_user = True
                        writeSer(_w_data=str(state), _single=False)
                elif key_kun in msg:
                    state = str(msg).replace(key_kun, '')
                    if state in key_list:
                        print('小只因子 —— ', user, ': 功德+n')
                        add_user = True
                        writeSer(_w_data=str(state), _single=False)

                if add_user:
                    global fans_dict
                    if user in fans_dict.keys():
                        fans_dict[user] = fans_dict[user] + 1
                    else:
                        fans_dict[user] = 1

                    file_w = open('data/dict.txt', 'w+')
                    for k, v in fans_dict.items():
                        file_w.write(str(k) + ' ' + str(v) + '\n')
                    file_w.close()



        except Exception as e:
            pass

if __name__ == '__main__':

    try:
        room_id = ''
        loop = asyncio.get_event_loop()
        loop.run_until_complete(startUp(room_id))

    except KeyboardInterrupt as exc:
        print('Quit.')
