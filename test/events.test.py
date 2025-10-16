from enum import IntEnum
import ctypes
import mmap
import time
import json
import os

from packer import VesperiaPacker
from vesperia_types import TSSHeader

from debug import test_structure


arte_table: dict = {}
skill_table: dict = {}
item_table: dict = {}

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
    def get_arte_events(cls) -> list[int]:
        return [cls.LEARN_ARTE, cls.EQUIP_ARTE, cls.CHECK_ARTE]

    @classmethod
    def get_skill_events(cls) -> list[int]:
        return [cls.LEARN_SKILL, cls.EQUIP_SKILL, cls.CHECK_SKILL]

    @classmethod
    def get_title_events(cls) -> list[int]:
        return [cls.LEARN_TITLE, cls.EQUIP_TITLE, cls.CHECK_TITLE]

    @classmethod
    def get_item_types(cls) -> list[int]:
        return [cls.EQUIP_ITEM1, cls.ADD_ITEM1, cls.GET_ITEM1, cls.GET_ITEM2, cls.EQUIP_ITEM2, cls.ADD_ITEM2]

class Character(IntEnum):
    UNKNOWN = 0
    YURI = 1
    ESTELLE = 2
    KAROL = 3
    RITA = 4
    RAVEN = 5
    JUDITH = 6
    REPEDE = 7
    FLYNN = 8
    PATTY = 9

    @classmethod
    def _missing_(cls, vakue):
        return cls.UNKNOWN

class InstructionData:
    def __init__(self, instruction_type: int, data_id: int, address: int, slot: int, character: int):
        self.instruction_type: int = instruction_type
        self.data_id: int = data_id
        self.address: int = address
        self.slot: int = slot
        self.character: int = character

    def __new__(cls, instruction_type: int, instruction_id: int, address: int, slot: int, character: int):
        if not InstructionType.is_valid(instruction_type): return None
        return super().__new__(cls)

    def report(self):
        report: str = f"{hex(self.address)} {InstructionType(self.instruction_type).name} | "

        if self.instruction_type in InstructionType.get_arte_events():
            arte: str = arte_table[self.data_id] if self.data_id in arte_table else f"Unknown Arte {self.data_id}"
            report += f"{Character(self.character).name}'s {arte}"
        elif self.instruction_type in InstructionType.get_skill_events():
            skill: str = skill_table[self.data_id] if self.data_id in skill_table else f"Unknown Skill {self.data_id}"
            report += f"{Character(self.character).name}'s {skill_table[self.data_id]}"
        elif self.instruction_type in InstructionType.get_title_events():
            report += f"{Character(self.character).name}'s Title ID {self.data_id}"
        elif self.instruction_type == InstructionType.UNLOCK_EVENT:
            if self.data_id <= 1971:
                report += f"{Character(self.character).name}-related "
            report += "unknown event"
        elif self.instruction_type in InstructionType.get_item_types():
            item: str = item_table[self.data_id] if self.data_id in item_table else f"Unknown Item {self.data_id}"

            if self.instruction_type in [InstructionType.ADD_ITEM1, InstructionType.ADD_ITEM2]:
                if self.data_id <= 1971:
                    report += f"{self.slot}x "
                report += f"{item}"
            elif self.instruction_type in [InstructionType.GET_ITEM1, InstructionType.GET_ITEM2]:
                if self.data_id <= 1971:
                    report += f"{item}"
                else:
                    report += "unknown item"
            elif self.instruction_type in [InstructionType.EQUIP_ITEM1, InstructionType.EQUIP_ITEM2]:
                if self.data_id <= 1971:
                    report += f"{self.slot}x {item}"
                else:
                    report += f"{item}\t< MIGHT BE EXTRACTED FROM FUNCTION CALL >"
        else:
            report += "unknown event"

        return report

packer: VesperiaPacker

def strip_formatting(string: str) -> str:
    return string.replace("\n", "").replace("\t", "").replace("\r", "")

