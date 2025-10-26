import json
import csv
import os


def strip_formatting(string: str) -> str:
    return string.replace("\n", "").replace("\t", "").replace("\r", "")

def keys_to_int(x):
    return {int(k): v for k, v in x.items()}

def generate_strings_table():
    strings_json: str = os.path.join("..", "artifacts", "strings.json")
    assert os.path.isfile(strings_json)

    strings: dict = json.load(open(strings_json), object_hook=keys_to_int)
    output: str = os.path.join("..", "artifacts", "strings.csv")
    with open(output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "String"])
        writer.writerows([[index, strip_formatting(string)] for index, string in strings.items()])

        f.close()

def generate_skills_table():
    json_file: str = os.path.join("..", "builds", "manifests", "skills.json")
    assert os.path.isfile(json_file)

    skills_data: dict = json.load(open(json_file))["skills"]
    skills_formatted = [[skill['name_string_key'], skill['id'], skill['sp_cost'], skill['lp_cost'],
                         skill['symbol'], skill['symbol_weight']]
                        for skill in skills_data]

    output: str = os.path.join("..", "artifacts", "skills.csv")
    with open(output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "ID", "SP", "LP", "Symbol", "Symbol Weight"])
        writer.writerows(skills_formatted)

        f.close()

def generate_search_points_table():
    json_file: str = os.path.join("..", "builds", "manifests", "search_points.json")
    assert os.path.isfile(json_file)

    data: dict = json.load(open(json_file))
    definitions: list = data["definitions"]

    output: str = os.path.join("..", "artifacts", "search_points.csv")
    with open(output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "Scenario Begin", "Scenario End", "X Coords", "Y Coords", "Z Coords"])
        writer.writerows([[definition['index'], definition['scenario_begin'], definition['scenario_end'],
                           definition['x_coord'], definition['y_coord'], definition['z_coord']]
                          for definition in definitions])

class DataTableGenerator:
    strings: dict = {}

    def __init__(self):
        strings_json: str = os.path.join("..", "artifacts", "strings.json")
        assert os.path.isfile(strings_json)

        self.strings = json.load(open(strings_json), object_hook=keys_to_int)

    def get_name(self, index: int) -> str:
        return strip_formatting(self.strings[index]) if index in self.strings else f"String {index}"


if __name__ == "__main__":
    generate_skills_table()