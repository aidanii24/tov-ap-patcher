from enum import IntEnum
import ctypes
import mmap
import time
import os

from packer import VesperiaPacker
from vesperia_types import TSSHeader

from debug import test_structure


class InstructionType(IntEnum):
    LEARN_ARTE = 0x183
    EQUIP_ARTE = 0x327
    CHECK_ARTE = 0x8B

    LEARN_SKILL = 0x6C
    EQUIP_SKILL = 0x2A4
    CHECK_SKILL = 0x98

    LEARN_TITLE = 0x1C0
    EQUIP_TITLE = 0x27B
    CHECK_TITLE = 0x2EE

    EQUIP_ITEM1 = 0xCB
    ADD_ITEM1 = 0xCC
    GET_ITEM1 = 0XCD
    GET_ITEM2 = 0x3BB
    EQUIP_ITEM2 = 0x3BC
    ADD_ITEM2 = 0x3BD

    UNLOCK_EVENT = 0xFFF

    @classmethod
    def is_valid(cls, inst_type: int) -> bool:
        return any(inst_type == inst for inst in cls)

    @classmethod
    def get_item_types(cls) -> list[int]:
        return [cls.EQUIP_ITEM1, cls.ADD_ITEM1, cls.GET_ITEM1, cls.GET_ITEM2, cls.EQUIP_ITEM2, cls.ADD_ITEM2]

class InstructionData:
    def __init__(self, instruction_type: int, instruction_id: int, address: int, slot: int, character: int):
        self.instruction_type: int = instruction_type
        self.instruction_id: int = instruction_id
        self.address: int = address
        self.slot: int = slot
        self.character: int = character

    def __new__(cls, instruction_type: int, instruction_id: int, address: int, slot: int, character: int):
        if instruction_type == 0xFFFFFF: return None
        return InstructionType(instruction_type, instruction_id, address, slot, character)


packer: VesperiaPacker

def get_events():
    work_dir: str = os.path.join("../builds/scenario")
    assert os.path.isdir(work_dir)

    scenario: str = os.path.join(work_dir, "ENG")
    assert os.path.isdir(scenario)

    start: float = time.time()

    files = os.listdir(scenario)
    for file in files:
        if os.path.isdir(os.path.join(scenario, file)):
            continue

        packer.decompress_scenario(file)

    dirs = [d for d in os.listdir(scenario)
            if d.isdigit()]

    count: int = 0
    for d in dirs:
        print(d)
        assert os.path.isfile(os.path.join(work_dir, d, d + ".dec"))
        count += 1

    end: float = time.time()
    print(f"[Scenario Walking] Time Taken: {end - start}")
    print("Total Files: ", count)

def find_instruction():
    target: str = os.path.join("./builds/scenario/1018/1018.dec")
    assert os.path.isfile(target)

    type_size: int = 2
    find_target: bytes = (0xFFFFFFFF).to_bytes(4, byteorder="little")

    instructions: list[InstructionData] = []

    with open(target, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        header = TSSHeader.from_buffer_copy(mm.read(ctypes.sizeof(TSSHeader)))

        pos: int = mm.find(find_target, header.code_start, mm.size())
        next_pos: int = mm.find(find_target, pos + 4, mm.size())

        while pos >= 0 or next_pos >= 0:
            slot: int = 0xFFFFFF
            character: int = 0xFFFFFF

            mm.seek(pos, 1)
            inst_type = int.from_bytes(mm.read(type_size), byteorder="little")

            if InstructionType.is_valid(inst_type):
                if inst_type == InstructionType.EQUIP_ARTE:
                    mm.seek(pos - 0xC - 0x4)
                    inst_id = int.from_bytes(mm.read(4), byteorder="little")

                    mm.seek(pos - 0x1C - 0x4)
                    slot = int.from_bytes(mm.read(1), byteorder="little")

                    mm.seek(pos - 0x28 - 0x4)
                    character = int.from_bytes(mm.read(4), byteorder="little")
                elif inst_type in InstructionType.get_item_types():
                    mm.seek(next_pos - 0x1E)
                    sub_type: int = int.from_bytes(mm.read(2), byteorder="little")
                    if sub_type == 0x203:
                        mm.seek(pos - 0x1C - 0x4)
                        slot = int.from_bytes(mm.read(1), byteorder="little")

                        mm.seek(pos - 0x2C - 0x4)
                        inst_id = int.from_bytes(mm.read(4), byteorder="little")
                    else:
                        mm.seek(pos - 0x18 - 0x4)
                        slot = int.from_bytes(mm.read(1), byteorder="little")

                        mm.seek(pos - 0x24 - 0x4)
                        inst_id = int.from_bytes(mm.read(4), byteorder="little")
                else:
                    mm.seek(pos - 0xC - 0x4)
                    inst_id = int.from_bytes(mm.read(4), byteorder="little")

                    mm.seek(pos - 0x1C - 0x4)
                    character = int.from_bytes(mm.read(4), byteorder="little")

                instructions.append(InstructionData(inst_type, inst_id, pos, slot, character))

                if inst_type in [InstructionType.CHECK_ARTE, InstructionType.CHECK_TITLE, 0x000F]:
                    event_pos: int = mm.find(find_target, pos + 4, next_pos)

                    while event_pos >= 0:
                        if event_pos % 4 == 0:
                            mm.seek(event_pos - 0x26)
                            sub_type: int = int.from_bytes(mm.read(2), byteorder="little")
                            if sub_type == 0x207:
                                character = -1

                                mm.seek(event_pos)
                                inst_type = int.from_bytes(mm.read(2), byteorder="little")

                                mm.seek(event_pos - 0x24)
                                inst_id = int.from_bytes(mm.read(4), byteorder="little")
                            else:
                                mm.seek(event_pos - 0x1C)
                                character = int.from_bytes(mm.read(4), byteorder="little")

                                mm.seek(event_pos)
                                inst_type = int.from_bytes(mm.read(2), byteorder="little")

                                mm.seek(event_pos - 0xC)
                                inst_id = int.from_bytes(mm.read(4), byteorder="little")

                            instructions.append(InstructionData(inst_type, inst_id, pos, slot, character))

                        event_pos: int = mm.find(find_target, event_pos + 4, next_pos)

            pos = next_pos
            next_pos = mm.find(find_target, pos + 4, mm.size())
            while next_pos % 4 != 0 or next_pos != -1:
                next_pos = mm.find(find_target, next_pos + 4, mm.size())

if __name__ == "__main__":
    pass
    # packer = VesperiaPacker()
    # packer.check_dependencies()