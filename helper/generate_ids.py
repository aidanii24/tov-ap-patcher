import json
import os


def generate_ids():
    artes_id_table_out: str = "artes_id_table.json"
    items_id_table_out: str = "items_id_table.json"

    manifest: str = "../builds/manifests"
    assert os.path.isdir(manifest)

    string_data: str = os.path.join(manifest, "strings.json")
    artes_data: str = os.path.join(manifest, "0004R.json")
    items_data: str = os.path.join(manifest, "item.json")

    assert os.path.isfile(string_data)
    assert os.path.isfile(artes_data)
    assert os.path.isfile(items_data)

    strings = json.load(open(string_data))
    artes = json.load(open(artes_data))["artes"]
    items = json.load(open(items_data))["items"]

    artes_id_table: dict = {arte["id"] : strings[f"{str(arte['name_string_key'])}"] for arte in artes
                            if str(arte['name_string_key']) in strings}

    items_id_table: dict = {item["id"] : strings[f"{str(item['name_string_key'])}"] for item in items
                            if str(item['name_string_key']) in strings}

    with open(artes_id_table_out, "w+") as f:
        json.dump(artes_id_table, f, indent=4)

    with open(items_id_table_out, "w+") as f:
        json.dump(items_id_table, f, indent=4)


if __name__ == "__main__":
    generate_ids()