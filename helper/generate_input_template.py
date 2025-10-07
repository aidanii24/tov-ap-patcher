import json
import os

artes_api: list = [""]

def generate_input_template():
    output: str = os.path.join("artifacts", "tovape.json")

    manifest: str = "../builds/manifests"
    assert os.path.isdir(manifest)

    string_data: str = os.path.join(manifest, "strings.json")
    artes_data: str = os.path.join(manifest, "0004R.json")
    skills_data: str = os.path.join(manifest, "skills.json")
    items_data: str = os.path.join(manifest, "item.json")

    assert os.path.isfile(string_data)
    assert os.path.isfile(artes_data)
    assert os.path.isfile(skills_data)
    assert os.path.isfile(items_data)

    strings = json.load(open(string_data))
    artes = json.load(open(artes_data))["artes"]
    skills = json.load(open(skills_data))["skills"]
    items = json.load(open(items_data))["items"]