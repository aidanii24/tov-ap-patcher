import ctypes
import mmap
import json
import os

import vesperia_types as vtypes
from vesperia_types import SkillsEntry


class VesperiaPatcher:
    build_dir: str = os.path.join(os.getcwd(), "builds")
    data_dir: str = os.path.join(os.getcwd(), "data")

    def __init__(self, patcher_id: str):
        self.build_dir = os.path.join(self.build_dir, patcher_id)

    def patch_artes(self, arte_patches: dict):
        target: str = os.path.join(self.build_dir, "BTL_PACK", "0004.ext", "ALL.0000")
        assert os.path.isfile(target)

        original_data_file: str = os.path.join(self.data_dir, "artes.json")
        assert os.path.isfile(original_data_file), f"Cannot find {original_data_file}"

        patches = {int(key): value for key, value in arte_patches.items()}
        assert patches

        original_data: dict = json.load(open(original_data_file))['artes']

        total_searched: int = 0
        total_patched: int = 0
        patched_data: dict = {}

        for arte in original_data:
            if arte['entry'] in patches:
                patched_data[arte['entry']] = {**arte, **patches[arte['entry']]}
                total_patched += 1

            total_searched += 1
            if total_patched >= len(patches):
                break

        with open(target, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

            mm.seek(0)
            header_size: int = ctypes.sizeof(vtypes.ArtesHeader)

            header: vtypes.ArtesHeader = vtypes.ArtesHeader.from_buffer_copy(mm.read(header_size))

            mm.seek(header_size)
            count: int = 0
            while len(patched_data) and mm.tell() < header.entry_end:
                next_entry: int = int.from_bytes(mm.read(4), byteorder="little")
                arte_entry: int = int.from_bytes(mm.read(4), byteorder="little")

                if arte_entry in patched_data:
                    mm.seek(-8, 1)

                    arte_data: vtypes.ArtesEntry = vtypes.ArtesEntry(*patched_data[arte_entry].values())
                    mm.write(bytearray(arte_data))
                    del patched_data[arte_entry]
                else:
                    mm.seek(next_entry - 8, 1)
                count += 1

            mm.flush()
            mm.close()

    def patch_skills(self, skill_patches: dict):
        target: str = os.path.join(self.build_dir, "BTL_PACK", "0010.ext", "ALL.0000")
        assert os.path.isfile(target)

        original_data_file: str = os.path.join(self.data_dir, "skills.json")
        assert os.path.isfile(original_data_file), f"Cannot find {original_data_file}"

        patches = {int(key): value for key, value in skill_patches.items()}
        assert patches

        original_data: dict = json.load(open(original_data_file))['skills']

        patched_data: dict = {}
        for entry, patch in sorted(patches.items()):
            assert entry < len(original_data), f"Skil Entry {entry} is not a recognized skill"
            assert entry == original_data[entry]['entry'], f"There was an error resolving patch for Skill Entry {entry}"

            patched_data[entry] = {**original_data[entry], **patch}

        with open(target, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
            mm.seek(0)

            header_size: int = ctypes.sizeof(vtypes.SkillsHeader)
            entry_size: int = ctypes.sizeof(vtypes.SkillsEntry)

            header = vtypes.SkillsHeader.from_buffer_copy(mm.read(header_size))

            for entry, patch in patched_data.items():
                mm.seek(header_size + (entry * entry_size))

                skills_data: vtypes.SkillsEntry = SkillsEntry(*patch.values())
                mm.write(bytearray(skills_data))

            mm.flush()
            mm.close()