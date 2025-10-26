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

def generate_artes_table():
    json_file: str = os.path.join("..", "builds", "manifests", "0004R.json")
    assert os.path.isfile(json_file)

    artes_data: dict = json.load(open(json_file))["artes"]
    artes_formatted = [[artes['name_string_key'], artes['id'], artes['tp_cost'], artes['cast_time'],
                        artes['learn_condition1'], artes['learn_parameter1'], artes["unknown3"],
                        artes['learn_condition2'], artes['learn_parameter2'], artes["unknown4"],
                        artes['learn_condition3'], artes['learn_parameter3'], artes["unknown5"],
                        artes['learn_condition4'], artes['learn_parameter4'], artes["unknown6"],
                        artes['learn_condition5'], artes['learn_parameter5'], artes["unknown7"],
                        artes['learn_condition6'], artes['learn_parameter6'], artes["unknown8"],
                        artes['evolve_base'],
                        artes['evolve_condition1'], artes['evolve_parameter1'],
                        artes['evolve_condition2'], artes['evolve_parameter2'],
                        artes['evolve_condition3'], artes['evolve_parameter3'],
                        artes['evolve_condition4'], artes['evolve_parameter4'],
                        artes['fatal_strike_type']]
                        for artes in artes_data]

    output: str = os.path.join("..", "artifacts", "artes.csv")
    with open(output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "ID", "TP", "Cast Time",
                         "Learn Condition 1", "Learn Parameter 1", "Learn Meta 1",
                         "Learn Condition 2", "Learn Parameter 2", "Learn Meta 2",
                         "Learn Condition 3", "Learn Parameter 3", "Learn Meta 3",
                         "Learn Condition 4", "Learn Parameter 4", "Learn Meta 4",
                         "Learn Condition 5", "Learn Parameter 5", "Learn Meta 5",
                         "Learn Condition 6", "Learn Parameter 6", "Learn Meta 6",
                         "Evolution Base",
                         "Evolve Condition 1", "Evolve Paramter 1",
                         "Evolve Condition 2", "Evolve Paramter 2",
                         "Evolve Condition 3", "Evolve Paramter 3",
                         "Evolve Condition 4", "Evolve Paramter 4",
                         "Fatal Strike Type"])
        writer.writerows(artes_formatted)

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
    generate_artes_table()