import enum
import json
import csv
import os

class Characters(enum.Enum):
    YURI = 1
    ESTELLE = 2
    KAROL = 4
    RITA = 8
    RAVEN = 16
    JUDITH = 32
    REPEDE = 64
    FLYNN = 128
    PATTY = 256

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

    field_names: list[str] = ["name_string_key", "id", "tp_cost", "cast_time",
                              "learn_condition1", "learn_parameter1", "unknown3",
                              "learn_condition2", "learn_parameter2", "unknown4",
                              "learn_condition3", "learn_parameter3", "unknown5",
                              "learn_condition4", "learn_parameter4", "unknown6",
                              "learn_condition5", "learn_parameter5", "unknown7",
                              "learn_condition6", "learn_parameter6", "unknown8",
                              "evolve_base",
                              "evolve_condition1", "evolve_parameter1",
                              "evolve_condition2", "evolve_parameter2",
                              "evolve_condition3", "evolve_parameter3",
                              "evolve_condition4", "evolve_parameter4",
                              "fatal_strike_type"]

    artes_formatted: list = []
    learnable_valid: list = []
    randomizer_valid: list[dict] = []

    # artes_queried: list = []

    for artes in data:
        entry: dict = {field : artes[field] for field in field_names}

        artes_formatted.append([*entry.values()])
        # artes_queried.append([artes['id'], artes_ids[(artes['id'])], artes['arte_type']])

        # Arte Type 12, 14 and 15 refers to Fatal Strikes, Mystic Artes and Skill Artes respectively
        if artes['arte_type'] not in [12, 14, 15] and any(0 < chara < 10 for chara in artes['character_ids']):
            learnable_valid.append([artes['id'], artes['character_ids'][0]])
            # learnable_valid.append([artes['id'], artes_ids[(artes['id'])]])

            if artes['tp_cost']:
                randomizer_valid.append(entry)
                # randomizer_valid.append([artes['id'], artes_ids[(artes['id'])]])

    output: str = os.path.join("..", "artifacts", "artes.csv")
    with open(output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(field_names)
        writer.writerows(artes_formatted)

        f.close()

    output_randomizer: str = os.path.join("..", "artifacts", "artes_api.json")
    with open(output_randomizer, "w+") as f:
        json.dump(randomizer_valid, f, indent=4)

        f.flush()
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

    fields: list[str] = ["name_string_key", "id", "sp_cost", "lp_cost", "symbol", "symbol_weight", "is_equippable"]

    data: dict = json.load(open(json_file))["skills"]

    skills_formatted: list = [{field : skill[field] for field in fields} for skill in data]
    output: str = os.path.join("..", "artifacts", "skills_api.json")
    with open(output, "w+") as f:
        json.dump(skills_formatted, f, indent=4)

        f.flush()
        f.close()

    # skills_formatted = [[skill[field] for field in fields] for skill in data]
    # output: str = os.path.join("..", "artifacts", "skills.csv")
    # with open(output, "w+") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["Name", "ID", "SP", "LP", "Symbol", "Symbol Weight"])
    #     writer.writerows(skills_formatted)
    #
    #     f.close()

def generate_items_table():
    json_file: str = os.path.join("..", "data", "item.json")
    assert os.path.isfile(json_file)

    fields: list[str] = ["id", "buy_price",
                         "skill1", "skill1_lp",
                         "skill2", "skill2_lp",
                         "skill3", "skill3_lp"]

    data: dict = json.load(open(json_file))["items"]
    items_formatted: list = [{field: item[field] for field in fields} for item in data ]

    items_input: dict = {
        'base': items_formatted,
        # 'custom': []
    }

    output: str = os.path.join("..", "artifacts", "items_api.json")
    with open(output, "w+") as f:
        json.dump(items_input, f, indent=4)

    # output: str = os.path.join("..", "artifacts", "weapons.csv")
    # with open(output, "w+") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["Name", "ID", "Price",
    #                      "Skill 1", "Skill 1 LP",
    #                      "Skill 2", "Skill 2 LP",
    #                      "Skill 3", "Skill 3 LP"])
    #     writer.writerows(items_formatted)
    #
    #     f.close()

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

def generate_character_equips_table():
    json_file: str = os.path.join("..", "builds", "manifests", "item.json")
    assert os.path.isfile(json_file)

    data: list[dict] = json.load(open(json_file))['items']

    char_per_skills: dict = {}
    skills_by_char: dict = {}
    for item in data:
        character_flags: int = item["character_usable"]
        if not character_flags: continue

        characters: list[str] = []
        skills: set[str] = {item[f'skill{_}'] for _ in range(1, 4)}
        for i, index in enumerate(Characters):
            if item['character_usable'] & index.value > 0:
                characters.append(index.value)

                skills_by_char.setdefault(i + 1, set()).update(skills)

        for skill in skills:
            char_per_skills.setdefault(skill, set()).update(set(c for c in characters))

    for skill, chars in char_per_skills.items():
        as_list: list[str] = [*char_per_skills[skill]]
        as_list.sort()
        char_per_skills[skill] = [Characters(index).name for index in as_list]

    per_skills_output: str = os.path.join("..", "artifacts", "chara_per_skills.csv")
    with open(per_skills_output, "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["Skills", "Characters"])
        writer.writerows([k, *v] for k, v in char_per_skills.items())

        f.flush()
        f.close()

    by_char_output: str = os.path.join("..", "artifacts", "skills_by_char.json")
    with open(by_char_output, "w+") as f:
        json.dump({char: [*skills] for char, skills in skills_by_char.items()}, f, indent=4)

        f.flush()
        f.close()

def generate_item_category_table():
    id_file: str = os.path.join("..", "artifacts", "items_id_table.csv")
    assert os.path.isfile(id_file)

    json_file: str = os.path.join("..", "builds", "manifests", "item.json")
    assert os.path.isfile(json_file)

    data: list[dict] = json.load(open(json_file))['items']

    items_per_category: dict = {}
    for item in data:
        items_per_category.setdefault(item['category'], []).append(item['id'])

        # id_to_name: dict = {int(data['ID']): strip_formatting(data['Name'])
        #                     for data in csv.DictReader(open(id_file))}

    # items_formatted = [[id_to_name[item['id']], item['id'], item['category']] for item in data]
    # output: str = os.path.join("..", "artifacts", "item_categories.csv")
    # with open(output, "w+") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["Name", "ID", "Category"])
    #     writer.writerows(items_formatted)
    #
    #     f.close()

def generate_shop_items_table(generate_csv: bool = True):
    json_file: str = os.path.join("..", "builds", "manifests", "shop_items.json")
    assert os.path.isfile(json_file)

    id_file: str = os.path.join("..", "artifacts", "items_id_table.csv")
    assert os.path.isfile(id_file)

    fields: list[str] = ["shop_id", "item_id"]

    id_to_name: dict = {int(data['ID']): strip_formatting(data['Name'])
                        for data in csv.DictReader(open(id_file))}

    data: list[dict] = json.load(open(json_file))

    items_cleaned: list = []
    items_formatted: list = []
    by_shop_id: dict[int, list[int]] = {}
    by_shop_id_formatted: dict[int, list[str]] = {}
    for item in data:
        item_name = id_to_name[item['item_id']] if item['item_id'] in id_to_name else item['item_id']

        items_cleaned.append({field : item[field] for field in fields})
        items_formatted.append([item['shop_id'], item_name])
        by_shop_id.setdefault(item['shop_id'], []).append(item['item_id'])
        by_shop_id_formatted.setdefault(item['shop_id'], []).append(item_name)

    if generate_csv:
        output: str = os.path.join("..", "artifacts", "shop_items.csv")
        with open(output, "w+") as f:
            writer = csv.writer(f)
            writer.writerow(["Shop", "Item"])
            writer.writerows(items_formatted)

            f.close()

        output: str = os.path.join("..", "artifacts", "items_by_shop.csv")
        with open(output, "w+") as f:
            writer = csv.writer(f)
            writer.writerow(["Shop", "Items"])
            writer.writerows([[shop, *items] for shop, items in by_shop_id_formatted.items()])

            f.close()

    output: str = os.path.join("..", "artifacts", "shop_items.json")
    with open(output, "w+") as f:
        json.dump(items_cleaned, f, indent=4)

        f.close()

    output: str = os.path.join("..", "artifacts", "items_by_shop.json")
    with open(output, "w+") as f:
        json.dump(by_shop_id, f, indent=4)

        f.close()

    for item in sorted(by_shop_id.keys()):
        print(item)

class DataTableGenerator:
    strings: dict = {}

    def __init__(self):
        strings_json: str = os.path.join("..", "artifacts", "strings.json")
        assert os.path.isfile(strings_json)

        self.strings = json.load(open(strings_json), object_hook=keys_to_int)

    def get_name(self, index: int) -> str:
        return strip_formatting(self.strings[index]) if index in self.strings else f"String {index}"


if __name__ == "__main__":
    generate_shop_items_table()