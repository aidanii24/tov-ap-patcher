import random
import struct
import shutil
import ctypes
import json
import mmap
import math
import time
import os

from vesperia_types import *

def test_structure(sample_struct):
    for attribute, ctype in sample_struct._fields_:
        value = getattr(sample_struct, attribute)

        if type(value) == int:
            as_hex = hex(value)
        elif type(value) == float:
            as_hex = hex(struct.unpack('<I', struct.pack('<f', value))[0])
        elif type(bytes):
            if "Array" in type(value).__name__:
                print(type(type(value)))
                print("Array Test:", issubclass(type(value), ctypes.Array))
                value = [*value]
                as_hex = [hex(arte_id) for arte_id in value]
            else:
                as_hex = value.hex()
        else:
            as_hex = "Unhandled"

        print(f"{attribute}: {value} | ({as_hex})")

    print(json.dumps(sample_struct, cls=VesperiaStructureEncoder, indent=4))
    as_bytes = bytearray(sample_struct)
    format_bytes(as_bytes)

    # copy_arte: ArtesEntry = ArtesEntry.from_buffer_copy(as_bytes)
    # copy_bytes = bytearray(copy_arte)
    # print(copy_bytes)

def format_bytes(as_bytes: bytes):
    print(as_bytes)
    print("\n 0 1 2 3  4 5 6 7  8 9 A B  C D E F")
    for _ in range(math.ceil(len(as_bytes) / 16)):
        chunk = as_bytes[_ * 16: _ * 16 + 16].hex()
        final = ""
        for _ in range(min(4, math.ceil(len(chunk) / 4))):
            final += chunk[_ * 8: _ * 8 + 8] + " "

        print(final)

def arte_to_json():
    test_file: str = "builds/BTL_PACK/0004.ext/ALL.0000"

    start: float = time.time()

    artes: list[ArtesEntry] = []
    strings: list[str] = []

    with open(test_file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        mm.seek(0)
        header_size: int = ctypes.sizeof(ArtesHeader)

        header : ArtesHeader = ArtesHeader.from_buffer_copy(mm.read(header_size))

        mm.seek(ctypes.sizeof(ArtesHeader))
        for count in range(header.entries):
            artes_size: int = int.from_bytes(mm.read(4), byteorder="little")
            mm.seek(-4, 1)
            artes.append(ArtesEntry.from_buffer_copy(mm.read(artes_size)))

        strings = (mm.read(-1).decode('utf-8').rstrip("\x00").split("\x00"))

        mm.close()

    with open("builds/0004R.json", "x+") as f:
        manifest: dict = {"artes": artes, "strings": strings}
        json.dump(manifest, f, cls=VesperiaStructureEncoder, indent=4)

        f.close()

    end: float = time.time()
    print(f"[Writing JSON] Time taken: {end - start} seconds")

    print(f"Artes: {len(artes)} | Strings: {len(strings)}")

def arte_from_json():
    start = time.time()

    artes: list[ArtesEntry] = []
    strings: list[str] = []

    with open("builds/0004R.json", "r") as f:
        data = json.load(f)

        artes = [ArtesEntry(*entry.values()) for entry in data["artes"]]
        strings = data["strings"]

        f.close()

    with open("builds/0004R.0000", "x+") as f:
        data_end: int = sum([ctypes.sizeof(arte) for arte in artes]) + ctypes.sizeof(ArtesHeader)
        string_list: str = "".join(string + "\x00" for string in strings)
        header: ArtesHeader = ArtesHeader(len(artes), data_end)

        f.truncate(ctypes.sizeof(ArtesHeader) + data_end + len(string_list))
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

        mm.write(bytearray(header))
        for arte in artes:
            mm.write(bytearray(arte))

        mm.write(string_list.encode())

        mm.flush()
        mm.close()

    end: float = time.time()
    print(f"[Rebuilding File] Time taken: {end - start} seconds")

def item_to_json():
    test_file: str = "builds/item/ITEM.DAT"

    start: float = time.time()

    items: list[ItemEntry] = []

    with open(test_file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        items_size: int = ctypes.sizeof(ItemEntry)

        mm.seek(0)
        while True:
            data = mm.read(items_size)

            if not data or len(data) < items_size or all(b == 0 for b in data): break

            items.append(ItemEntry.from_buffer_copy(data))

        mm.close()

    with open("builds/item.json", "x+") as f:
        manifest: dict = {"items": items}
        json.dump(manifest, f, cls=VesperiaStructureEncoder, indent=4)

        f.close()

    end: float = time.time()
    print(f"[Writing JSON] Time taken: {end - start} seconds")

    print(f"Items: {len(items)}")

def add_items(extra_items: int):
    start = time.time()

    items: list[ItemEntry] = []
    base_data: dict = {}

    with open("builds/item.json", "r") as f:
        data = json.load(f)
        base_data: dict = data["items"][1]

        items = [ItemEntry(**entry) for entry in data["items"]]

        f.close()

    base_data["picture"] = "ITEM_AP"
    for _ in range(extra_items):
        new_data: dict = base_data.copy()
        new_data["id"] = 2000 + _
        new_data["name_string_key"] += 1 + _
        new_data["buy_price"] = random.randint(1, 500) * 10
        new_data["entry"] += _ + 1

        new_entry: ItemEntry = ItemEntry(**new_data)
        items.append(new_entry)

    patch_item_sort(items[-extra_items:])

    with open(f"builds/item-r{extra_items}.dat", "x+") as f:
        f.truncate(ctypes.sizeof(ItemEntry) * len(items))
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

        for item in items:
            mm.write(bytearray(item))

        mm.flush()
        mm.close()

    end: float = time.time()
    print(f"[Rebuilding File and Added 100 new Items] Time taken: {end - start} seconds")


def item_from_json():
    start = time.time()

    items: list[ItemEntry] = []

    with open("builds/item.json", "r") as f:
        data = json.load(f)

        items = [ItemEntry(**entry) for entry in data["items"]]

        f.close()

    with open("builds/item-r.dat", "x+") as f:
        f.truncate(ctypes.sizeof(ItemEntry) * len(items))
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

        for item in items:
            mm.write(bytearray(item))

        mm.flush()
        mm.close()

    end: float = time.time()
    print(f"[Rebuilding File] Time taken: {end - start} seconds")

def patch_item_sort(items: list[ItemEntry]):
    shutil.copyfile("builds/item/ITEMSORT.DAT", f"builds/sort-r{len(items)}.dat")

    with open(f"builds/sort-r{len(items)}.dat", "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

        entries: int = int.from_bytes(mm.read(4))
        entry_size: int = ctypes.sizeof(ItemSortEntry)
        data_end: int = entries * entry_size + 4
        mm.resize(data_end + entry_size * len(items))

        mm.seek(0)
        entries += len(items)
        mm.write(entries.to_bytes(4))

        mm.seek(data_end)

        for i, item in enumerate(items):
            new_item: ItemSortEntry = ItemSortEntry.from_item_generic(2000 + i, item)
            mm.write(bytearray(new_item))

        mm.flush()
        mm.close()

if __name__ == '__main__':
    add_items(1000)