def get_meta_data():
    manifest: str = "../builds/manifests"
    assert os.path.isdir(manifest)

    string_data: str = os.path.join(manifest, "strings.json")
    artes_data: str = os.path.join(manifest, "0004R.json")
    skills_data: str = os.path.join(manifest, "skills.json")
    items_data: str = os.path.join(manifest, "item.json")

    assert os.path.isfile(string_data)
    assert os.path.isfile(artes_data)
    assert os.path.isfile(skills_data)
    assert os.path.isfile(items_data)

    strings = json.load(open(string_data))
    artes = json.load(open(artes_data))["artes"]
    skills = json.load(open(skills_data))["skills"]
    items = json.load(open(items_data))["items"]

    global arte_table
    arte_table = {arte["id"]: strip_formatting(strings[f"{str(arte['name_string_key'])}"]) for arte in artes
                  if str(arte['name_string_key']) in strings}

    global skill_table
    skill_table = {skill["id"]: strip_formatting(strings[f"{str(skill['name_string_key'])}"]) for skill in skills
                             if str(skill['name_string_key']) in strings}

    global item_table
    item_table = {item["id"]: strip_formatting(strings[f"{str(item['name_string_key'])}"]) for item in items
                            if str(item['name_string_key']) in strings}

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

def find_instructions():
    target: str = os.path.join("./builds/scenario/1018/1018.dec")
    assert os.path.isfile(target)

    type_size: int = 2
    find_target: bytes = (0xFFFFFFFF).to_bytes(4, byteorder="little")

    instructions: list[InstructionData] = []

    start = time.time()

    with open(target, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        header = TSSHeader.from_buffer_copy(mm.read(ctypes.sizeof(TSSHeader)))

        pos: int = mm.find(find_target, header.code_start, mm.size())
        next_pos: int = mm.find(find_target, pos + 4, mm.size())

        scans: int = 0
        while pos >= 0 and next_pos >= 0:
            slot: int = 0xFFFFFF
            character: int = 0xFFFFFF

            mm.seek(pos - 0x4)
            inst_type = int.from_bytes(mm.read(type_size), byteorder="little")

            # print(f"Scan {scans} > Current: {hex(pos)} | Next: {hex(next_pos)} | Type: {hex(inst_type)} "
            #       f"{InstructionType(inst_type).name if InstructionType.is_valid(inst_type) else ""}")

            if InstructionType.is_valid(inst_type):
                if inst_type == InstructionType.EQUIP_ARTE:
                    mm.seek(pos - 0xC - 0x4)
                    data_id = int.from_bytes(mm.read(4), byteorder="little")

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
                        data_id = int.from_bytes(mm.read(4), byteorder="little")
                    else:
                        mm.seek(pos - 0x18 - 0x4)
                        slot = int.from_bytes(mm.read(1), byteorder="little")

                        mm.seek(pos - 0x24 - 0x4)
                        data_id = int.from_bytes(mm.read(4), byteorder="little")
                else:
                    mm.seek(pos - 0xC - 0x4)
                    data_id = int.from_bytes(mm.read(4), byteorder="little")

                    mm.seek(pos - 0x1C - 0x4)
                    character = int.from_bytes(mm.read(4), byteorder="little")

                instructions.append(InstructionData(inst_type, data_id, pos, slot, character))

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
                                data_id = int.from_bytes(mm.read(4), byteorder="little")
                            else:
                                mm.seek(event_pos - 0x1C)
                                character = int.from_bytes(mm.read(4), byteorder="little")

                                mm.seek(event_pos)
                                inst_type = int.from_bytes(mm.read(2), byteorder="little")

                                mm.seek(event_pos - 0xC)
                                data_id = int.from_bytes(mm.read(4), byteorder="little")

                            instructions.append(InstructionData(inst_type, data_id, pos, slot, character))

                        event_pos: int = mm.find(find_target, event_pos + 4, next_pos)

            pos = next_pos
            next_pos = mm.find(find_target, pos + 4, mm.size())
            while next_pos % 4 != 0 and next_pos > pos:
                next_pos = mm.find(find_target, next_pos + 4, mm.size())

            scans += 1

    end: float = time.time()
    print(f"[Event Scanning ({1018})]\n"
          f"Time Taken: {end - start} seconds\n"
          f"Total Scans: {scans}\n"
          f"Total Events: {len(instructions)}")

    artifact: str = "../helper/artifacts/"
    assert os.path.isdir(artifact)

    output: str = os.path.join(artifact, f"1018.txt")
    with open(output, "w+") as f:
        f.write("--- File 1018 ---------------\n\n")

        for instruction in instructions:
            f.write(instruction.report() + "\n")

        f.close()

if __name__ == "__main__":
    get_meta_data()

    find_instructions()
