import ctypes
import json
import mmap
import time

from vesperia_types import VesperiaStructureEncoder, ArtesHeader, ArtesEntry

def arte_to_json():
    test_file: str = "../builds/BTL_PACK/0004.ext/ALL.0000"

    start: float = time.time()

    artes: list[ArtesEntry] = []
    strings: list[str] = []

    with open(test_file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        mm.seek(0)
        header_size: int = ctypes.sizeof(ArtesHeader)

        header : ArtesHeader = ArtesHeader.from_buffer_copy(mm.read(header_size))

        mm.seek(ctypes.sizeof(ArtesHeader))
        for count in range(header.entries):
            artes_size: int = int.from_bytes(mm.read(4), byteorder="little")
            mm.seek(-4, 1)
            artes.append(ArtesEntry.from_buffer_copy(mm.read(artes_size)))

        strings = (mm.read(-1).decode('utf-8').rstrip("\x00").split("\x00"))

        mm.close()

    with open("../builds/manifests/0004R.json", "w+") as f:
        manifest: dict = {"artes": artes, "strings": strings}
        json.dump(manifest, f, cls=VesperiaStructureEncoder, indent=4)

        f.close()

    end: float = time.time()
    print(f"[Writing JSON] Time taken: {end - start} seconds")

    print(f"Artes: {len(artes)} | Strings: {len(strings)}")