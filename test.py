import struct
import ctypes
import json
import mmap
import math
import time

from vesperia_types import ArtesHeader, ArtesEntry, VesperiaStructureEncoder

def test_arte_structure():
    sample_arte = ArtesEntry(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, [8, 2, 3, 4, 5])

    for attribute, ctype in sample_arte._fields_:
        value = getattr(sample_arte, attribute)
        as_hex = ""

        if type(value) == int:
            as_hex = hex(value)
        elif type(value) == float:
            as_hex = hex(struct.unpack('<I', struct.pack('<f', value))[0])
        elif type(bytes):
            if "Array" in type(value).__name__:
                print(type(type(value)))
                print("Array Test:", issubclass(type(value), ctypes.Array))
                value = [*value]
                as_hex = [hex(arte_id) for arte_id in value]
            else:
                as_hex = value.hex()
        else:
            as_hex = "Unhandled"

        print(f"{attribute}: {value} | ({as_hex})")

    print(json.dumps(sample_arte, cls=VesperiaStructureEncoder, indent=4))
    as_bytes = bytearray(sample_arte)
    print(as_bytes)
    print("\n 0 1 2 3  4 5 6 7  8 9 A B  C D E F")
    for _ in range(math.ceil(len(as_bytes) / 16)):
        chunk = as_bytes[_ * 16: _ * 16 + 16].hex()
        final = ""
        for _ in range(min(4, math.ceil(len(chunk) / 4))):
            final += chunk[_ * 8: _ * 8 + 8] + " "

        print(final)

    copy_arte: ArtesEntry = ArtesEntry.from_buffer_copy(as_bytes)
    copy_bytes = bytearray(copy_arte)
    print(copy_bytes)


def to_json():
    test_file: str = "builds/BTL_PACK/0004.ext/ALL.0000"

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

    with open("builds/0004R.json", "x+") as f:
        manifest: dict = {"artes": artes, "strings": strings}
        json.dump(manifest, f, cls=VesperiaStructureEncoder, indent=4)

        f.close()

    end: float = time.time()
    print(f"[Writing JSON] Time taken: {end - start} seconds")

    print(f"Artes: {len(artes)} | Strings: {len(strings)}")

def from_json():
    start = time.time()

    artes: list[ArtesEntry] = []
    strings: list[str] = []

    with open("builds/0004R.json", "r") as f:
        data = json.load(f)

        artes = [ArtesEntry(*entry.values()) for entry in data["artes"]]
        strings = data["strings"]

        f.close()

    with open("builds/0004R.0000", "x+") as f:
        data_end: int = sum([ctypes.sizeof(arte) for arte in artes]) + ctypes.sizeof(ArtesHeader)
        string_list: str = "".join(string + "\x00" for string in strings)
        header: ArtesHeader = ArtesHeader(len(artes), data_end)

        f.truncate(ctypes.sizeof(ArtesHeader) + data_end + len(string_list))
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

        mm.write(bytearray(header))
        for arte in artes:
            mm.write(bytearray(arte))

        mm.write(string_list.encode())

        mm.flush()
        mm.close()

    end: float = time.time()
    print(f"[Rebuilding File] Time taken: {end - start} seconds")

if __name__ == '__main__':
    from_json()