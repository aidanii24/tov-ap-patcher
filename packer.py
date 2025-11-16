import subprocess
import hashlib
import shutil
import sys
import os

from vesperia_types import *


# Configuraiton Files
dependencies: str = "config.json"

# Dependencies Default Directories
dependency_vesperia = "vesperia"
dependency_dotnet = "dotnet"
dependency_hyouta = "hyouta"
dependencies_comptoe = "comptoe"

default_vesperia: str = os.path.join("steam", "steamapps", "common", "Tales of Vesperia Definitive Edition")
default_backup: str = os.path.join(default_vesperia, "Data64", "_backup")
default_dotnet: str = "dotnet"
default_hyouta: str = os.path.join("HyoutaToolsCLI", "HyoutaToolsCLI.dll")
default_comptoe: str = "comptoe"

# Vesperia Files directories
tov_executable = "TOV_DE.exe"
tov_btl = os.path.join("Data64", "btl.svo")
tov_item = os.path.join("Data64", "item.svo")
tov_npc = os.path.join("Data64", "npc.svo")
tov_ui = os.path.join("Data64", "UI.svo")
tov_scenario = os.path.join("Data64", "language", "scenario_ENG.dat")

# Checksums
checksums: dict[str, str] = {
    "TOV_DE.exe": "ee3212432d063c3551f8d5eb9c8dde6d55a22240912ae9ea3411b3808bfb3827",
    "btl.svo": "bab8c0497665bd5a46f2ffabba5f4d2acc9fcdf0e4e0dd50c1b8199d3f6d7111",
    "item.svo": "d86e4e3d7df4d60c9c752f999e916d495c77b2ae321c18fe281a51464a5d4d25"
}


class Hyouta:
    """Wrapper instance for HyoutaToolsCLI Commands"""
    dotnet: str = default_dotnet
    path: str = default_hyouta

    def __init__(self, dotnet:str, path: str):
        self.dotnet = dotnet
        self.path = path

    def check_dependencies(self) -> bool:
        err: bool = False

        try:
            version = subprocess.check_output([self.dotnet, "--version"])

            assert version.decode('utf-8')[0] == "6"
        except AssertionError:
            err = True
            print("Wrong Dependency: The installed .NET is incompatible with HyoutaToolsCLI. Please install .NET 6.0.")
        except FileNotFoundError:
            err = True
            print("Missing Dependency: .NET 6.0 is not installed, or is not present in the provided path.")
        except subprocess.CalledProcessError as e:
            err = True
            if e.returncode != 255:
                print("Runtime Error: There was a problem calling .NET 6.0. "
                      "Try re-installing the application then try again.")

        try:
            subprocess.check_output([self.dotnet, self.path])
        except FileNotFoundError:
            err = True
            print("Missing Dependency: HyoutaToolsCLI was not found.")
        except subprocess.CalledProcessError as c:
            if c.returncode != 255:
                err = True
                print("Runtime Error: There was a problem calling HyoutaToolsCLI. "
                      "Try re-installing the application then try again.")

        return err

    def extract_svo(self, file: str, out: str="", manifest:str = ""):
        command: list[str] = [self.dotnet, self.path, "ToVfps4e", file]
        if out:
            command.append(out)

        if manifest:
            command.extend(["-j", manifest + ".json"])

        subprocess.check_output(command)

    def decompress_tlzc(self, file: str, out: str=""):
        command: list[str] = [self.dotnet, self.path, "tlzc", "-d", file, out]

        subprocess.check_output(command)

    def extract_scenario(self, file: str, dir_out: str=""):
        command: list[str] = [self.dotnet, self.path, "Tales.Vesperia.Scenario.Extract", file, dir_out]

        subprocess.check_output(command)

    def pack_svo(self, manifest_file: str, out: str=""):
        command: list[str] = [self.dotnet, self.path, "ToVfps4p", manifest_file]
        if out:
            command.append(out)

        subprocess.check_output(command)

    def compress_tlzc(self, file: str, out: str=""):
        command: list[str] = [self.dotnet, self.path, "tlzc", "-c", file, out]

        subprocess.check_output(command)

    def pack_scenario(self, file: str, dir_out: str=""):
        command: list[str] = [self.dotnet, self.path, "Tales.Vesperia.Scenario.Pack", file, dir_out]

        subprocess.check_output(command)

