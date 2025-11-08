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

    artes_id_table: str = os.path.join('..', 'artifacts', 'artes_id_table.csv')
    assert os.path.isfile(artes_id_table), f'{artes_id_table} does not exist'

    # artes_ids = {int(data['ID']): strip_formatting(data['Name'])
    #              for data in csv.DictReader(open(artes_id_table))}

    data: list[dict] = json.load(open(json_file))["artes"]

    artes_formatted: list = []
    learnable_valid: list = []
    randomizer_valid: list = []

    # artes_queried: list = []

    for artes in data:
        entry: list = [artes['name_string_key'], artes['id'], artes['tp_cost'], artes['cast_time'],
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

        artes_formatted.append(entry)
        # artes_queried.append([artes['id'], artes_ids[(artes['id'])], artes['arte_type']])

        # Arte Type 12, 14 and 15 refers to Fatal Strikes, Mystic Artes and Skill Artes respectively
        if artes['arte_type'] not in [12, 14, 15] and any(0 < chara < 10 for chara in artes['character_ids']):
            learnable_valid.append([artes['id'], artes['character_ids'][0]])
            # learnable_valid.append([artes['id'], artes_ids[(artes['id'])]])

            if artes['tp_cost']:
                randomizer_valid.append(entry)
                # randomizer_valid.append([artes['id'], artes_ids[(artes['id'])]])


    field_names: list[str] = ["Name", "ID", "TP", "Cast Time",
                         "Learn Condition 1", "Learn Parameter 1", "Learn Meta 1",
                         "Learn Condition 2", "Learn Parameter 2", "Learn Meta 2",
                         "Learn Condition 3", "Learn Parameter 3", "Learn Meta 3",
                         "Learn Condition 4", "Learn Parameter 4", "Learn Meta 4",
                         "Learn Condition 5", "Learn Parameter 5", "Learn Meta 5",
                         "Learn Condition 6", "Learn Parameter 6", "Learn Meta 6",
                         "Evolution Base",
                         "Evolve Condition 1", "Evolve Parameter 1",
                         "Evolve Condition 2", "Evolve Parameter 2",
                         "Evolve Condition 3", "Evolve Parameter 3",
                         "Evolve Condition 4", "Evolve Parameter 4",
                         "Fatal Strike Type"]

    output: str = os.path.join("..", "artifacts", "artes.csv")
    with open(output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(field_names)
        writer.writerows(artes_formatted)

        f.close()

    output_randomizer: str = os.path.join("..", "artifacts", "artes_api.csv")
    with open(output_randomizer, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(field_names)
        writer.writerows(randomizer_valid)

        f.close()

    output_learnable: str = os.path.join("..", "artifacts", "artes_learnable.json")
    with open(output_learnable, "w+") as f:
        json.dump(learnable_valid, f, indent=4)

        f.flush()
        f.close()

    output_learnable: str = os.path.join("..", "artifacts", "artes_learnable.csv")
    with open(output_learnable, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Character IDs"])
        writer.writerows(learnable_valid)

        f.close()


    # output_randomizer: str = os.path.join("..", "artifacts", "artes_types.csv")
    # with open(output_randomizer, "w+") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["ID", "Name", "Type"])
    #     writer.writerows(artes_queried)
    #
    #     f.close()

def generate_skills_table():
    json_file: str = os.path.join("..", "builds", "manifests", "skills.json")
    assert os.path.isfile(json_file)

    data: dict = json.load(open(json_file))["skills"]
    skills_formatted = [[skill['name_string_key'], skill['id'], skill['sp_cost'], skill['lp_cost'],
                         skill['symbol'], skill['symbol_weight']]
                        for skill in data]

    output: str = os.path.join("..", "artifacts", "skills.csv")
    with open(output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "ID", "SP", "LP", "Symbol", "Symbol Weight"])
        writer.writerows(skills_formatted)

        f.close()

def generate_items_table():
    json_file: str = os.path.join("..", "builds", "manifests", "item.json")
    assert os.path.isfile(json_file)

    data: dict = json.load(open(json_file))["items"]
    items_formatted = [[item['name_string_key'], item['id'], item['buy_price'],
                         item['skill1'], item['skill1_lp'],
                        item['skill2'], item['skill2_lp'],
                        item['skill3'], item['skill3_lp'],]
                        for item in data]

    output: str = os.path.join("..", "artifacts", "items.csv")
    with open(output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "ID", "Price",
                         "Skill 1", "Skill 1 LP",
                         "Skill 2", "Skill 2 LP",
                         "Skill 3", "Skill 3 LP"])
        writer.writerows(items_formatted)

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