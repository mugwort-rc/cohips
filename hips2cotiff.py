#!/usr/bin/env python3

"""
Copyright (c) 2022 AstroArts Inc.
Copyright (c) 2022 mugwort_rc.

Licensed under the MIT License.

-------------------------------------------------------------------------------

Generate Cloud Optimized HiPS-TIFF

z=0 (nside=1)
+----+----+----+----+
|  0 |  1 |  2 |  3 |
+----+----+----+----+
|  4 |  5 |  6 |  7 |
+----+----+----+----+
|  8 |  9 | 10 | 11 |
+----+----+----+----+

z=1 (nside=2)
+----+----+----+----+----+----+----+----+
|  0 |  2 |  4 |  6 |  8 | 10 | 12 | 14 |
+----+----+----+----+----+----+----+----+
|  1 |  3 |  5 |  7 |  9 | 11 | 13 | 15 |
+----+----+----+----+----+----+----+----+
| 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 |
+----+----+----+----+----+----+----+----+
| 17 | 19 | 21 | 23 | 25 | 27 | 29 | 31 |
+----+----+----+----+----+----+----+----+
| 32 | 34 | 36 | 38 | 40 | 42 | 44 | 46 |
+----+----+----+----+----+----+----+----+
| 33 | 35 | 37 | 39 | 41 | 43 | 45 | 47 |
+----+----+----+----+----+----+----+----+

z=2 (nside=4)
+----+----+----+----+----+----+----+----+
|  0 |  2 |  8 | 10 | 16 | 18 | 24 | 26 | ..
+----+----+----+----+----+----+----+----+
|  1 |  3 |  9 | 11 | 17 | 19 | 25 | 27 | ..
+----+----+----+----+----+----+----+----+
|  4 |  6 | 12 | 14 | 20 | 22 | 28 | 30 | ..
+----+----+----+----+----+----+----+----+
|  5 |  7 | 13 | 15 | 21 | 23 | 29 | 31 | ..
+----+----+----+----+----+----+----+----+
  :     :    :    :    :    :    :    :
"""

from __future__ import annotations

import argparse
import enum
import os
import shutil
import struct
import sys

from PIL import Image


class TiffType(enum.IntEnum):
    BYTE = 1
    ASCII = 2
    SHORT = 3
    LONG = 4
    RATIONAL = 5
    SBYTE = 6
    UNDEFINED = 7
    SSHORT = 8
    SLONG = 9
    SRATIONAL = 10
    FLOAT = 11
    DOUBLE = 12


TIFF_BYTES = {
    TiffType.BYTE: 1,
    TiffType.ASCII: 1,
    TiffType.SHORT: 2,
    TiffType.LONG: 4,
    TiffType.RATIONAL: 8,
    TiffType.SBYTE: 1,
    TiffType.UNDEFINED: 1,
    TiffType.SSHORT: 2,
    TiffType.SLONG: 4,
    TiffType.SRATIONAL: 8,
    TiffType.FLOAT: 4,
    TiffType.DOUBLE: 8,
}


