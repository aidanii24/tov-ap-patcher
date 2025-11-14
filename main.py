from packer import *
from patcher import *

class VesperiaPatcherApp:
    packer: VesperiaPacker
    patcher: VesperiaPatcher

    def __init__(self, patch_data: str):
        patch_data = json.load(open(patch_file))
        identifier = f"{patch_data['player']}-{patch_data['created'].split(' ')[0]}-{patch_data['seed']}"

        self.packer = VesperiaPacker(identifier)
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


if __name__ == '__main__':
    patch_file: str = ""
    for arg in sys.argv[1:]:
        if os.path.isfile(arg) and arg.endswith(".appatch"):
            patch_file = arg
            break

    assert patch_file != "", "No Valid Patch File was provided!"

    app = VesperiaPatcherApp(patch_file)
    app.unpack_files()