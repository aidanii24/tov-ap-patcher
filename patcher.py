import ctypes
import mmap
import json
import os

import utils
import vesperia_types as vtypes
from vesperia_types import SkillsEntry, ChestHeader, ChestEntry, ChestItemEntry


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

        header_size: int = ctypes.sizeof(vtypes.ArtesHeader)

        with open(target, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

            mm.seek(0)

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
            assert entry == original_data[entry]['entry'], \
                f"There was an error resolving the patch for Skill Entry {entry}"

            patched_data[entry] = {**original_data[entry], **patch}

        header_size: int = ctypes.sizeof(vtypes.SkillsHeader)
        entry_size: int = ctypes.sizeof(vtypes.SkillsEntry)

        with open(target, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
            mm.seek(0)

            for entry, patch in patched_data.items():
                mm.seek(header_size + (entry * entry_size))

                skills_data: vtypes.SkillsEntry = SkillsEntry(*patch.values())
                mm.write(bytearray(skills_data))

            mm.flush()
            mm.close()

    def patch_items(self, item_patches: dict):
        target: str = os.path.join(self.build_dir, "item", "ITEM.DAT")
        assert os.path.isfile(target)

        if 'base' in item_patches:
            self.patch_items_base(target, item_patches['base'])

        if 'custom' in item_patches:
            self.patch_items_custom(target, item_patches['custom'])

    def patch_items_base(self, target_file: str, item_patches: dict):
        patches: dict[int, dict] = {int(key): value for key, value in item_patches.items()}

        original_data_file: str = os.path.join(self.data_dir, "item.json")
        assert os.path.isfile(original_data_file), f"Cannot find {original_data_file}"

        original_data: dict = json.load(open(original_data_file))["items"]

        patched_data: dict = {}
        for entry, patch in sorted(patches.items()):
            assert entry < len(original_data), f"Item Entry {entry} is not a recognized item"
            assert entry == original_data[entry]['entry'], \
                f"There was an error resolving patch data for Item Entry {entry}"

            patched_data[entry] = {**original_data[entry], **patch}

        entry_size: int = ctypes.sizeof(vtypes.ItemEntry)

        with open(target_file, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
            mm.seek(0)

            for entry, patch in patched_data.items():
                mm.seek(entry * entry_size)

                items_data = vtypes.ItemEntry(**patch)
                mm.write(bytearray(items_data))

            mm.flush()
            mm.close()

    def patch_items_custom(self, target_file: str, item_patches: dict):
        pass

    def patch_shops(self, shop_patches: dict, lang: str = "ENG"):
        target: str = os.path.join(self.build_dir, "language", f".{lang}.dec", "0.dec")
        assert os.path.isfile(target)

        if 'commons' in shop_patches or 'uniques' in shop_patches:
            patches: dict = {}
            if 'commons' in shop_patches:
                patches['commons'] = shop_patches['commons']
            if 'uniques' in shop_patches:
                patches['uniques'] = shop_patches['uniques']

            self.patch_shops_precise(target, patches)

    def patch_shops_precise(self, target_file: str, patches: dict):
        original_data_file: str = os.path.join(self.data_dir, "shop_items.json")
        assert os.path.isfile(original_data_file), f"Cannot find {original_data_file}"

        original_data: dict = json.load(open(original_data_file), object_hook=utils.keys_to_int)

        shop_items: dict = {}
        if 'commons' in patches:
            for entry in patches['commons']:
                for shop in entry['shops']:
                    shop_items.setdefault(shop, set()).update(entry['items'])

            for entry in original_data['items']['commons']:
                m_shops: list = [shop for shop in entry['shops'] if shop in original_data['missables']]
                if not m_shops: continue
                for shop in m_shops:
                    shop_items.setdefault(shop, set()).update(entry['items'])

        if 'uniques' in patches:
            for shop, items in patches['uniques'].items():
                shop_items.setdefault(shop, set()).update(items)

            for shop in original_data['missables']:
                if shop not in original_data['items']['uniques']: continue
                shop_items.setdefault(shop, set()).update(original_data['items']['uniques'][shop])

        for shop, items in (shop_items.items()):
            shop_items[shop] = sorted(items)

        shop_items = dict(sorted(shop_items.items()))

        item_start: int = 0x980
        item_count: int = 1521

        with open(target_file, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
            mm.seek(item_start)

            count: int = 0
            for shop, items in shop_items.items():
                if count >= item_count: break
                for item in items:
                    shop_entry_data = vtypes.ShopItemEntry(shop, item)
                    mm.write(bytearray(shop_entry_data))

                count += 1

            mm.flush()
            mm.close()

    def patch_chests(self, target_file: str, patches: dict):
        path: str = os.path.join(self.build_dir, "maps", target_file, "0004.tlzc")
        assert os.path.isfile(path), f"Cannot find {path}"

        header_size: int = ctypes.sizeof(ChestHeader)
        chest_size: int = ctypes.sizeof(ChestEntry)
        item_size: int = ctypes.sizeof(ChestItemEntry)

        with open(path, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

            header = ChestHeader.from_buffer_copy(mm.read(header_size))

            chest_entries: list[dict] = []

            mm.seek(header.chest_start)
            for _ in range(header.chest_entries):
                chest_id: int = int.from_bytes(mm.read(4), byteorder="little")

                mm.seek(0x38, 1)
                item_count: int = int.from_bytes(mm.read(4), byteorder="little")

                chest_entries.append({
                    "chest_id": chest_id,
                    "item_count": item_count,
                })

            position: int = header.item_start
            for chest in chest_entries:
                if chest['chest_id'] in patches:
                    mm.seek(position)
                    for i, item in enumerate(patches[chest['chest_id']]):
                        item = ChestItemEntry(*item.values())
                        mm.write(bytearray(item))

                        # Break in case of mismatched item count and prevent writing to other chest's item data
                        if i - 1 >= chest['item_count']:
                            break

                # Correct position in case a chest/item is missing from the patch data
                position += chest['item_count'] * item_size

            mm.flush()
            mm.close()