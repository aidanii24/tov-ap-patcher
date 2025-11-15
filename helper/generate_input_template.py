import enum
import datetime
import random
import math
import uuid
import json
import csv
import os

class FatalStrikeType(enum.Enum):
    INDIGO = 0
    CRIMSON = 1
    VIRIDIAN = 2
    NONE = 3

    @classmethod
    def _missing_(cls, value):
        return cls.NONE

class Symbol(enum.Enum):
    FLECK = 0
    ROCKRA = 1
    STRHIM = 2
    LAYTOS = 3

    @classmethod
    def _missing_(cls, value):
        return cls.FLECK

def keys_to_int(x):
    return {int(k): v for k, v in x.items()}

def strip_formatting(string: str) -> str:
    return string.replace("\n", "").replace("\t", "").replace("\r", "")

class InputTemplate:
    artes_data_table: dict
    skills_data_table: dict

    arte_ids: dict
    skill_ids: dict

    artes_by_char: dict[int, list[int]]
    skills_by_char: dict[int, list[int]]

    seed: int
    random: random.Random

    patch_output: str = os.path.join(".", "artifacts", "tovde.appatch")
    report_output: str = os.path.join(".", "artifacts", "tovde-report.csv")

    def __init__(self, seed = random.randint(1, 10000)):
        self.seed = uuid.uuid1().int
        self.random = random.Random(seed)

        artes_id_table: str = os.path.join('.', 'artifacts', 'artes_id_table.csv')
        skills_id_table: str = os.path.join('.', 'artifacts', 'skills_id_table.csv')
        artes_data_file: str = os.path.join('.', 'data', 'artes.json')
        skills_data_file: str = os.path.join('.', 'data', 'skills.json')
        skills_char_data_file: str = os.path.join('.', 'artifacts', 'skills_by_char.json')

        assert os.path.isfile(artes_data_file), f'{artes_data_file} does not exist'
        assert os.path.isfile(skills_data_file), f'{skills_data_file} does not exist'
        assert os.path.isfile(skills_char_data_file), f'{skills_char_data_file} does not exist'
        assert os.path.isfile(artes_id_table), f'{artes_id_table} does not exist'
        assert os.path.isfile(skills_id_table), f'{skills_id_table} does not exist'

        self.artes_ids = {int(data['ID']) : strip_formatting(data['Name'])
                          for data in csv.DictReader(open(artes_id_table))}
        self.skill_ids = {int(data['ID']) : strip_formatting(data['Name'])
                          for data in csv.DictReader(open(skills_id_table))}

        artes_data = json.load(open(artes_data_file))['artes']
        skills_data = json.load(open(skills_data_file))['skills']

        artes_data_table = {}
        artes_by_char = {}
        for arte in artes_data:
            artes_data_table[int(arte['id'])] = arte

            for char in arte['character_ids']:
                if arte['arte_type'] not in [12, 14, 15] and any(0 < chara < 10 for chara in arte['character_ids'])\
                        and arte['tp_cost'] > 0:
                    artes_by_char.setdefault(char, []).append(arte['id'])

        self.artes_data_table = artes_data_table
        self.skills_data_table = {skill['id'] : skill for skill in skills_data}
        self.artes_by_char = artes_by_char

        self.skills_by_char = json.load(open(skills_char_data_file), object_hook=keys_to_int)

    def random_from_distribution(self, mu: float, sigma: float, range_min: float = -math.inf,
                                 range_max: float = math.inf):
        return int(math.ceil(min(max(self.random.gauss(mu, sigma), range_min), range_max)))


    def generate(self, *args):
        output: str = self.patch_output

        manifest: str = "./builds/manifests"
        assert os.path.isdir(manifest)

        patch_data: dict = {
            'version': '0.1',
            'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'seed': self.seed,
            'player': "test",
        }

        if os.path.isfile(self.report_output):
            os.remove(self.report_output)

        if not args or 'artes' in args:
            artes_input = self.randomize_artes_input([arte_entry for arte_entry in self.generate_artes_input()])
            patch_data['artes'] = artes_input
            self.generate_artes_report(artes_input)

        if not args or 'skills' in args:
            skills_input = self.randomize_skills_input(self.generate_skills_input())
            patch_data['skills'] = skills_input
            self.generate_skills_report(skills_input)

        with open(output, 'w+') as f:
            json.dump(patch_data, f, indent=4)

    @staticmethod
    def generate_artes_input():
        artes_data: str = os.path.join(".", "artifacts", "artes_api.json")
        assert os.path.isfile(artes_data)

        return json.load(open(artes_data))

    @staticmethod
    def generate_skills_input() -> dict:
        skills_data: str = os.path.join(".", "artifacts", "skills_api.json")
        assert os.path.isfile(skills_data)

        return json.load(open(skills_data))

    def generate_artes_report(self, patched_artes: dict):
        report_list: list = []
        for arte in [*patched_artes.values()]:
            learn_conditions: list = []
            # Parse Learn Conditions
            for _ in range(1, 7):
                condition_id = arte[f'learn_condition{_}']
                parameter_id = arte[f'learn_parameter{_}']
                meta_id = arte[f'unknown{_ + 2}']

                if condition_id == 0:
                    if parameter_id >= 300:
                        learn_conditions.extend(["Event", "", ""])
                    else:
                        learn_conditions.extend(["" for _ in range(3)])
                elif condition_id == 1:
                    learn_conditions.extend(["Level", parameter_id, ""])
                elif condition_id == 2:
                    learn_conditions.extend(["Arte Usage", self.artes_ids[parameter_id], f"x{meta_id}"])
                elif condition_id == 3:
                    learn_conditions.extend(["Equip Skill", self.skill_ids[parameter_id], ""])
                else:
                    learn_conditions.extend(["INVALID", "!", "!"])

            # Parse Evolve Conditions
            evolve_conditions: list = [self.artes_ids[arte['evolve_base']] if arte['evolve_base'] != 0
                                       else ""]
            for _ in range(1, 5):
                condition_id = arte[f'evolve_condition{_}']
                parameter_id = arte[f'evolve_parameter{_}']

                if condition_id == 0:
                    evolve_conditions.extend(["" for _ in range(2)])
                elif condition_id == 3:
                    evolve_conditions.extend(["Equip Skill", self.skill_ids[parameter_id]])
                else:
                    evolve_conditions.extend(["INVALID", "!"])

            details: list = [
                self.artes_ids[arte['id']], arte['tp_cost'], arte['cast_time'] if arte['cast_time'] else "N/A",
                *learn_conditions, *evolve_conditions,
                FatalStrikeType(arte['fatal_strike_type']).name
            ]

            report_list.append(details)

        field_names: list[str] = ["Arte", "TP", "Cast Time",
                                  "Learn Condition 1", "Learn Parameter 1", "Learn Meta 1",
                                  "Learn Condition 2", "Learn Parameter 2", "Learn Meta 2",
                                  "Learn Condition 3", "Learn Parameter 3", "Learn Meta 3",
                                  "Learn Condition 4", "Learn Parameter 4", "Learn Meta 4",
                                  "Learn Condition 5", "Learn Parameter 5", "Learn Meta 5",
                                  "Learn Condition 6", "Learn Parameter 6", "Learn Meta 6",
                                  "Evolves From",
                                  "Evolve Condition 1", "Evolve Parameter 1",
                                  "Evolve Condition 2", "Evolve Parameter 2",
                                  "Evolve Condition 3", "Evolve Parameter 3",
                                  "Evolve Condition 4", "Evolve Parameter 4",
                                  "Fatal Strike Type"]

        with open(self.report_output, "a+") as f:
            writer = csv.writer(f)
            writer.writerow(field_names)
            writer.writerows(report_list)
            writer.writerow([""])

            f.flush()
            f.close()

    def generate_skills_report(self, patched_skills: dict):
        report_list: list = []
        for skill in [*patched_skills.values()]:
            report_list.append([
                self.skill_ids[skill['id']], skill['sp_cost'], skill['lp_cost'], Symbol(skill['symbol']).name,
                skill['symbol_weight'], 'Yes' if skill['is_equippable'] else 'No'
            ])

        field_names: list[str] = ["Skill", "SP", "LP", "Symbol", "Symbol Weight", "Equippable"]

        with open(self.report_output, "a+") as f:
            writer = csv.writer(f)
            writer.writerow(field_names)
            writer.writerows(report_list)
            writer.writerow([""])

            f.flush()
            f.close()

    def randomize_artes_input(self, patch):
        # Based on average amount of character artes with evolve conditions
        evolve_opportunities: list[int] = [0, 0.0258, 0.0041, 0.0005, 0.005]
        # Based on average amount of character artes with learn conditions
        learn_opportunities: list[int] = [0, 0.75, 0.042, 0.8, 0.077]
        learn_type_opportunities: list[list[int]] = [[0, 0], [0.35, 0.05], [0.005, 0.005], [0.75, 0.05], [0.5, 0.5]]

        def _randomize_evolve(target_arte, character, count):
            target_arte[f'evolve_condition{count}'] = 3
            target_arte[f'evolve_parameter{count}'] = self.random.choice(self.skills_by_char[character])

        def _randomize_learn(target_arte, character, count):
            condition_pop: list[int] = [_ for _ in range(1 if count <= 1 else 2, 4)]
            condition_chances: list[float] = [0.6] if count <= 1 else []
            condition_chances.extend(learn_type_opportunities[count])

            meta: int = 0

            condition: int = self.random.choices(condition_pop, weights=condition_chances)[0]
            if condition == 1:
                cap_level: int = self.random.randint(5, 20)
                parameter = self.random.randint(1, cap_level)
            elif condition == 2:
                parameter: int = self.random.choice(self.artes_by_char[character])
                meta = math.ceil(10 * (self.random.randrange(10, 100) / 100))
            else:
                parameter: int = self.random.choice(self.skills_by_char[character])

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
            if self.random.random() <= 0.05:
                continue

            r_candidates += 1
            data = self.artes_data_table[int(arte['id'])]

            # Randomize TP Cost
            if self.random.random() <= 0.4:
                r_tp += 1
                arte['tp_cost'] = math.ceil(int(arte['tp_cost']) * (self.random.randrange(10, 200) * 0.01))

            # Randomize Cast Time
            if int(arte['cast_time']) > 0 and self.random.random() >= 0.3:
                r_cast += 1
                arte['cast_time'] = math.ceil(int(arte['cast_time']) *
                                              (self.random.randrange(10, 200) * 0.01))

            # Randomize FS Type
            if self.random.random() <= 0.75:
                r_fs += 1
                arte['fatal_strike_type'] = self.random.randrange(0, 3)

            # Randomize Evolution
            ## Only Randomize Artes with Evolve Conditions already, since Evolve Base can't seem to be changed for now
            has_evolve: bool = False
            if arte['evolve_base']:
                has_evolve = True

                # Average Total Artes over Altered Artes Count across all Party Members
                if self.random.random() <= 0.258:
                    r_evolve += 1

                    ## Can't change evolve base for now; this property seems to be for information display only
                    # arte['evolve_base'] = self.random.choice(self.artes_by_char[data['character_ids'][0]])

                    continue_iter: bool = True
                    iterations: int = 1
                    while iterations < len(evolve_opportunities):

                        if continue_iter:
                            _randomize_evolve(arte, data['character_ids'][0], iterations)
                        else:
                            arte[f'evolve_condition{iterations}'] = 0
                            arte[f'evolve_parameter{iterations}'] = 0

                        if continue_iter and self.random.random() > evolve_opportunities[iterations]:
                            continue_iter = False

                        iterations += 1

                    usage_req: int = self.random.choice([5, 10])
                    if self.random.random() <= 0.4: math.ceil(usage_req *
                                                              (self.random.randrange(10, 100) / 100))

                    arte['learn_condition1'] = 2
                    arte['learn_parameter1'] = int(arte['id'])
                    arte['unknown3'] = usage_req

            # Randomize Learn Condition
            if self.random.random() < learn_opportunities[has_evolve + 1]:
                r_learn += 1
                continue_iter: bool = True
                iterations: int = 2 if has_evolve else 1
                while iterations < len(learn_opportunities):
                    if continue_iter: _randomize_learn(arte, data['character_ids'][0], iterations)
                    else:
                        arte[f"learn_condition{iterations}"] = 0
                        arte[f"learn_parameter{iterations}"] = 0
                        arte[f"unknown{iterations + 2}"] = 0

                    if continue_iter and self.random.random() > learn_opportunities[iterations]:
                        continue_iter = False

                    iterations += 1

                # If Arte has Evolve Conditions from Vanilla, remove them if Learn Condition is randomized
                if not has_evolve and arte['evolve_base']:
                    arte['evolve_base'] = 0
                    for _ in range(1, 5):
                        arte[f'evolve_condition{_}'] = 0
                        arte[f'evolve_parameter{_}'] = 0

            new_input[data['entry']] = arte

        print("--- Artes Results -------------------")
        print(f"Total Artes: {len(patch)}")

        print(f"Randomized: {r_candidates} ({r_candidates / len(patch) * 100:.2f}%)")
        print(f"Randomized TP: {r_tp} ({r_tp / r_candidates * 100:.2f}%)")
        print(f"Randomized Cast Time: {r_cast} ({r_cast / r_candidates * 100:.2f}%)")
        print(f"Randomized Fatal Strike Type: {r_fs} ({r_fs / r_candidates * 100:.2f}%)")
        print(f"Randomized Evolve Conditions: {r_evolve} ({r_evolve / r_candidates * 100:.2f}%)")
        print(f"Randomized Learn Conditions: {r_learn} ({r_learn / r_candidates * 100:.2f}%)")
        print("\n")

        return new_input

    def randomize_skills_input(self, patch):
        symbol_distribution: list[float] = [0.28, 0.20, 0.27, 0.25]

        new_input: dict = {}

        r_candidates: int = 0
        r_sp: int = 0
        r_lp: int = 0
        r_sym: int = 0
        r_sym_w: int = 0
        for skill in patch:
            # Randomize Candidacy
            if self.random.random() <= 0.05:
                continue

            r_candidates += 1
            data = self.skills_data_table[skill['id']]

            # Randomize SP Cost
            if skill['sp_cost'] and self.random.random() <= 0.95:
                r_sp += 1
                skill['sp_cost'] = self.random_from_distribution(7.6, 5, 0, 30)

            # Randomize LP
            if skill['lp_cost']:
                if self.random.random() <= 0.95:
                    r_lp += 1
                    base = self.random_from_distribution(329.16, 226.17, 100, 1600)
                    skill['lp_cost'] = int(max(int(math.ceil(base / 100.0)) * 10, 10) if base % 100 != 0 else base / 10)
                else:
                    skill['lp_cost'] = int(skill['lp_cost'] / 10)

            # Randomize Symbol
            if self.random.random() <= 0.75:
                r_sym += 1
                skill['symbol'] = self.random.choices([_ for _ in range(4)], symbol_distribution)[0]

            # Randomize Symbol Weight
            if self.random.random() <= 0.75:
                r_sym_w += 1
                skill['symbol_weight'] = self.random_from_distribution(3.48, 2.58, 0, 30)

            new_input[data['entry']] = skill

        print("--- Skills Results -------------------")
        print(f"Total Skills: {len(patch)}")

        print(f"Randomized: {r_candidates} ({r_candidates / len(patch) * 100:.2f}%)")
        print(f"Randomized SP: {r_sp} ({r_sp / r_candidates * 100:.2f}%)")
        print(f"Randomized LP: {r_lp} ({r_lp / r_candidates * 100:.2f}%)")
        print(f"Randomized Symbol: {r_sym} ({r_sym / r_candidates * 100:.2f}%)")
        print(f"Randomized Symbol Weight: {r_sym_w} ({r_sym_w / r_candidates * 100:.2f}%)")
        print("\n")

        return new_input

if __name__ == "__main__":
    template = InputTemplate()
    template.generate()