class VesperiaPacker:
    """Handler Instance for Extraction, Packing, Compressing and Decompressing files from the game."""
    vesperia_dir: str = default_vesperia
    backup_dir: str = default_backup
    comptoe: str = default_comptoe
    hyouta: Hyouta

    build_dir: str = os.path.join(os.getcwd(), "builds")
    manifest_dir: str = os.path.join(build_dir, "manifests")
    output_dir: str = os.path.join(os.getcwd(), "output")

    apply_immediately: bool = False

    def __init__(self, patch_id: str = "singleton", apply_immediately: bool = False):
        if not os.path.isfile(dependencies):
            VesperiaPacker.generate_config()
            print("> Please provide the paths to the dependencies in the config.json file, then try again.")
            exit(0)
        else:
            with open(dependencies, 'r+') as file:
                data = json.load(file)

                if dependency_vesperia in data and data[dependency_vesperia]:
                    self.vesperia_dir = data[dependency_vesperia]
                    self.backup_dir = os.path.join(self.vesperia_dir, "Data64", "_backup")

                if dependency_dotnet in data and data[dependency_dotnet]:
                    dotnet_dir = data[dependency_dotnet]

                if dependency_hyouta in data and data[dependency_hyouta]:
                    hyouta_dir = data[dependency_hyouta]

                if dependencies_comptoe in data and data[dependencies_comptoe]:
                    self.comptoe = data[dependencies_comptoe]

                if hyouta_dir and dotnet_dir:
                    self.hyouta = Hyouta(dotnet_dir, hyouta_dir)

                file.close()

        self.check_dependencies()

        if patch_id == "singleton":
            return

        if not os.path.isdir(self.build_dir):
            os.makedirs(self.build_dir)

        build_path: str = os.path.join(self.build_dir, patch_id)
        if not os.path.isdir(build_path):
            os.makedirs(build_path)

        self.build_dir = build_path
        self.manifest_dir = os.path.join(build_path, "manifests")

        if not os.path.isdir(self.manifest_dir):
            os.makedirs(self.manifest_dir)

        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        self.output_dir = os.path.join(self.output_dir, patch_id)

        self.apply_immediately = apply_immediately

    @classmethod
    def generate_config(cls):
        vesperia: str = default_vesperia
        if sys.platform == "linux" or sys.platform == "linux2":
            vesperia = os.path.join(os.path.expanduser("~"), ".steam", default_vesperia)
        elif sys.platform == "win32":
            vesperia = os.path.join("C:", "Program Files (x86)", default_vesperia)

        config = {
            dependency_vesperia : vesperia,
            dependency_dotnet : default_dotnet,
            dependency_hyouta : default_hyouta,
            dependencies_comptoe: default_comptoe,
        }

        with open(dependencies, "x+") as file:
            json.dump(config, file, indent=4)

            file.close()

    def check_dependencies(self):
        err: bool = False

        try:
            with open(os.path.join(self.vesperia_dir, "TOV_DE.exe"), "rb") as file:
                as_bytes = file.read()
                exec_hash = hashlib.sha256(as_bytes).hexdigest()

                assert exec_hash == checksums["TOV_DE.exe"]
                file.close()
        except AssertionError:
            err = True
            print("Wrong Dependency: The provided game executable did not meet the expected supported version."
                  "Please update the game then try again.")
        except FileNotFoundError:
            err = True
            print("Missing Dependency: The game was not found in the provided path.")

        err = err and self.hyouta.check_dependencies()

        try:
            subprocess.check_output([self.comptoe])
        except FileNotFoundError:
            err = True
            print("Missing Dependency: comptoe was not found.")
        except subprocess.CalledProcessError as c:
            if c.returncode != 255:
                err = True
                print("Runtime Error: There was a problem calling comptoe."
                      "Try re-installing the application then try again.")

        if err:
            exit(1)

    @staticmethod
    def verify_vesperia_file(filepath: str) -> bool:
        basename = os.path.basename(filepath)

        try:
            with open(filepath, "rb") as file:
                as_bytes = file.read()
                file_hash = hashlib.sha256(as_bytes).hexdigest()

                assert file_hash == checksums[basename]

                file.close()
        except AssertionError:
            print(f"Invalid File: {basename} may have already been patched, modified, or may be corrupted.")
            return False

        return True

    def check_vesperia_file(self, original_path: str) -> str:
        basename: str = os.path.basename(original_path)
        backup_path: str = os.path.join(self.backup_dir, basename)

        if os.path.isfile(backup_path) and self.verify_vesperia_file(backup_path):
            if os.path.isfile(original_path):
                os.remove(original_path)

            return backup_path
        elif os.path.isfile(original_path):
            assert self.verify_vesperia_file(original_path), \
                f"Invalid File: {basename} may have already been patched, modified, or may be corrupted."

            if not os.path.isdir(self.backup_dir):
                os.makedirs(self.backup_dir)

            shutil.copy2(original_path, backup_path)

            if self.apply_immediately:
                os.remove(original_path)

            return backup_path
        else:
            raise AssertionError(f"{basename} could not be found in the game directory.")

    def ensure_output_directory(self):
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

    def comptoe_decompress(self, file: str, out: str = ""):
        command: list[str] = [self.comptoe, "-d", file]

        if out:
            command.append(out)

        subprocess.check_output(command)

    def comptoe_compress(self, file: str, out: str = ""):
        command: list[str] = [self.comptoe, "-c", file]

        if out:
            command.append(out)

        subprocess.check_output(command)

    def set_build_dir(self, build_dir: str):
        self.build_dir = build_dir

    def unpack_btl(self):
        path: str = self.check_vesperia_file(os.path.join(self.vesperia_dir, tov_btl))

        base_build: str = os.path.join(self.build_dir, "btl")
        if not os.path.isfile(path):
            os.mkdir(base_build)

        self.hyouta.extract_svo(path, base_build)

        pack_build: str = os.path.join(self.build_dir, "BTL_PACK")
        self.hyouta.extract_svo(os.path.join(base_build, "BTL_PACK.DAT"), pack_build,
                                os.path.join(self.manifest_dir, "BTL_PACK.DAT"))

    def extract_artes(self):
        path: str = os.path.join(self.build_dir, "BTL_PACK", "0004")
        assert os.path.isfile(path)

        self.hyouta.extract_svo(path, manifest=os.path.join(self.manifest_dir, "0004"))

    def extract_skills(self):
        path: str = os.path.join(self.build_dir, "BTL_PACK", "0010")
        assert os.path.isfile(path)

        self.hyouta.extract_svo(path, manifest=os.path.join(self.manifest_dir, "0010"))

    def unpack_item(self):
        path: str = self.check_vesperia_file(os.path.join(self.vesperia_dir, tov_item))
        assert os.path.isfile(path)

        base_build: str = os.path.join(self.build_dir, "item")
        if not os.path.isdir(base_build):
            os.makedirs(base_build)

        self.hyouta.extract_svo(path, base_build)

    def unpack_npc(self):
        path: str = os.path.join(self.vesperia_dir, tov_npc)
        base_build: str = os.path.join(self.build_dir, "npc", "npc")
        assert os.path.isfile(path)

        self.hyouta.extract_svo(path, base_build)

    def extract_map(self, map_data: str):
        data_name: str = map_data if not map_data.endswith(".DAT") else map_data.replace(".DAT", "")
        data_file: str = data_name + ".DAT"

        base: str = os.path.join(self.build_dir, "npc")
        assert os.path.isdir(base)

        path: str = os.path.join(base, "npc", data_file)
        assert os.path.isfile(path)

        work_dir: str = os.path.join(base, data_name)
        if not os.path.isdir(work_dir): os.mkdir(work_dir)

        decompress_name: str = f"{data_name}.tlzc"
        field_decompress: str = os.path.join(work_dir, decompress_name)
        self.hyouta.decompress_tlzc(path, field_decompress)
        self.hyouta.extract_svo(field_decompress, "", os.path.join(self.manifest_dir, decompress_name))

        return field_decompress + ".ext"

    def decompress_data(self, file: str):
        assert os.path.isfile(file)

        out: str = file + ".tlzc"
        self.hyouta.decompress_tlzc(file, out)

    def unpack_ui(self):
        path: str = os.path.join(self.vesperia_dir, tov_ui)
        assert os.path.isfile(path)

        work_dir: str = os.path.join(self.build_dir, "ui")
        if not os.path.isdir(work_dir): os.mkdir(work_dir)

        self.hyouta.extract_svo(path, work_dir)

    def extract_scenario(self):
        path: str = os.path.join(self.vesperia_dir, tov_scenario)
        assert os.path.isfile(path)

        work_dir: str = os.path.join(self.build_dir, "scenario")
        if not os.path.isdir(work_dir): os.mkdir(work_dir)

        extract_dir: str = os.path.join(work_dir, "ENG")
        if not os.path.isdir(extract_dir): os.mkdir(extract_dir)

        self.hyouta.extract_scenario(path, extract_dir)

    def decompress_scenario(self, file: str):
        assert file

        work_dir: str = os.path.join(self.build_dir, "scenario")
        if not os.path.isdir(work_dir): os.mkdir(work_dir)

        extract_dir: str = os.path.join(work_dir, "ENG")
        if not os.path.isdir(extract_dir): os.mkdir(extract_dir)

        target: str = os.path.join(extract_dir, file)
        assert os.path.isfile(target)

        decompress_dir: str = os.path.join(work_dir, file)
        if not os.path.isdir(decompress_dir): os.mkdir(decompress_dir)

        self.comptoe_decompress(target, os.path.join(decompress_dir, file + ".dec"))

    def pack_btl(self):
        path: str = os.path.join(self.manifest_dir, "BTL_PACK.DAT.json")
        assert os.path.isfile(path)

        self.ensure_output_directory()
        output_dir: str = os.path.join(self.output_dir, "Data64", "btl")

        shutil.copytree(os.path.join(self.build_dir, "btl"), output_dir, dirs_exist_ok=True)
        self.hyouta.pack_svo(path, os.path.join(output_dir, "BTL_PACK.DAT"))

    def pack_artes(self):
        path: str = os.path.join(self.manifest_dir, "0004.json")
        assert os.path.isfile(path)

        self.hyouta.pack_svo(path, os.path.join(self.build_dir, "BTL_PACK", "0004"))

    def pack_skills(self):
        path: str = os.path.join(self.manifest_dir, "0010.json")
        assert os.path.isfile(path)

        self.hyouta.pack_svo(path, os.path.join(self.build_dir, "BTL_PACK", "0010"))

    def pack_map(self, map_data: str):
        base_dir: str = os.path.join(self.build_dir, "npc")
        assert os.path.isdir(base_dir)

        data_name: str = map_data if not map_data.endswith(".DAT") else map_data.replace(".DAT", "")
        work_dir: str = os.path.join(base_dir, data_name)
        extract_dir: str = os.path.join(work_dir, data_name + ".tlzc.ext")
        assert os.path.isdir(extract_dir)

        manifest: str = os.path.join(self.manifest_dir, data_name + ".tlzc.json")
        assert os.path.isfile(manifest)

        map_decompressed: str = os.path.join(work_dir, data_name + ".tlzc")
        self.hyouta.pack_svo(manifest, os.path.join(work_dir, data_name + ".tlzc"))

        data_file: str = os.path.join(base_dir, "npc", data_name + ".DAT")
        self.hyouta.compress_tlzc(map_decompressed, data_file)

    def compress_data(self, file: str):
        assert os.path.isfile(file)
        if file.endswith(".tlzc"):
            out: str = file.replace(".tlzc", "")
        else:
            out: str = file
            file = file + ".tlzc"

        self.hyouta.compress_tlzc(file, out)

    def pack_scenario(self):
        path: str = os.path.join(self.build_dir, "scenario")
        main: str = os.path.join(path, "ENG")
        assert os.path.isdir(path)
        assert os.path.isdir(main)

        dirs: list[str] = [F for F in os.listdir(path)
                           if os.path.isdir(os.path.join(path, F))
                           and F.isdigit()]

        for directory in dirs:
            file: str = os.path.join(path, directory, f"{directory}.dec")
            out: str = os.path.join(main, directory)
            if not os.path.isfile(file): continue

            self.comptoe_compress(file, out)

        packed: str = os.path.join(path, "scenario_ENG.dat")
        self.hyouta.pack_scenario(main, packed)

    def copy_to_output(self, dir_name: str, ):
        target: str = os.path.join(self.build_dir, dir_name)
        assert os.path.isdir(target), f"Cannot find {dir_name} in the build directory for the patch."

        self.ensure_output_directory()

        shutil.copytree(target, os.path.join(self.output_dir, "Data64", dir_name), dirs_exist_ok=True)

    def apply_patch(self, start_time: float):
        if not self.apply_immediately:
            return

        print("> Applying Patch...")

        shutil.copytree(self.output_dir, self.vesperia_dir, dirs_exist_ok=True)

    def clean_game(self, quiet: bool = True):
        detected_patches: list[str] = []

        if os.path.isdir(os.path.join(self.vesperia_dir, "Data64", "btl")):
            detected_patches.append(os.path.join(self.vesperia_dir, "Data64", "btl"))

        if os.path.isdir(os.path.join(self.vesperia_dir, "Data64", "item")):
            detected_patches.append(os.path.join(self.vesperia_dir, "Data64", "item"))

        if detected_patches:
            if not quiet: print("> Removing active patches...")
            for patches in detected_patches:
                shutil.rmtree(patches)

    def restore_backup(self):
        if not os.path.isdir(self.backup_dir):
            print("> There is no backup to restore.")
            return

        self.clean_game()

        print("> Restoring Backup...")
        shutil.copytree(self.backup_dir, os.path.join(self.vesperia_dir, "Data64"), dirs_exist_ok=True)

        print("[-/-] Backup Restored")