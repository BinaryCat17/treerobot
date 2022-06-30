import struct
import libscrc
from collections import OrderedDict
from .tags import tags as TAGS

def make_packet(ltags, is_archive = True):
    packet = struct.pack('<B', 1)
    tags = b''
    for tag_id, data in ltags:
        if tag_id not in TAGS:
            return None
        tags += struct.pack('<B', tag_id) + TAGS[tag_id].pack(data)

    mask = 0b1000000000000000 if is_archive else 0b0000000000000000
    len_packet = len(tags) | mask
    packet += struct.pack('<H', len_packet)
    packet += tags
    crc16 = libscrc.modbus(packet)
    packet += struct.pack('<H', crc16)
    return packet, crc16
       

# Пакет всегда начинается с трёх байт, в которых кодируется
# заголовок, размер пакета до начала контрольной суммы и признак неотправленных данных в архиве
def packet_begin(data):
    h, len_pack = struct.unpack_from('<BH', data)
    length = len_pack & 0b0111111111111111
    is_archive = len_pack & 0b1000000000000000 == 0b1000000000000000
    return h, length, is_archive

def crc16(data):
    # переданная контрольная сумма занимает два последних байта
    data_crc16 = struct.unpack_from('<H', data, offset=len(data) - 2)[0]
    # вычисляем фактическую контрольную сумму
    calc_crc16 = libscrc.modbus(data[:-2])
    return data_crc16, calc_crc16


# составление пакета, отправляемого обратно для подтверждения
def confirm(data_crc16):
    return struct.pack('<B', 2) + struct.pack('<H', data_crc16)

# функция возвращает массив показаний
# каждое показание состоит из карты именнованных тегов
# теги определяются в файле tags.py
# скорее всего (но это не точно):
# если приходит одно показание, то возвращается массив из одного элемента
# если приходит архив показаний, они сохраняются в массив
def parse(data):
    body = data[3:-2]
    offset = 0
    packet = []
    record = {}
    last_tag_id = 0
    while offset < len(body):
        tag_id = body[offset]

        if last_tag_id >= tag_id:
            packet.append(record)
            record = OrderedDict()

        tag = TAGS[tag_id]
        value, size = tag.unpack(body, offset=offset + 1, record=record, header_packet=OrderedDict(), conf={})
        offset += size + 1
        record.update(value)
        last_tag_id = tag_id

    if record:
        packet.append(record)

    return packet