class TiffEntry:
    def __init__(self, id: int, type: TiffType, count: int, value):
        self.id = id
        self.type = type
        self.count = count
        self.value = value

    def serialize(self, offset=-1, classical=True):
        if offset < 0:
            offset = 0
        bytes = TIFF_BYTES[self.type]
        size = self.count * bytes
        if classical:
            if self.type in [TiffType.BYTE, TiffType.SHORT, TiffType.LONG]:
                if size <= 4:
                    if self.type == TiffType.BYTE:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0, 0, 0, 0])[:4]
                        return struct.pack("<HHI4B", int(self.id), int(self.type), self.count, *value)
                    elif self.type == TiffType.SHORT:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0, 0])[:2]
                        return struct.pack("<HHI2H", int(self.id), int(self.type), self.count, *value)
                    elif self.type == TiffType.LONG:
                        return struct.pack("<HHII", int(self.id), int(self.type), self.count, self.value)
                else:
                    return struct.pack("<HHII", int(self.id), int(self.type), self.count, offset)
            elif self.type in [TiffType.SBYTE, TiffType.SSHORT, TiffType.SLONG]:
                if size <= 4:
                    if self.type == TiffType.BYTE:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0]*4)[:4]
                        return struct.pack("<HHI4b", int(self.id), int(self.type), self.count, *value)
                    elif self.type == TiffType.SHORT:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0]*2)[:2]
                        return struct.pack("<HHI2h", int(self.id), int(self.type), self.count, *value)
                    elif self.type == TiffType.LONG:
                        return struct.pack("<HHIi", int(self.id), int(self.type), self.count, self.value)
                else:
                    return struct.pack("<HHII", int(self.id), int(self.type), self.count, offset)
            else:
                assert False, f"ToDo: not implemented yet: {self.type}"
        else:
            # BigTIFF
            if self.type in [TiffType.BYTE, TiffType.SHORT, TiffType.LONG]:
                if size <= 8:
                    if self.type == TiffType.BYTE:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0]*8)[:8]
                        return struct.pack("<HHQ8B", int(self.id), int(self.type), self.count, *value)
                    elif self.type == TiffType.SHORT:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0]*4)[:4]
                        return struct.pack("<HHQ4H", int(self.id), int(self.type), self.count, *value)
                    elif self.type == TiffType.LONG:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0]*2)[:2]
                        return struct.pack("<HHQ2I", int(self.id), int(self.type), self.count, *value)
                else:
                    return struct.pack("<HHQQ", int(self.id), int(self.type), self.count, offset)
            elif self.type in [TiffType.SBYTE, TiffType.SSHORT, TiffType.SLONG]:
                if size <= 8:
                    if self.type == TiffType.BYTE:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0]*8)[:8]
                        return struct.pack("<HHQ8b", int(self.id), int(self.type), self.count, *value)
                    elif self.type == TiffType.SHORT:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0, 0])[:2]
                        return struct.pack("<HHQ4h", int(self.id), int(self.type), self.count, *value)
                    elif self.type == TiffType.LONG:
                        value = self.value
                        if not isinstance(value, list):
                            value = [value]
                        value = (value + [0]*2)[:2]
                        return struct.pack("<HHQ2i", int(self.id), int(self.type), self.count, *value)
                else:
                    return struct.pack("<HHQQ", int(self.id), int(self.type), self.count, offset)
            else:
                assert False, f"ToDo: not implemented yet: {self.type}"

    def has_tail(self):
        bytes = TIFF_BYTES[self.type]
        size = self.count * bytes
        return size > 4

    def tail(self):
        if not self.has_tail():
            return b""
        if self.count > 1:
            if self.type == TiffType.BYTE:
                return struct.pack(f"{self.count}B", *self.value)
            elif self.type == TiffType.ASCII:
                return struct.pack(f"{self.size-1}s", self.value) + b"\0"
            elif self.type == TiffType.SHORT:
                return struct.pack(f"{self.count}H", *self.value)
            elif self.type == TiffType.LONG:
                return struct.pack(f"{self.count}I", *self.value)
            else:
                assert False, f"ToDo: not implemented yet: {self.type}"
        else:
            assert self.count == 0
            if self.type == TiffType.RATIONAL:
                return struct.pack("<2I", *self.value)
            elif self.type == TiffType.SRATIONAL:
                return struct.pack("<2i", *self.value)
            elif self.type == TiffType.DOUBLE:
                return struct.pack("<d", self.value)
            else:
                assert False, f"Unknown data type: {self.type}"


class TiffBuilder:
    def __init__(self, classical=False):
        self.classical = classical
        self.entries = []

    def add_entry(self, id: int, type: TiffType, count: int, value):
        entry = TiffEntry(id, type, count, value)
        self.entries.append(entry)
        return entry

    def build_header(self, offset=-1):
        if self.classical:
            header = b"II*\x00\x08\x00\x00\x00"
            header += struct.pack("<H", len(self.entries))
        else:
            header = b"II+\x00\x08\x00\x00\x00"
            header += struct.pack("<Q", 0x10)
            header += struct.pack("<Q", len(self.entries))
        header_tail_bytes = 0
        for entry in self.entries:
            header += entry.serialize(offset + header_tail_bytes, classical=self.classical)
            header_tail_bytes += len(entry.tail())
        if self.classical:
            header += b"\x00" * 4  # Next IFD (none)
        else:
            # BigTIFF
            header += b"\x00" * 8  # Next IFD (none)
        header_pointer_offset = len(header)
        for entry in self.entries:
            header += entry.tail()
        if offset < 0:
            return self.build_header(header_pointer_offset)
        return header


class TiffTag:
    ImageWidth = 0x100
    ImageLength = 0x101
    BitsPerSample = 0x102
    Compression = 0x103
    PhotometricInterpretation = 0x106
    SamplesPerPixel = 0x115
    PlanarConfiguration = 0x11c
    TileWidth = 0x142
    TileLength = 0x143
    TileOffsets = 0x144
    TileByteCounts = 0x145
    SampleFormat = 0x153
    ModelTransformationTag = 0x85d8
    GeoKeyDirectoryTag = 0x87af
    GeoAsciiParamsTag = 0x87b1


