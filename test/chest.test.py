import ctypes
import mmap
import os

from GameMeta import IDTables
from debug import test_structure

from packer import VesperiaPacker
from vesperia_types import ChestHeader, ChestEntry, ChestItemEntry

chest_files_data: str = "../helper/artifacts/chest_files"

item_table = IDTables().get_item_table()

def to_bytes():
    chest_item: ChestItemEntry = ChestItemEntry(17, 1)

    test_structure(chest_item)

def test_header(target_file):
    subject: str = "target_file"
    assert os.path.isfile(subject)

    header_size: int = ctypes.sizeof(ChestHeader)
    item_size: int = ctypes.sizeof(ChestItemEntry)

    items: list[ChestItemEntry] = []

    with open(subject, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

        header: ChestHeader = ChestHeader.from_buffer_copy(mm.read(header_size))

        mm.seek(header.item_start)
        for i in range(header.item_entries):
            items.append(ChestItemEntry.from_buffer_copy(mm.read(item_size)))

        mm.close()

    for item in items:
        test_structure(item)

# TODO: Test using async functions to see if it provides better performance
def get_chest_files() -> list[str]:
    packer: VesperiaPacker = VesperiaPacker()
    packer.check_dependencies()

    work_dir: str = os.path.join("../builds/npc")
    assert os.path.isdir(work_dir)

    npc: str = os.path.join(work_dir, "npc")
    assert os.path.isdir(npc)

    maps: list[str] = []
    npc_files = os.listdir(npc)
    for npc_file in npc_files:
        file_name: str = npc_file.strip(".DAT")
        if not os.path.isdir(os.path.join(work_dir, file_name)):
            packer.extract_map(npc_file)

        chests_file: str = os.path.join(work_dir, file_name, f"{file_name}.tlzc.ext", "0004")
        if not os.path.isfile(chests_file):
            continue

        extracted_file: str = chests_file + ".tlzc"
        maps.append(extracted_file)
        if not os.path.isfile(extracted_file):
            packer.decompress_data(chests_file)

    return maps

def get_chests(target) -> dict:
    assert os.path.isfile(target)

    header_size: int = ctypes.sizeof(ChestHeader)
    item_size: int = ctypes.sizeof(ChestItemEntry)

    chests: list[ChestEntry] = []
    chests_table: dict[ChestEntry, list[ChestItemEntry]] = {}

    with open(target, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

        header: ChestHeader = ChestHeader.from_buffer_copy(mm.read(header_size))

        mm.seek(header.chest_start)
        for i in range(header.chest_entries):
            chest_id: int = int.from_bytes(mm.read(4), byteorder="little")

            mm.seek(0x38, 1)
            amount: int = int.from_bytes(mm.read(4), byteorder="little")

            chests.append(ChestEntry(chest_id, amount))

        mm.seek(header.item_start)
        for found_chest in chests:
            for _ in range(found_chest.item_amount):
                chests_table.setdefault(found_chest.chest_id, []).append(ChestItemEntry.from_buffer_copy(mm.read(item_size)))

        mm.close()

    return chests_table

if __name__ == "__main__":
    files: list[str] = []
    if os.path.isfile(chest_files_data):
        print("[-!-] Using Cache!")
        with open(chest_files_data, "r") as f:
            files = [line.replace("\n", "") for line in f.readlines()]
            f.close()
    else:
        files = get_chest_files()
        with open(chest_files_data, "w+") as f:
            files_formatted = [file + "\n" for file in files]
            f.writelines(files_formatted)
            f.close()

    chests: dict = {}
    for file in files:
        file_name: str = file.split("/")[-3]
        if file_name == "NPC": continue
        print(f"Processing {file_name}")
        chests[file_name] = get_chests(file)

    output: str = os.path.join("..", "helper", "artifacts", "chests.txt")
    with open(output, "w+") as f:
        for game_map, contents in chests.items():
            f.write(f"--- {game_map} ---------------------\n")
            for chest, items in contents.items():
                f.write(f"> Chest {chest}: {[f"x{item.amount} "
                                           f"{item_table[item.item_id] if item.item_id in item_table
                                           else f"ID {item.item_id}"}" for item in items]}\n")
            f.write("\n")
