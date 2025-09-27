import ctypes
import mmap
import os

from vesperia_types import TSSHeader, TSSStringEntry

from debug import test_structure, format_bytes


def parse_tss():
    test_file: str = "../builds/strings/string_dic_ENG.so"
    dump_file: str = "../builds/strings/output.txt"
    stop: bytes = (0xFFFFFFFF).to_bytes(4, byteorder="little")

    header_size: int = ctypes.sizeof(TSSHeader)

    string_entries: list = []

    with open(test_file, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        header = TSSHeader.from_buffer_copy(mm.read(header_size))
        mm.seek(header.code_start)

        stop_index: int = header.code_length
        last_max: int = header.code_start

        print("Getting Entries...")
        while stop_index >= 0:
            stop_index = mm.find(stop, last_max + 4, mm.size())

            length: int = stop_index - last_max
            if length == 0x64 or length == 0x48:
                mm.seek(last_max)
                new_entry: TSSStringEntry = TSSStringEntry.from_buffer(mm.read(length))
                string_entries.append(new_entry)

            last_max: int = stop_index
            mm.seek(last_max + 4)

        print("Entries:", len(string_entries))
        print("Getting Strings...")
        out = open(dump_file, "w")
        for string in string_entries:
            out.write(f"\n{string.string_id}:")
            start: int = string.pointer_eng + header.text_start
            mm.seek(start)
            end: int = mm.find("\x00".encode(), start)

            if end == -1:
                raise AssertionError(f"Cannot find String endpoint for {string.string_id}")

            if end >= string.pointer_eng:
                result = mm.read(end - start)

                try:
                    decoded = "\t" + (result.decode("utf-8"))
                    out.write(decoded)
                except UnicodeDecodeError:
                    continue

        out.close()

        mm.close()
        f.close()


if __name__ == "__main__":
    test = TSSStringEntry(50143, 0x35099, 0x35134)
    format_bytes(test.encode_tss())