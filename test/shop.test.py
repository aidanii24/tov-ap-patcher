import ctypes
import json
import mmap
import time
import os

from vesperia_types import VesperiaStructureEncoder, ShopItemEntry
import debug


item_start: int = 0x980
base_shop_items: int = 1521

def to_json():
    file: str = "../builds/scenario/0/0.dec"
    assert os.path.isfile(file)

    manifest: str = "../builds/manifests/shop_items.json"

    item_entry_size: int = ctypes.sizeof(ShopItemEntry)

    item_entries: list[ShopItemEntry] = []

    start: float = time.time()

    with open(file, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        mm.seek(item_start)
        for _ in range(base_shop_items):
            item_entries.append(ShopItemEntry.from_buffer_copy(mm.read(item_entry_size)))

        mm.close()

    mode: str = "w+"
    if not os.path.isfile(manifest): mode = "x+"

    with open(manifest, mode) as f:
        json.dump(item_entries, f, cls=VesperiaStructureEncoder, indent=4)

        f.close()

    end: float = time.time()
    print(f"[Shop Data Extraction] Time Taken: {end - start} seconds")

def append_item():
    file: str = "../builds/scenario/0/0.dec"
    assert os.path.isfile(file)

    item_size: int = ctypes.sizeof(ShopItemEntry)
    item_end: int = item_start + (item_size * base_shop_items)

    # Zaphias Shop I - Adding Overdrive Big Kid
    new_item: ShopItemEntry = ShopItemEntry(7, 1841)

    start: float = time.time()

    with open(file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

        original_size: int = mm.size()

        mm.resize(mm.size() + item_size)
        mm.move(item_end + item_size, item_end, original_size - item_end)

        mm.seek(item_end)
        mm.write(bytearray(new_item))

        mm.flush()
        mm.close()

    end: float = time.time()
    print(f"[Shop Data Addition] Time Taken: {end - start} seconds")

if __name__ == "__main__":
    append_item()