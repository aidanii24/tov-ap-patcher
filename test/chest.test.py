import ctypes
import mmap
import os

from debug import test_structure

from vesperia_types import ChestHeader, ChestItemEntry

def to_bytes():
    chest_item: ChestItemEntry = ChestItemEntry(17, 1)

    test_structure(chest_item)

def test_header():
    subject: str = "../builds/npc/MYS_D00/MYS_D00.tlzc.ext/0004.tlzc"
    assert os.path.isfile(subject)

    header: ChestHeader = ChestHeader()
    header_size: int = ctypes.sizeof(ChestHeader)
    item_size: int = ctypes.sizeof(ChestItemEntry)

    items: list[ChestItemEntry] = []

    with open(subject, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

        header = ChestHeader.from_buffer_copy(mm.read(header_size))

        mm.seek(header.item_start)
        for i in range(header.item_entries):
            items.append(ChestItemEntry.from_buffer_copy(mm.read(item_size)))

        mm.close()

    for item in items:
        test_structure(item)

if __name__ == "__main__":
    test_header()