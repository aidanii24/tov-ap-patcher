import datetime
import random
import math
import json
import csv
import os


def strip_formatting(string: str) -> str:
    return string.replace("\n", "").replace("\t", "").replace("\r", "")

class InputTemplate:
    artes_data_table: dict
    skills_data_table: dict

    arte_ids: dict
    skill_ids: dict

    artes_by_char: dict[int, list[int]]

    def __init__(self):
        artes_id_table: str = os.path.join('..', 'artifacts', 'artes_id_table.csv')
        skills_id_table: str = os.path.join('..', 'artifacts', 'skills_id_table.csv')
        artes_data_file: str = os.path.join('..', 'builds', 'manifests', '0004R.json')

        assert os.path.isfile(artes_data_file), f'{artes_data_file} does not exist'
        assert os.path.isfile(artes_id_table), f'{artes_id_table} does not exist'
        assert os.path.isfile(skills_id_table), f'{skills_id_table} does not exist'

        self.artes_ids = {int(data['ID']) : strip_formatting(data['Name'])
                          for data in csv.DictReader(open(artes_id_table))}
        self.skill_ids = {int(data['ID']) : strip_formatting(data['Name'])
                          for data in csv.DictReader(open(skills_id_table))}

        artes_data = json.load(open(artes_data_file))['artes']

        artes_data_table = {}
        artes_by_char = {}
        for arte in artes_data:
            artes_data_table[int(arte['id'])] = arte

            for char in arte['character_ids']:
                if arte['arte_type'] not in [12, 14, 15] and any(0 < chara < 10 for chara in arte['character_ids']):
                    artes_by_char.setdefault(char, []).append(arte['id'])

        self.artes_data_table = artes_data_table
        self.artes_by_char = artes_by_char

    def generate(self):
        output: str = os.path.join("..", "artifacts", "tovde.appatch")

        manifest: str = "../builds/manifests"
        assert os.path.isdir(manifest)

        artes_input: dict = self.randomize_artes_input([arte_entry for arte_entry in self.generate_artes_input()])

        patch_data: dict = {
            'version': '0.1',
            'seed': 'test',
            'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'artes': artes_input
        }

        with open(output, 'w+') as f:
            json.dump(patch_data, f, indent=4)

    @staticmethod
    def generate_artes_input():
        artes_data: str = os.path.join("..", "artifacts", "artes_api.csv")

        assert os.path.isfile(artes_data)

        return csv.DictReader(open(artes_data))

    def randomize_artes_input(self, patch):
        # Based on average amount of character artes with evolve conditions
        evolve_opportunities: list[int] = [0, 0.0258, 0.0041, 0.0005, 0.005]
        # Based on average amount of character artes with learn conditions
        learn_opportunities: list[int] = [0, 0.75, 0.042, 0.8, 0.077]
        learn_type_opportunities: list[list[int]] = [[0, 0], [0.35, 0.05], [0.005, 0.005], [0.75, 0.05], [0.5, 0.5]]

        def _randomize_evolve(target_arte, count):
            target_arte[f'evolve_condition{count}'] = 3
            target_arte[f'evolve_parameter{count}'] = random.choice([*self.skill_ids.keys()])

        def _randomize_learn(target_arte, arte_data, count):
            condition_pop: list[int] = [_ for _ in range(1 if count <= 1 else 2, 4)]
            condition_chances: list[float] = [0.6] if count <= 1 else []
            condition_chances.extend(learn_type_opportunities[count])

            meta: int = 0

            condition: int = random.choices(condition_pop, weights=condition_chances)[0]
            if condition == 1:
                cap_level: int = random.randint(5, 20)
                parameter = random.randint(1, cap_level)
            elif condition == 2:
                parameter: int = random.choice(self.artes_by_char[arte_data['character_ids'][0]])
                meta = math.ceil(10 * (random.randrange(10, 100) / 100))
            else:
                parameter: int = random.choice([*self.skill_ids.keys()])

            target_arte[f'learn_condition{count}'] = condition
            target_arte[f'learn_parameter{count}'] = parameter
            target_arte[f'unknown{count + 2}'] = meta

        new_input = {}

        r_candidates: int = 0
        r_tp: int = 0
        r_cast: int = 0
        r_fs: int = 0
        r_evolve: int = 0
        r_learn: int = 0
        for arte in patch:
            # Randomize Candidacy
            if random.random() <= 0.05:
                continue

            r_candidates += 1
            data = self.artes_data_table[int(arte['id'])]

            # Randomize TP Cost
            if random.random() <= 0.4:
                r_tp += 1
                arte['tp_cost'] = math.ceil(int(arte['tp_cost']) * (random.randrange(10, 200) * 0.01))

            # Randomize Cast Time
            if int(arte['cast_time']) > 0 and random.random() >= 0.3:
                r_cast += 1
                arte['cast_time'] = math.ceil(int(arte['cast_time']) * (random.randrange(10, 200) * 0.01))

            # Randomize FS Type
            if random.random() <= 0.75:
                r_fs += 1
                arte['fatal_strike_type'] = random.randrange(0, 3)

            # Randomize Evolution
            has_evolve: bool = False
            if random.random() <= 0.258:  # Average Total Artes over Altered Artes Count across all Party Members
                r_evolve += 1
                has_evolve = True
                arte['evolve_base'] = random.choice(self.artes_by_char[data['character_ids'][0]])

                continue_iter: bool = True
                iterations: int = 1
                while iterations < len(evolve_opportunities):
                    if continue_iter:
                        _randomize_evolve(arte, iterations)
                    else:
                        arte[f'evolve_condition{iterations}'] = 0
                        arte[f'evolve_parameter{iterations}'] = 0

                    if continue_iter and random.random() > evolve_opportunities[iterations]:
                        continue_iter = False

                    iterations += 1

                usage_req: int = random.choice([50, 100])
                if random.random() <= 0.4: math.ceil(usage_req * (random.randrange(10, 100) / 100))

                arte['learn_condition1'] = 2
                arte['learn_parameter1'] = int(arte['id'])
                arte['unknown3'] = usage_req

            # Randomize Learn Condition
            if random.random() > learn_opportunities[has_evolve + 1]:
                r_learn += 1
                continue_iter: bool = True
                iterations: int = 2 if has_evolve else 1
                while iterations < len(learn_opportunities):
                    if continue_iter: _randomize_learn(arte, data, iterations)
                    else:
                        arte[f"learn_condition{iterations}"] = 0
                        arte[f"learn_parameter{iterations}"] = 0
                        arte[f"unknown{iterations + 2}"] = 0

                    iterations += 1

            new_input[data['entry']] = arte

        print("--- Artes Results -------------------")
        print(f"Total Artes: {len(patch)}")

        print(f"Randomized: {r_candidates} ({r_candidates / len(patch) * 100:.2f}%)")
        print(f"Randomized TP: {r_tp} ({r_tp / r_candidates * 100:.2f}%)")
        print(f"Randomized Cast Time: {r_cast} ({r_cast / r_candidates * 100:.2f}%)")
        print(f"Randomized Fatal Strike Type: {r_fs} ({r_fs / r_candidates * 100:.2f}%)")
        print(f"Randomized Evolve Conditions: {r_evolve} ({r_evolve / r_candidates * 100:.2f}%)")
        print(f"Randomized Learn Conditions: {r_learn} ({r_learn / r_candidates * 100:.2f}%)")

        return new_input

if __name__ == "__main__":
    template = InputTemplate()
    template.generate()