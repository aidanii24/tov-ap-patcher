import utils
import json
import sys
import os

from packer import VesperiaPacker
from patcher import VesperiaPatcher

class VesperiaPatcherApp:
    packer: VesperiaPacker
    patcher: VesperiaPatcher

    patch_data: dict
    targets: list = []

    def __init__(self, patch_data: str, apply_immediately: bool = False):
        self.patch_data = json.load(open(patch_file), object_hook=utils.keys_to_int)
        identifier = f"{self.patch_data['player']}-{self.patch_data['created'].split(' ')[0]}-{self.patch_data['seed']}"

        self.packer = VesperiaPacker(identifier, apply_immediately)
        self.packer.check_dependencies()

        self.patcher = VesperiaPatcher(identifier)

    def begin(self):
        print("--- Tales of Vesperia: Definitive Edition Patcher -------------\n"
              f"\tPlayer: {self.patch_data['player']}\n"
              f"\tGeneration Date: {self.patch_data['created']}\n"
              f"\tSeed: {self.patch_data['seed']}\n")

        if 'artes' in self.patch_data or 'skills' in self.patch_data:
            self.patch_btl()

        if 'items' in self.patch_data:
            self.patch_items()

        self.packer.apply_patch()

    def patch_btl(self):
        self.packer.unpack_btl()

        if 'artes' in self.patch_data:
            print("> Patching Artes...")
            self.packer.extract_artes()
            self.patcher.patch_artes(self.patch_data['artes'])
            self.packer.pack_artes()

        if 'skills' in self.patch_data:
            print("> Patching Skills...")
            self.packer.extract_skills()
            self.patcher.patch_skills(self.patch_data['skills'])
            self.packer.pack_skills()

        self.packer.pack_btl()

    def patch_items(self):
        self.packer.unpack_item()
        self.patcher.patch_items(self.patch_data['items'])
        self.packer.copy_to_output('item')

if __name__ == '__main__':
    patch_file: str = ""
    apply: bool = False

    for arg in sys.argv[1:]:
        if arg in ("-h", "--help"):
            print(
                "Usage: main.py [ -a | --apply ] <patch file>"
                "\n\tPatcher for Tales of Vesperia: Definitive Edition on PC/Steam."
                "\n\n\tOptions:"
                "\n\t\t-a | --apply-immediately\tImmediately apply the patched files into the game directory, "
                "and move the affected original files to a backup directory (<game_directory>/Data64/_backup)."
                "\n\t\t-r | --restore-backup\t\tRestore Backups of the original unmodified files if present "
                "and remove all instances of patched files in the game directory"
            )
            exit(0)
        elif arg in ("-a", "--apply-immediately"):
            apply = True
        elif arg in ("-r", "--restore-backup"):
            packer = VesperiaPacker()
            packer.restore_backup()
            exit(0)
        elif os.path.isfile(arg) and arg.endswith(".appatch"):
            patch_file = arg

    assert patch_file != "", "No Valid Patch File was provided!"

    app = VesperiaPatcherApp(patch_file, apply)
    app.begin()