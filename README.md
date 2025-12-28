# ToV Randomizer Tools
A pair of tools for randomizing and patching aspects of Tales of Vesperia: Definitive Edition.

These tools were created in part for an eventual integration of the game into the 
[Archipelago](https://github.com/ArchipelagoMW/Archipelago) Randomizer framework, but can work
standalone with the bundled Basic Randomizer.
# Features
- Artes Randomization
  - TP
  - Cast Time (Magic only)
  - Learn Conditions
  - Evolve Conditions (for existing Altered artes only)
- Skills Randomization
  - Category
  - SP Cost
  - LP Cost
- Items Randomization
  - Price
  - Skills
- Shops Randomization
- Chests Randomization
- Search Point Randomization

# Use
ToVRandomizerTools comes with two main utilities: **ToVBasicRandomizer**, 
which is a naive randomizer that can create a patch file, and **ToVPatcher**, which can take that patch file
and applies them directly onto the game files.
## Dependencies
ToVBasicRandomizer works standalone, but ToVPatcher requires some external applications to apply patches. The patcher
must be directed to the locations of these applications by specifying them in the `config.json` file generated when
first running the patcher.
- [HyoutaTools](https://github.com/AdmiralCurtiss/HyoutaTools/actions)
  - [.NET 6.0 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/6.0)*
- [comptoe](https://github.com/lifebottle/comptoe/releases)

_* .NET 6.0 is only required when running HyoutaTools from source (using the .dll file directly instead of the binary)._
### From Source
It is also possible to use these tools from source, but will require further dependencies:
- Python (Current Build: Python3.13)
  - odfdo (optional; only used by ToVBasicRandomizer for creating spoiler files)

All source runtime dependencies are listed in the `requirements.txt` file, and can be easily installed with `pip`.
If using an IDE like Pycharm, it will automatically detect this file and will prompt to download the packages.
```commandline
pip install -r requirements.txt
```

## Procedure
ToVRandomizerTools are command line utilities. They must be invoked through the terminal.
### Generating a Patch
To generate a patch file, run `ToVBasicRandomizer`. This will create a `patches` folder with a `tovdepatch` inside of it.
```commandline
ToVBasicRandomizer
```
By default, ToVBasicRandomizer will randomize all supported aspects of the game. But the randomizer can also be specified 
to only randomize specific aspects of the game. 
For example, adding `artes` and `items` after will create a patch file that only randomizes those two aspects of the game.
```commandline
ToVBasicRandomizer artes items
```
Listed below are all the valid arguments that the randomizer can take to selectively randomize the game:
- `artes`
- `skills`
- `items`
- `shops`
- `chests`
- `search` (Search Points)

Alongside the patch, it may often be useful to have a spoiler to what was randomized and into what.
A spoiler sheet can be generated alongside the patch by adding the argument `-s` or `--spoil`.
```commandline
ToVBasicRandomizer -s
```
## Preparing the Patcher
Once a patch file is ready, it must be provided to ToVPatcher. Simply amend the location of the file after the
executable name to run it.
```commandline
ToVPatcher ./patches/sample.tovdepatch
```
If a `config.json` does not exist within the same directory, one will be created. The default configurations will 
attempt a basic guess on where the dependencies are and the patcher will attempt to use that. If the dependencies could
not be found with the default paths, the `config.json` can be configured to give the correct paths. The configuration 
file will ask for the paths of the following:
- Base directory of _Tales of Vesperia: Definitive Edition_
- HyoutaToolsCLI*
- comptoe
- .NET (if applicable)**

_* When using with .NET, HyoutaToolsCLI must direct to the .dll file. Direct to a compiled binary otherwise._\
_** .NET's path should be left as just `dotnet` unless it is installed into a custom directory. When using
the compiled binary for HyoutaToolsCLI, the dotnet entry must be removed._

The generated configuration will use common defaults, but is configurable if needed.
For Windows users, the backslash `\` used for paths must be escaped with another backslash, 
and so paths must look like `C:\\Program Files (x86)\\Steam`. A typical config.json will look something like this:
```json
{
  "vesperia": "C:\\Program Files (x86)\\steam\\steamapps\\common\\Tales of Vesperia Definitive Edition",
  "comptoe": "dependencies\\comptoe",
  "hyouta": "dependencies\\HyoutaToolsCLI\\HyoutaToolsCLI.dll",
  "dotnet": "dotnet"
}
```
## Applying the Patch
Once the configuration file is set, simply run the patcher again. 
As long as all dependencies have been properly provided, the patch will be successful, and the patched files will be
generated into the `output` folder.
```commandline
ToVPatcher ./patches/sample.tovdepatch
```
For certain aspects of the game, the patcher may take a long time to create the patched files.
The process can be sped up by specifying the number of threads desired for the patcher to use.
Add the argument `-t` or `--threads` and then the number of threads desired to be used.
For best results, specify the amount of cores available on your CPU. 
This option defaults to 4 if the argument is not used.
```commandline
ToVPatcher -t 12 ./patches/sample.tovdepatch
```
Once the patching process finishes, the files and folders in the output can now be safely used to replace their
original counterparts in the game directory. However, the patcher can also be specified to automatically apply
the patched files. Simply add the argument `-a` or `--apply-immediately`.
```commandline
ToVPatcher -a ./patches/sample.tovdepatch
```
During patching, the patcher will use the `builds` folder as space for extracting and decompressing files before
patching them, and will be left there after patching completes. If it is desired to remove these files after patching
finishes, add the `-c` or `--clean` argument.
```commandline
ToVPatcher -c ./patches/sample.tovdepatch
```
## Manual Application
When manually applying the patch, it is important to note that certain files are left unpacked as folders. Simply
remove the original files, and then place the folders in their place. Examples of files that are left unpacked when patched
include `btl.svo`, `item.svo` and `npc.svo`. Their patched folders will usually just be the same name without the
file extension.

For patched files that remain as files, simply replace them as normal.
## Re-applying Patches
The patcher can also re-apply patches and restore unaffected files by using the `-s` or `--set` argument.
It only needs to be provided the directory of the patched files desired.
```commandline
ToVPatcher -s ./builds/yuri-lowell-2019-01-11
```
## Restoring Originals
During patching, patched files are also automatically backed up inside
a `.backup` folder within the game directory, so any patches can be safely reverted by replacing the patched files 
and folder with the backed up original files. This process can also be automated by using the patcher.
Use the `-r` or `--restore-backup` argument to restore backups.
```commandline
ToVPatcher -r
```
# Build
ToVRandomizerTools is written in Python3 and bundled by pyinstaller. Python3 must first be installed, either system-wide
or when used with an IDE such as PyCharm.

Once Python is ready, source dependencies must be installed. All dependencies are listed in the `requirements.txt` file.
When using an IDE such as PyCharm, you will be prompted to download these. Otherwise, it can be easily installed with `pip.`
```commandline
pip install -r requirements.txt
```
A spec file is already present in the repository, which provides all the information pyinstaller needs to bundle the program.
Provide this spec file to pyinstaller to build the application. Note that pyinstaller is not a cross-compiler;
when building under Linux, it will only build a Linux executable, same on Windows.
```commandline
pyinstaller ToVRandomizerTools.spec
```
The binaries will be available in the generated `dist` directory upon successful build.
# Roadmap
- [ ] Event Rewards Patching
- [ ] Text Patching (string_dic_<lang>.so)
- [ ] Adding new Icons for in-game use
- [ ] Implement GUI
- [ ] Archipelago Support

# Acknowledgements
Thanks to @Sora3100 for providing me with the knowledge and resources to make this possible.

Thank you to @AdmiralCurtiss for the development of HyoutaTools, and the team behind @lifebottle
and the original work of @talestra for developing comptoe. These tools are necessary for the patcher to access
various files of the game, and this would not have been possible without them.