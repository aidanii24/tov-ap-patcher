import ctypes
import mmap
import json
import os

from vesperia_types import ArtesHeader, ArtesEntry


class VesperiaPatcher():
    build_dir: str = os.path.join(os.getcwd(), "builds")

    def patch_artes(self):
        target: str = os.path.join(self.build_dir, "BTL_PACK", "0004.ext", "ALL.0000")
        assert os.path.isfile(target)

        original_data_file: str = os.path.join(self.build_dir, "manifests", "0004R.json")
        assert os.path.isfile(original_data_file)

        patch_file: str = os.path.join(".", "artifacts", "tovde.appatch")
        assert os.path.isfile(patch_file)

        patches = {int(key): value for key, value in json.load(open(patch_file))['artes'].items()}
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
            header_size: int = ctypes.sizeof(ArtesHeader)

            header: ArtesHeader = ArtesHeader.from_buffer_copy(mm.read(header_size))

            mm.seek(header_size)
            count: int = 0
            while len(patched_data) and mm.tell() < header.entry_end:
                next_entry: int = int.from_bytes(mm.read(4), byteorder="little")
                mm.seek(4, 1)
                arte_id: int = int.from_bytes(mm.read(4), byteorder="little")

                if arte_id in patched_data:
                    mm.write(bytearray(patched_data[arte_id]))
                    del patched_data[arte_id]

                count += 1

            print(f"Patched {count} entries")

            mm.close()


if __name__ == "__main__":
    patcher = VesperiaPatcher()
    patcher.patch_artes()