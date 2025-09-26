import ctypes
import mmap
import os

from vesperia_types import TSSHeader, TSSStringLeadEntry, TSSStringEntry

from debug import test_structure


def parse_tss():
    test_file: str = "../builds/strings/string_dic_ENG.so"
    stop: bytes = (0xFFFFFFFF).to_bytes(4, byteorder="little")

    header: TSSHeader = TSSHeader()
    header_size: int = ctypes.sizeof(TSSHeader)

    string_entries: list = []

    with open(test_file, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        header = TSSHeader.from_buffer_copy(mm.read(header_size))
        mm.seek(header.code_start)

        stop_index: int = header.code_length
        last_max: int = header.code_start

        while stop_index >= 0:
            stop_index = mm.find(stop, last_max + 1, mm.size())

            length: int = stop_index - last_max
            if length == 0x64:
                mm.seek(last_max)
                new_entry: TSSStringLeadEntry = TSSStringLeadEntry.from_buffer_copy(mm.read(length))
                string_entries.append(new_entry)
            elif length == 0x48:
                mm.seek(last_max)
                new_entry: TSSStringEntry = TSSStringEntry.from_buffer_copy(mm.read(length))
                string_entries.append(new_entry)

            last_max: int = stop_index
            mm.seek(last_max + 1)

        test = string_entries[0]
        start: int = test.pointer_eng + header.text_start
        mm.seek(start)
        end: int = mm.find("\x00".encode(), start)

        if end >= test.pointer_eng:
            print(hex(start), hex(end))
            result = mm.read(end - test.pointer_eng)
            print(len(result))
            print(result.decode())
        else: print("No String...")

        mm.close()

    print("Entries", len(string_entries))
    for entry in string_entries:
        print(entry.string_id, entry.pointer_jpn, entry.pointer_eng)


if __name__ == "__main__":
    parse_tss()