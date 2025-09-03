import ctypes
import json
import mmap
import os


class VesperiaFileEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ctypes.Structure):
            return obj.__dict__

        return super().default(obj)

class SkillsHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic_number", ctypes.c_char * 8),
        ("entries", ctypes.c_uint32),
        ("entry_end", ctypes.c_uint32),
    ]

    def __init__(self, entries: int, entry_end: int):
        super(SkillsHeader).__init__("T8BTSK  ", entries, entry_end)

class SkillsEntry(ctypes.Structure):
    """Byte Structure Template for Skill Entries in file data64/btl.svo/BTL_PACK.DAT/0010"""
    _pack_ = 1
    _fields_ = [
        ("next_entry_offset", ctypes.c_uint32),
        ("entry", ctypes.c_uint32),
        ("id", ctypes.c_uint32),
        ("string_ref_offset", ctypes.c_uint64),
        ("name_string_index", ctypes.c_uint32),
        ("desc_string_index", ctypes.c_uint32),
        ("unknown1", ctypes.c_uint32),
        ("unknown2", ctypes.c_uint32),
        ("sp_cost", ctypes.c_uint32),
        ("lp_cost", ctypes.c_uint32),
        ("symbol", ctypes.c_uint32),
        ("symbol_weight", ctypes.c_uint32),
        ("paramater1", ctypes.c_float),
        ("paramater2", ctypes.c_float),
        ("paramater3", ctypes.c_float),
        ("is_equippable", ctypes.c_uint32),
    ]

    name: str = "SKILL_NONE"

def generate_skills_manifest(filename: str, skills: list[SkillsEntry], strings: list[str]):
    data: dict[str, list] = {"entries": skills, "strings": strings}

    with open(filename, "w+") as f:
        json.dump(data, f, cls=VesperiaFileEncoder, indent=4)
        f.close()

def generate_skills_file(file: str, header: SkillsHeader, skills: list[SkillsEntry], strings: list[str]):
    with open(file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

        size: int = (ctypes.sizeof(SkillsHeader) +
                     ctypes.sizeof(SkillsEntry) * len(skills) +
                     sum(len(i) + 1 for i in strings))
        mm.resize(size)

        mm.write(bytearray(header))
        for skill in skills:
            mm.write(bytearray(skill))

        for string in strings:
            mm.write(("x\00" + string).encode('utf-8'))

        mm.flush()
        f.close()