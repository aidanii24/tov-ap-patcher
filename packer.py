import subprocess
import hashlib
import json
import sys
import os


# Configuraiton Files
dependencies: str = "config.json"

# Dependencies Default Directories
dependency_vesperia = "vesperia"
dependency_dotnet = "dotnet"
dependency_hyouta = "hyouta"
dependencies_comptoe = "comptoe"

default_vesperia: str = os.path.join("steam", "steamapps", "common", "Tales of Vesperia Definitive Edition")
default_dotnet: str = "dotnet"
default_hyouta: str = os.path.join("HyoutaToolsCLI", "HyoutaToolsCLI.dll")
default_comptoe: str = "comptoe"

# Checksums
sha256_vesperia: str = "ee3212432d063c3551f8d5eb9c8dde6d55a22240912ae9ea3411b3808bfb3827"

class VesperiaPacker:
    vesperia: str = default_vesperia
    dotnet: str = default_dotnet
    hyouta: str = default_hyouta
    comptoe: str = default_comptoe

    def __init__(self):
        if not os.path.isfile(dependencies):
            VesperiaPacker.generate_config()
            print("> Please provide the paths to the dependencies in the config.json file, then try again.")
            exit(0)
        else:
            with open(dependencies, 'r+') as file:
                data = json.load(file)

                if dependency_vesperia in data and data[dependency_vesperia]:
                    self.vesperia = data[dependency_vesperia]

                if dependency_dotnet in data and data[dependency_dotnet]:
                    self.dotnet = data[dependency_dotnet]

                if dependency_hyouta in data and data[dependency_hyouta]:
                    self.hyouta = data[dependency_hyouta]

                if dependencies_comptoe in data and data[dependencies_comptoe]:
                    self.comptoe = data[dependencies_comptoe]

                file.close()

        self.check_dependencies()

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
            with open(os.path.join(self.vesperia, "TOV_DE.exe"), "rb") as file:
                as_bytes = file.read()
                hash = hashlib.sha256(as_bytes).hexdigest()

                assert hash == sha256_vesperia
                file.close()
        except AssertionError:
            err = True
            print("Wrong Dependency: The provided game executable did not meet the expected supported version. "
                  "Please update the game then try again.")
        except FileNotFoundError:
            err = True
            print("Missing Dependency: The game was not found in the provided path.")

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
            subprocess.check_output([self.dotnet, self.hyouta])
        except FileNotFoundError:
            err = True
            print("Missing Dependency: HyoutaToolsCLI was not found.")
        except subprocess.CalledProcessError as c:
            if c.returncode != 255:
                err = True
                print("Runtime Error: There was a problem calling HyoutaToolsCLI. "
                      "Try re-installing the application then try again.")

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


if __name__ == "__main__":
    packer = VesperiaPacker()
    packer.check_dependencies()