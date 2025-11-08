import ctypes
import mmap
import json
import os


class VesperiaPatcher():
    def __init__(self, build_dir: str):
        self.build_dir = build_dir

    def patch_artes(self):
        target: str = os.path.join(self.build_dir, "BTL_PACK", "0004.ext", "ALL.0000")
        assert os.path.isfile(target)

        original_data_file: str = os.path.join(self.build_dir, "manifests", "0004R.json")
        assert os.path.isfile(original_data_file)

        patch_file: str = os.path.join(".", "artifacts", "tovde.appatch")
        assert os.path.isfile(patch_file)

        patches = {int(key): value for key, value in json.load(open(patch_file))['artes'].items()}
        assert patches

        patch_data: dict = json.load(open(original_data_file))['artes']

        # with open(target, 'r+b') as f:
        #     mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
        #
        #     mm.seek(0)
        #     header_size: int = ctypes.sizeof(ArtesHeader)
        #
        #     header: ArtesHeader = ArtesHeader.from_buffer_copy(mm.read(header_size))
        #
        #     mm.seek(header_size)
        #     count: int = 0
        #     while len(patches) and mm.tell() < header.entry_end:
        #         next_entry: int = int.from_bytes(mm.read(4), byteorder="little")
        #         mm.seek(4, 1)
        #         arte_id: int = int.from_bytes(mm.read(4), byteorder="little")
        #
        #         if arte_id in patches:
        #             del patches[arte_id]
        #             print("Found", arte_id)
        #
        #         mm.seek(next_entry - 12, 1)
        #         count += 1
        #
        #     mm.close()