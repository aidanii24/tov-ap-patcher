import time
import os

from packer import VesperiaPacker

packer: VesperiaPacker

def get_events():
    work_dir: str = os.path.join("../builds/scenario")
    assert os.path.isdir(work_dir)

    scenario: str = os.path.join(work_dir, "ENG")
    assert os.path.isdir(scenario)

    start: float = time.time()

    files = os.listdir(scenario)
    for file in files:
        if os.path.isdir(os.path.join(scenario, file)):
            continue

        packer.decompress_scenario(file)

    dirs = [d for d in os.listdir(scenario)
            if d.isdigit()]

    count: int = 0
    for d in dirs:
        print(d)
        assert os.path.isfile(os.path.join(work_dir, d, d + ".dec"))
        count += 1

    end: float = time.time()
    print(f"[Scenario Walking] Time Taken: {end - start}")
    print("Total Files: ", count)

if __name__ == "__main__":
    packer = VesperiaPacker()
    packer.check_dependencies()

    get_events()