r'''
How to use:
Install python 3.8 or later, run python.exe -m pip install pywin32
put your text in input.txt, run this, then paste in LM layer 3 or credits editor



rd /s/q dist build
pyinstaller  lm_l3_clipboard.py

pip install pyinstaller

pyinstaller -F --exclude-module select --exclude-module _bz2 --exclude-module _decimal --exclude-module _lzma  --exclude-module _socket  lm_l3_clipboard.py


Lunar Magic OV Tiles v2 notes:
1: 80 00 00 00 80 d0 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 09 00 00 30 00 00 00 30 00 00 00 00 00 00 00
num sel tile sel width   sel height

5-8: 0
9: 19 38 1e 38 1b 38 19 38 15 38 0e 38 fc 38 0b 38
start of tile data
tile num, YXPCCCTT
(it can start 2*2 bytes earlier sometimes???)


end of visible tile data (layer 3 editor)
520: fc 38 1c 38 19 38 1b 38 12 38 1d 38 0e 38 1c 38


selection mask??
3337: 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10
3337: unselected 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

'''

import sys
import struct
import win32clipboard  # pip install pywin32
import gzip
import base64

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

if True:
    # print(repr(dir(win32clipboard)))
    win32clipboard.OpenClipboard(None)
    try:
        format = 0
        while True:
            format = win32clipboard.EnumClipboardFormats(format)
            if format == 0:
                break
            name = None
            try:
                if format >= 0xC000:
                    name = win32clipboard.GetClipboardFormatName(format)
            except:
                pass
            if name == 'Lunar Magic OV Tiles v2':
                data = win32clipboard.GetClipboardData(format)
                with open('empty', 'wb') as out_file:
                    for chunk in chunker(data, 16):
                        line = (' '.join((f'{v:02x}' for v in chunk))).encode('utf8')
                        # print(line, file=out_file)
                        out_file.write(line)
                        out_file.write(b'\n')
            # 'Lunar Magic Map8 Tiles'

    finally:
        # win32clipboard.CloseClipboard()
        pass




# print(repr(dir(win32clipboard)))
win32clipboard.OpenClipboard(None)
try:
    format = win32clipboard.RegisterClipboardFormat('Lunar Magic OV Tiles v2')
    # empty file is created from all tiles 0xFC pal 6 priority; select all, copy
    # with open('empty', 'rt') as example:
    #     data = b''.join((bytes(int(v, 16) for v in line.split()) for line in example.readlines()))
    # data = data[:-1]
    # print(len(gzip.compress(data)))
    # print(base64.b64encode(gzip.compress(data)))
    empty = b'H4sIANUzyGIC/+3DsREAEAAEwS9BOUKlKVFBAoEGBCRmb+d6kj5yXkla9jeaFQAAAAAAAAAAAAAAAA' + \
        b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN4rkiRJkiTp+yJJkiRJkiRJkiRJkiRJk' + \
        b'iRJkiRJkiRJkiRJkiRJkiRJkm63ANZgChR/OAEA'
    data = gzip.decompress(base64.b64decode(empty))
    data = list(data)

    char_map = {}
    for c in range(ord('a'), ord('z') + 1):
        char_map[chr(c).upper()] = char_map[chr(c)] = c - ord('a') + 10
    for c in '0123456789':
        char_map[c] = ord(c) - ord('0')
    char_map['.'] = 0x24
    char_map[','] = 0x25
    char_map['*'] = 0x26
    char_map['-'] = 0x27
    char_map['_'] = 0x27
    char_map['!'] = 0x28
    char_map['$'] = 0x2E
    char_map[' '] = 0xFC

    char_map2 = {}
    for c in range(ord('a'), ord('z') + 1):
        tile = 0xC0 + c - ord('a')
        if c >= ord('q'):
            tile += 0x10
        char_map2[chr(c).upper()] = char_map2[chr(c)] = (tile, tile + 0x10)
    char_map2[' '] = (0xFC, 0xFC)
    char_map2['-'] = (0xEA, 0xFA)
    char_map2['.'] = (0xEB, 0xFB)


    data[3336 * 0x10:] = b'\x00' * (len(data) - 3336 * 0x10)
    # data[3336 * 0x10 + tiles_length:] = b'\x00' * (len(data) - 3336 * 0x10 - tiles_length)

    # print(repr(char_map))
    def add_output(c):
        tile = char_map.get(c)
        if tile is None:
            print(f'Couldnt map {c}')
            return
        data[output_pos:output_pos+2] = bytes([tile, 0x38])

    def add_output2(c):
        tile = char_map2.get(c)
        if tile is None:
            print(f'Couldnt map {c}')
            return
        data[output_pos:output_pos+2] = bytes([tile[0], 0x38])
        data[output_pos+line_width:output_pos+line_width+2] = bytes([tile[1], 0x38])

    width = 1
    height = 0
    with open('input.txt', 'rt') as input:
        output_pos = 0x80
        for line_no, line in enumerate(input.readlines()):
            line = line.rstrip('\r\n')
            two_tall = line.startswith('2')
            if two_tall:
                line = line[1:]
            if len(line) >= 0x20:
                raise ValueError(f'Line too long  {line}')
            line_width = 0x40  # bytes, 2 bytes per tile

            if len(line) < line_width:
                line = ' ' * ((line_width // 2 - len(line)) // 2) + line
            width = max(len(line), width)
            height += 2 if two_tall else 1

            mask_addr = 3336*16
            mask_addr = mask_addr + (height - 1) * line_width // 2  # // 2: two bytes per tile
            data[mask_addr:mask_addr + line_width // 2] = [0x10] * (line_width // 2)
            if two_tall:
                mask_addr = 3336*16
                mask_addr = mask_addr + (height - 2) * line_width // 2
                data[mask_addr:mask_addr + line_width // 2] = [0x10] * (line_width // 2)

            for c in line:
                if two_tall:
                    add_output2(c)
                else:
                    add_output(c)
                output_pos += 2

            output_pos = (output_pos & ~(line_width - 1)) + line_width
            if two_tall:
                output_pos = (output_pos & ~(line_width - 1)) + line_width
            # print(hex(output_pos))

    # data[0x30:0x30+0x10] = struct.pack('iiii', width * height, width * 2, height * 2, 0)
    data[0x30:0x30+0x10] = struct.pack('iiii', line_width // 2 * height, line_width // 2, height, 0)
    if height >= 0x80:
        data[0x30:0x30+0x10] = struct.pack('iiii', line_width // 2 * 0x80, line_width, 0x80, 0)

    tiles_length = line_width * (output_pos + 0)
    # data[3336 * 0x10:3337 * 0x10 + tiles_length] = b'\x10' * tiles_length
    # data[3336 * 0x10 + tiles_length:] = b'\x00' * (len(data) - 3336 * 0x10 - tiles_length)

    data = bytes(data)
    win32clipboard.SetClipboardData(format, data)
finally:
    win32clipboard.CloseClipboard()
