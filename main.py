from packer import *
from patcher import *

class VesperiaPatcherApp:
    packer: VesperiaPacker
    patcher: VesperiaPatcher

    def __init__(self, patch_data: str, apply_immediately: bool = False):
        patch_data = json.load(open(patch_file))
        identifier = f"{patch_data['player']}-{patch_data['created'].split(' ')[0]}-{patch_data['seed']}"

        self.packer = VesperiaPacker(identifier, apply_immediately)
        self.packer.check_dependencies()

        self.patcher = VesperiaPatcher()

    def unpack_files(self):
        self.packer.unpack_btl()
        self.packer.extract_artes()

    def patch_artes(self):
        self.patcher.patch_artes()

    def pack_files(self):
        self.packer.pack_artes()
        self.packer.pack_btl()

        self.packer.apply_patch()

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
    app.unpack_files()
    app.patch_artes()
    app.pack_files()