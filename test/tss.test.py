import ctypes
import mmap
import time
import os

from vesperia_types import TSSHeader, TSSStringEntry

from debug import test_structure, format_bytes


def parse_tss():
    test_file: str = "../builds/strings/string_dic_ENG.so"
    dump_file: str = "../builds/strings/output.txt"
    stop: bytes = (0xFFFFFFFF).to_bytes(4, byteorder="little")

    header_size: int = ctypes.sizeof(TSSHeader)

    string_entries: list = []

    start_time: float = time.time()

    with open(test_file, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        header = TSSHeader.from_buffer_copy(mm.read(header_size))
        mm.seek(header.code_start)

        last_max: int = header.code_start
        stop_index: int = mm.find(stop, last_max + 4, header.code_length)

        while stop_index >= 0:
            length: int = stop_index - last_max
            new_entry: TSSStringEntry = TSSStringEntry.from_buffer(mm.read(length))
            string_entries.append(new_entry)

            last_max: int = stop_index
            stop_index = mm.find(stop, last_max + 4, header.code_length)

        out = open(dump_file, "w")
        for string in string_entries:
            out.write(f"{string.string_id}:")
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

            out.write("\n")

        out.close()

        mm.close()
        f.close()

    end_time: float = time.time()
    print("Parsing and Dumping Time Taken:", end_time - start_time, "seconds")

    ids = [entry.string_id for entry in string_entries]
    print(f"Highest ID: {max(*ids)}")


if __name__ == "__main__":
    parse_tss()