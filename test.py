import struct

from vesperia_types import ArtesHeader, ArtesEntry

def test_arte_structure():
    sample_arte = ArtesEntry(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 2, 3, 4, 5, 6)

    for attribute, ctype in sample_arte._fields_:
        value = getattr(sample_arte, attribute)
        as_hex = ""

        if type(value) == int:
            as_hex = hex(value)
        elif type(value) == float:
            as_hex = hex(struct.unpack('<I', struct.pack('<f', value))[0])
        elif type(bytes):
            if "Array" in type(value).__name__:
                value = [*value]
                as_hex = [hex(id) for id in value]
            else:
                as_hex = value.hex()
        else:
            as_hex = "Unhandled"

        print(f"{attribute}: {value} | ({as_hex})")

if __name__ == '__main__':
    test_arte_structure()