# for index -> (x, y)
def compress_bits(v: int) -> int:
    res = v & 0x5555555555555555
    res = (res^(res>> 1)) & 0x3333333333333333
    res = (res^(res>> 2)) & 0x0f0f0f0f0f0f0f0f
    res = (res^(res>> 4)) & 0x00ff00ff00ff00ff
    res = (res^(res>> 8)) & 0x0000ffff0000ffff
    res = (res^(res>>16)) & 0x00000000ffffffff
    return res


# for (x, y) -> index
def spread_bits(v: int) -> int:
    res = v & 0xffffffff
    res = (res^(res<<16)) & 0x0000ffff0000ffff
    res = (res^(res<< 8)) & 0x00ff00ff00ff00ff
    res = (res^(res<< 4)) & 0x0f0f0f0f0f0f0f0f
    res = (res^(res<< 2)) & 0x3333333333333333
    res = (res^(res<< 1)) & 0x5555555555555555
    return res


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("zoom", type=int)
    parser.add_argument("--classical", action="store_true", default=False)

    args = parser.parse_args(argv[1:])

    nside = 1 << args.zoom

    # 0  1  2  3
    # 4  5  6  7
    # 8  9 10 11
    tile_count_x = nside * 4
    tile_count_y = nside * 3
    total_tile = tile_count_x * tile_count_y

    img = Image.open(os.path.join(args.root, f"Norder{args.zoom}", "Dir0", "Npix0.jpg"))
    tile_width, tile_height = img.size
    image_width = tile_width * tile_count_x
    image_height = tile_height * tile_count_y

    builder = TiffBuilder(classical=args.classical)
    if args.classical:
        builder.add_entry(TiffTag.ImageWidth, TiffType.SHORT, 1, image_width)
        builder.add_entry(TiffTag.ImageLength, TiffType.SHORT, 1, image_height)
    else:
        builder.add_entry(TiffTag.ImageWidth, TiffType.LONG, 1, image_width)
        builder.add_entry(TiffTag.ImageLength, TiffType.LONG, 1, image_height)
    builder.add_entry(TiffTag.BitsPerSample, TiffType.SHORT, 3, [8, 8, 8])
    builder.add_entry(TiffTag.Compression, TiffType.SHORT, 1, 0x07)
    builder.add_entry(TiffTag.PhotometricInterpretation, TiffType.SHORT, 1, 6)
    builder.add_entry(TiffTag.SamplesPerPixel, TiffType.SHORT, 1, 3)
    builder.add_entry(TiffTag.PlanarConfiguration, TiffType.SHORT, 1, 1)
    builder.add_entry(TiffTag.TileWidth, TiffType.SHORT, 1, tile_width)
    builder.add_entry(TiffTag.TileLength, TiffType.SHORT, 1, tile_height)
    offsets = builder.add_entry(TiffTag.TileOffsets, TiffType.LONG, total_tile, [0 for x in range(total_tile)])
    counts = builder.add_entry(TiffTag.TileByteCounts, TiffType.LONG, total_tile, [0 for x in range(total_tile)])
    builder.add_entry(TiffTag.SampleFormat, TiffType.SHORT, 1, 1)

    header = builder.build_header()
    data_head = len(header)

    # calculate offsets
    nside2 = nside * nside
    for i in range(total_tile):
        row = i // tile_count_x
        col = i % tile_count_x
        row0 = row // nside
        col0 = col // nside
        f = row0 * 4 + col0
        x = row % nside
        y = col % nside
        # NOTE: HiPS is transposed
        ti = f * nside2 + ((spread_bits(y) << 1) | spread_bits(x))
        s = os.stat(os.path.join(args.root, f"Norder{args.zoom}", f"Dir{ti // 10000 * 100000}", f"Npix{ti}.jpg"))
        size = s.st_size
        offsets.value[i] = data_head
        counts.value[i] = size
        data_head += size

    header = builder.build_header()

    with open(f"{args.zoom}.tif", "wb") as tiff:
        tiff.write(header)
        for i in range(total_tile):
            row = i // tile_count_x
            col = i % tile_count_x
            row0 = row // nside
            col0 = col // nside
            f = row0 * 4 + col0
            x = row % nside
            y = col % nside
            # NOTE: HiPS is transposed
            ti = f * nside2 + ((spread_bits(y) << 1) | spread_bits(x))
            src = open(os.path.join(args.root, f"Norder{args.zoom}", f"Dir{ti // 10000 * 10000}", f"Npix{ti}.jpg"), "rb")
            shutil.copyfileobj(src, tiff)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
