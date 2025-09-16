import ctypes
import copy
import json
import mmap
from _ctypes import Structure


class VesperiaStructureEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ctypes.Structure):
            d: dict = {}
            try:
                for attribute in o._fields_:
                    name: str = attribute[0]
                    value = getattr(o, attribute[0])

                    if issubclass(type(value), ctypes.Array):
                        value = [*value]
                    elif type(value) is bytes:
                        value = value.decode('utf-8')

                    d[name] = value
            except TypeError:
                return TypeError
            return d

        return super().default(o)

class SkillsHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic_number", ctypes.c_char * 8),
        ("entries", ctypes.c_uint32),
        ("entry_end", ctypes.c_uint32),
    ]

    def __init__(self, entries: int, entry_end: int):
        super().__init__("T8BTSK  ".encode(), entries, entry_end)

class SkillsEntry(ctypes.Structure):
    """Byte Structure Template for Skill Entries in file data64/btl.svo/BTL_PACK.DAT/0010 (T8BTSK)"""
    _pack_ = 1
    _fields_ = [
        ("next_entry_offset", ctypes.c_uint32),
        ("entry", ctypes.c_uint32),
        ("id", ctypes.c_uint32),
        ("string_pointer", ctypes.c_uint64),
        ("name_string_key", ctypes.c_uint32),
        ("desc_string_key", ctypes.c_uint32),
        ("unknown1", ctypes.c_uint32),
        ("unknown2", ctypes.c_uint32),
        ("sp_cost", ctypes.c_uint32),
        ("lp_cost", ctypes.c_uint32),
        ("symbol", ctypes.c_uint32),
        ("symbol_weight", ctypes.c_uint32),
        ("paramater1", ctypes.c_float),
        ("paramater2", ctypes.c_float),
        ("paramater3", ctypes.c_float),
        ("is_equippable", ctypes.c_uint32),
    ]

class ArtesHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic_number", ctypes.c_char * 8),
        ("entries", ctypes.c_uint32),
        ("entry_end", ctypes.c_uint32),
    ]

    def __init__(self, entries: int, entry_end: int):
        super().__init__("T8BTMA  ".encode(), entries, entry_end)


class ArtesEntry(ctypes.Structure):
    """Byte Structure Template for Arte Entries in file data64/btl.svo/BTL_PACK.DAT/0004 (T8BTMA)"""
    _pack_ = 1
    _fields_ = [
        ("next_entry_offset", ctypes.c_uint32),
        ("entry", ctypes.c_uint32),
        ("id", ctypes.c_uint32),
        ("unknown0", ctypes.c_uint64),
        ("string_pointer", ctypes.c_uint64),
        ("name_string_key", ctypes.c_uint32),
        ("desc_string_key", ctypes.c_uint32),
        ("arte_type", ctypes.c_uint32),
        ("tp_cost", ctypes.c_uint32),
        # Elemental Power
        ("power", ctypes.c_uint32),
        ("fire_power", ctypes.c_uint32),
        ("earth_power", ctypes.c_uint32),
        ("wind_power", ctypes.c_uint32),
        ("water_power", ctypes.c_uint32),
        ("light_power", ctypes.c_uint32),
        ("dark_power", ctypes.c_uint32),
        ("unknown_power", ctypes.c_uint32),
        ("semi_auto_range_min", ctypes.c_uint32),
        ("semi_auto_range_max", ctypes.c_uint32),
        ("unknown1", ctypes.c_uint32),
        ("unknown2", ctypes.c_uint32),
        ("cast_time", ctypes.c_uint32),
        # Learn Attributes
        ("learn_condition1", ctypes.c_uint32),
        ("learn_condition2", ctypes.c_uint32),
        ("learn_condition3", ctypes.c_uint32),
        ("learn_condition4", ctypes.c_uint32),
        ("learn_condition5", ctypes.c_uint32),
        ("learn_condition6", ctypes.c_uint32),
        ("learn_parameter1", ctypes.c_uint32),
        ("learn_parameter2", ctypes.c_uint32),
        ("learn_parameter3", ctypes.c_uint32),
        ("learn_parameter4", ctypes.c_uint32),
        ("learn_parameter5", ctypes.c_uint32),
        ("learn_parameter6", ctypes.c_uint32),
        ("unknown3", ctypes.c_uint32),
        ("unknown4", ctypes.c_uint32),
        ("unknown5", ctypes.c_uint32),
        ("unknown6", ctypes.c_uint32),
        ("unknown7", ctypes.c_uint32),
        ("unknown8", ctypes.c_uint32),
        ("unknown9", ctypes.c_uint32),
        ("magic_attack_mod", ctypes.c_uint32),
        ("unknown10", ctypes.c_float),
        ("casting_circle_type", ctypes.c_uint32),
        ("is_usable_outside_battle", ctypes.c_uint32),
        ("target_type", ctypes.c_uint32),
        # Enemy Type Power
        ("vs_human_power", ctypes.c_uint32),
        ("vs_beast_power", ctypes.c_uint32),
        ("vs_bird_power", ctypes.c_uint32),
        ("vs_magic_power", ctypes.c_uint32),
        ("vs_plant_power", ctypes.c_uint32),
        ("vs_aquatic_power", ctypes.c_uint32),
        ("vs_insect_power", ctypes.c_uint32),
        ("vs_inorganic_power", ctypes.c_uint32),
        ("vs_scale_power", ctypes.c_uint32),
        ("vs_small_power", ctypes.c_uint32),
        ("vs_normal_power", ctypes.c_uint32),
        ("vs_big_power", ctypes.c_uint32),
        ("vs_large_power", ctypes.c_uint32),
        # Status Effects
        ("status_effect1", ctypes.c_uint32),
        ("status_effect2", ctypes.c_uint32),
        ("status_effect3", ctypes.c_uint32),
        ("status_effect1_parameter", ctypes.c_uint32),
        ("status_effect2_parameter", ctypes.c_uint32),
        ("status_effect3_parameter", ctypes.c_uint32),
        ("ground_enable_uses", ctypes.c_int32),
        ("aerial_enable_uses", ctypes.c_int32),
        ("aerial_enable_skill1", ctypes.c_uint32),
        ("aerial_enable_skill2", ctypes.c_uint32),
        # Evolve Attributes
        ("can_evolve", ctypes.c_uint32),
        ("evolve_condition1", ctypes.c_uint32),
        ("evolve_condition2", ctypes.c_uint32),
        ("evolve_condition3", ctypes.c_uint32),
        ("evolve_condition4", ctypes.c_uint32),
        ("evolve_base", ctypes.c_uint32),
        ("evolve_parameter1", ctypes.c_uint32),
        ("evolve_parameter2", ctypes.c_uint32),
        ("evolve_parameter3", ctypes.c_uint32),
        ("evolve_parameter4", ctypes.c_uint32),
        ("physical_attack_mod", ctypes.c_uint32),
        ("unknown11", ctypes.c_uint32),
        ("unknown12", ctypes.c_uint32),
        ("unknown13", ctypes.c_uint32),
        ("fatal_strike_type", ctypes.c_uint32),
        # Time/Weather Power
        ("day_weather_power", ctypes.c_uint32),
        ("cloudy_weather_power", ctypes.c_uint32),
        ("fog_weather_power", ctypes.c_uint32),
        ("night_weather_power", ctypes.c_uint32),
        ("rain_weather_power", ctypes.c_uint32),
        ("snow_weather_power", ctypes.c_uint32),
        ("sandstorm_weather_power", ctypes.c_uint32),
        ("evening_weather_power", ctypes.c_uint32),
        ("semi_auto_range_max_advance", ctypes.c_uint32),
        ("semi_auto_range_max_brainiac", ctypes.c_uint32),
        ("semi_auto_range_max_critical", ctypes.c_uint32),
        ("character_id_entries", ctypes.c_uint32),
        ("character_ids", ctypes.c_uint32 * 1),
    ]

    def __new__(cls, *args, **kwargs):
        # Automatically Handle Variable Length of Character IDs Attribute
        character_id_entry_size: int = 1

        if len(args) >= 97:
            character_id_entry_size = args[-2]
            id_entries: list[int] = []
            for id_entry in args[96:]:
                if isinstance(id_entry, int):
                    id_entries.append(id_entry)
                elif isinstance(id_entry, list):
                    id_entries.extend(id_entry)
            args = tuple([*args[:96], (ctypes.c_uint32 * character_id_entry_size)(*id_entries)])
        elif "character_id_entries" in kwargs and "character_ids" in kwargs:
            character_id_entry_size = kwargs["character_id_entries"]
            kwargs["character_ids"] = (ctypes.c_uint32 * character_id_entry_size)(*kwargs["character_ids"])

        local_fields = copy.deepcopy(cls._fields_)
        local_fields[-1] = ("character_ids", ctypes.c_uint32 * character_id_entry_size)

        class BaseArteEntry(ctypes.Structure):
            _pack_ = 1
            _fields_ = local_fields
        return BaseArteEntry(*args, **kwargs)

    @classmethod
    def from_buffer_copy(cls, source, offset:... = 0):
        character_id_entry_size_position: int = ctypes.sizeof(cls) - 8
        character_id_entry_size: int = int.from_bytes(
            source[character_id_entry_size_position:character_id_entry_size_position + 4], "little"
        )

        local_fields = copy.deepcopy(cls._fields_)
        local_fields[-1] = ("character_ids", ctypes.c_uint32 * character_id_entry_size)

        class BaseArteEntry(ctypes.Structure):
            _pack_ = 1
            _fields_ = local_fields

        return BaseArteEntry.from_buffer_copy(source, offset)

class ItemEntry(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("name_string_key", ctypes.c_uint32),
        ("buy_price", ctypes.c_uint32),
        ("menu_use_type", ctypes.c_uint32),
        ("character_usable", ctypes.c_uint32),
        ("unknown0", ctypes.c_uint32),
        ("icon", ctypes.c_uint32),
        ("category", ctypes.c_uint32),
        ("picture", ctypes.c_char * 32),
        ("unknown1", ctypes.c_uint32),
        ("desc1_string_key", ctypes.c_uint32),
        ("battle_use_type", ctypes.c_uint32),
        ("phy_attack", ctypes.c_uint32),
        ("magic_attack", ctypes.c_uint32),
        ("phy_defense", ctypes.c_uint32),
        ("magic_defense", ctypes.c_uint32),
        ("tp_heal", ctypes.c_uint32),
        ("luck", ctypes.c_uint32),
        ("agility", ctypes.c_uint32),
        ("phys_attack_increase", ctypes.c_uint32),
        ("phys_defense_increase", ctypes.c_uint32),
        ("fire_power", ctypes.c_uint32),
        ("water_power", ctypes.c_uint32),
        ("wind_power", ctypes.c_uint32),
        ("earth_power", ctypes.c_uint32),
        ("light_power", ctypes.c_uint32),
        ("dark_power", ctypes.c_uint32),
        ("skill1", ctypes.c_uint32),
        ("skill1_lp", ctypes.c_uint32),
        ("skill2", ctypes.c_uint32),
        ("skill2_lp", ctypes.c_uint32),
        ("skill3", ctypes.c_uint32),
        ("skill3_lp", ctypes.c_uint32),
        ("parameter22", ctypes.c_uint32),
        ("parameter23", ctypes.c_uint32),
        ("parameter24", ctypes.c_uint32),
        ("desc2_string_key", ctypes.c_uint32),
        ("enemy_drop1", ctypes.c_uint32),
        ("enemy_drop2", ctypes.c_uint32),
        ("enemy_drop3", ctypes.c_uint32),
        ("enemy_drop4", ctypes.c_uint32),
        ("enemy_drop5", ctypes.c_uint32),
        ("enemy_drop6", ctypes.c_uint32),
        ("enemy_drop7", ctypes.c_uint32),
        ("enemy_drop8", ctypes.c_uint32),
        ("enemy_drop9", ctypes.c_uint32),
        ("enemy_drop10", ctypes.c_uint32),
        ("enemy_drop11", ctypes.c_uint32),
        ("enemy_drop12", ctypes.c_uint32),
        ("enemy_drop13", ctypes.c_uint32),
        ("enemy_drop14", ctypes.c_uint32),
        ("enemy_drop15", ctypes.c_uint32),
        ("enemy_drop16", ctypes.c_uint32),
        ("enemy_drop1_chance", ctypes.c_uint32),
        ("enemy_drop2_chance", ctypes.c_uint32),
        ("enemy_drop3_chance", ctypes.c_uint32),
        ("enemy_drop4_chance", ctypes.c_uint32),
        ("enemy_drop5_chance", ctypes.c_uint32),
        ("enemy_drop6_chance", ctypes.c_uint32),
        ("enemy_drop7_chance", ctypes.c_uint32),
        ("enemy_drop8_chance", ctypes.c_uint32),
        ("enemy_drop9_chance", ctypes.c_uint32),
        ("enemy_drop10_chance", ctypes.c_uint32),
        ("enemy_drop11_chance", ctypes.c_uint32),
        ("enemy_drop12_chance", ctypes.c_uint32),
        ("enemy_drop13_chance", ctypes.c_uint32),
        ("enemy_drop14_chance", ctypes.c_uint32),
        ("enemy_drop15_chance", ctypes.c_uint32),
        ("enemy_drop16_chance", ctypes.c_uint32),
        ("enemy_steal1", ctypes.c_uint32),
        ("enemy_steal2", ctypes.c_uint32),
        ("enemy_steal3", ctypes.c_uint32),
        ("enemy_steal4", ctypes.c_uint32),
        ("enemy_steal5", ctypes.c_uint32),
        ("enemy_steal6", ctypes.c_uint32),
        ("enemy_steal7", ctypes.c_uint32),
        ("enemy_steal8", ctypes.c_uint32),
        ("enemy_steal9", ctypes.c_uint32),
        ("enemy_steal10", ctypes.c_uint32),
        ("enemy_steal11", ctypes.c_uint32),
        ("enemy_steal12", ctypes.c_uint32),
        ("enemy_steal13", ctypes.c_uint32),
        ("enemy_steal14", ctypes.c_uint32),
        ("enemy_steal15", ctypes.c_uint32),
        ("enemy_steal16", ctypes.c_uint32),
        ("enemy_steal1_chance", ctypes.c_uint32),
        ("enemy_steal2_chance", ctypes.c_uint32),
        ("enemy_steal3_chance", ctypes.c_uint32),
        ("enemy_steal4_chance", ctypes.c_uint32),
        ("enemy_steal5_chance", ctypes.c_uint32),
        ("enemy_steal6_chance", ctypes.c_uint32),
        ("enemy_steal7_chance", ctypes.c_uint32),
        ("enemy_steal8_chance", ctypes.c_uint32),
        ("enemy_steal9_chance", ctypes.c_uint32),
        ("enemy_steal10_chance", ctypes.c_uint32),
        ("enemy_steal11_chance", ctypes.c_uint32),
        ("enemy_steal12_chance", ctypes.c_uint32),
        ("enemy_steal13_chance", ctypes.c_uint32),
        ("enemy_steal14_chance", ctypes.c_uint32),
        ("enemy_steal15_chance", ctypes.c_uint32),
        ("enemy_steal16_chance", ctypes.c_uint32),
        ("location1", ctypes.c_uint32),
        ("location2", ctypes.c_uint32),
        ("location3", ctypes.c_uint32),
        ("recipe1", ctypes.c_uint32),
        ("recipe2", ctypes.c_uint32),
        ("recipe3", ctypes.c_uint32),
        ("recipe4", ctypes.c_uint32),
        ("unknown2", ctypes.c_uint32),
        ("unknown3", ctypes.c_uint32),
        ("unknown4", ctypes.c_uint32),
        ("unknown5", ctypes.c_uint32),
        ("unknown6", ctypes.c_uint32),
        ("synth1_level", ctypes.c_uint32),
        ("synth1_cost", ctypes.c_uint32),
        ("synth1_unknown", ctypes.c_uint32),
        ("synth1_material1", ctypes.c_uint32),
        ("synth1_material1_amount", ctypes.c_uint32),
        ("synth1_material2", ctypes.c_uint32),
        ("synth1_material2_amount", ctypes.c_uint32),
        ("synth1_material3", ctypes.c_uint32),
        ("synth1_material3_amount", ctypes.c_uint32),
        ("synth1_material4", ctypes.c_uint32),
        ("synth1_material4_amount", ctypes.c_uint32),
        ("synth1_material5", ctypes.c_uint32),
        ("synth1_material5_amount", ctypes.c_uint32),
        ("synth1_material6", ctypes.c_uint32),
        ("synth1_material6_amount", ctypes.c_uint32),
        ("synth1_material_size", ctypes.c_uint32),
        ("synth2_level", ctypes.c_uint32),
        ("synth2_cost", ctypes.c_uint32),
        ("synth2_unknown", ctypes.c_uint32),
        ("synth2_material1", ctypes.c_uint32),
        ("synth2_material1_amount", ctypes.c_uint32),
        ("synth2_material2", ctypes.c_uint32),
        ("synth2_material2_amount", ctypes.c_uint32),
        ("synth2_material3", ctypes.c_uint32),
        ("synth2_material3_amount", ctypes.c_uint32),
        ("synth2_material4", ctypes.c_uint32),
        ("synth2_material4_amount", ctypes.c_uint32),
        ("synth2_material5", ctypes.c_uint32),
        ("synth2_material5_amount", ctypes.c_uint32),
        ("synth2_material6", ctypes.c_uint32),
        ("synth2_material6_amount", ctypes.c_uint32),
        ("synth2_material_size", ctypes.c_uint32),
        ("synth3_level", ctypes.c_uint32),
        ("synth3_cost", ctypes.c_uint32),
        ("synth3_unknown", ctypes.c_uint32),
        ("synth3_material1", ctypes.c_uint32),
        ("synth3_material1_amount", ctypes.c_uint32),
        ("synth3_material2", ctypes.c_uint32),
        ("synth3_material2_amount", ctypes.c_uint32),
        ("synth3_material3", ctypes.c_uint32),
        ("synth3_material3_amount", ctypes.c_uint32),
        ("synth3_material4", ctypes.c_uint32),
        ("synth3_material4_amount", ctypes.c_uint32),
        ("synth3_material5", ctypes.c_uint32),
        ("synth3_material5_amount", ctypes.c_uint32),
        ("synth3_material6", ctypes.c_uint32),
        ("synth3_material6_amount", ctypes.c_uint32),
        ("synth3_material_size", ctypes.c_uint32),
        ("synth_size", ctypes.c_uint32),
        ("unknown7", ctypes.c_uint32),
        ("unknown8", ctypes.c_uint32),
        ("unknown9", ctypes.c_uint32),
        ("unknown10", ctypes.c_uint32),
        ("unknown11", ctypes.c_uint32),
        ("unknown12", ctypes.c_uint32),
        ("model_id", ctypes.c_int32),
        ("entry", ctypes.c_uint32),
        ("battle_used", ctypes.c_uint32),
        ("show_in_book", ctypes.c_uint32),
        ("unknown13", ctypes.c_uint32),
        ("unknown14", ctypes.c_uint32),
        ("unknown15", ctypes.c_uint32),
        ("unknown16", ctypes.c_uint32),
        ("unknown17", ctypes.c_uint32),
        ("unknown18", ctypes.c_uint32),
    ]

    def __init__(self, *args, **kwargs):
        if len(args) == 178 and isinstance(args[8], str):
            args = tuple([*args[:7], args[8].encode(), *args[8:]])
        elif "picture" in kwargs:
            kwargs["picture"] = kwargs["picture"].encode()

        super().__init__(*args, **kwargs)

    @classmethod
    def copy(cls, item_entry):
        new_entry = type(item_entry)()
        ctypes.pointer(new_entry)[0] = item_entry

        return new_entry

class ItemSortEntry(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("entry", ctypes.c_uint32),
        ("id", ctypes.c_uint32),
        ("id_sort", ctypes.c_uint32),
        ("phys_attack_sort", ctypes.c_uint32),
        ("phys_defense_sort", ctypes.c_uint32),
        ("magic_attack_sort", ctypes.c_uint32),
        ("magic_defense_sort", ctypes.c_uint32),
        ("padding1", ctypes.c_uint32),
        ("padding2", ctypes.c_uint32),
        ("padding3", ctypes.c_uint32),
        ("padding4", ctypes.c_uint32),
    ]

    @classmethod
    def from_item_generic(cls, entry:int, item_entry: ItemEntry = None, **item_data):
        if isinstance(item_entry, ItemEntry):
            return ItemSortEntry(entry,
                                 item_entry.id,
                                 item_entry.id,
                                 item_entry.id,
                                 item_entry.id,
                                 item_entry.id,
                                 item_entry.id,
                                 0, 0, 0, 0)

        elif "id" in item_data:
            return ItemSortEntry(entry, *[item_data["id"] for _ in range(6)], 0, 0, 0, 0)

        return None

class SearchPointHeader(ctypes.Structure):
    _padding_ = 1
    _fields_ = [
        ("magic_number", ctypes.c_char * 8),
        ("file_size", ctypes.c_uint32),
        ("definition_start", ctypes.c_uint32),
        ("definition_entries", ctypes.c_uint32),
        ("content_start", ctypes.c_uint32),
        ("content_entries", ctypes.c_uint32),
        ("item_start", ctypes.c_uint32),
        ("item_entries", ctypes.c_uint32),
        ("entry_end", ctypes.c_uint32),
        ("padding1", ctypes.c_uint64),
        ("padding2", ctypes.c_uint64),
        ("padding3", ctypes.c_uint64),
    ]

    def __init__(self, file_size:int,
                 definition_start:int, definition_entries:int,
                 content_start:int, content_entries:int,
                 item_start:int, item_entries:int,
                 entry_end:int):
        super().__init__("TOVSEAF ".encode(), file_size,
                         definition_start, definition_entries,
                         content_start, content_entries,
                         item_start, item_entries,
                         entry_end, 0, 0, 0)

class SearchPointDefinitionEntry(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("index", ctypes.c_uint32),
        ("scenario_begin", ctypes.c_uint32),
        ("scenario_end", ctypes.c_uint32),
        ("type", ctypes.c_uint32),
        ("unknown0", ctypes.c_uint32),
        ("x_coord", ctypes.c_int32),
        ("y_coord", ctypes.c_int32),
        ("z_coord", ctypes.c_int32),
        ("unknown1", ctypes.c_uint16),
        ("chance", ctypes.c_uint16),
        ("disappear_rate", ctypes.c_uint32),
        ("unknown2", ctypes.c_uint32),
        ("unknown3", ctypes.c_uint32),
        ("unknown4", ctypes.c_uint32),
        ("max_use", ctypes.c_uint16),
        ("unknown5", ctypes.c_uint16),
        ("content_index", ctypes.c_uint32),
        ("content_range", ctypes.c_uint32),
    ]

class SearchPointContentEntry(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("chance", ctypes.c_uint32),
        ("item_index", ctypes.c_uint32),
        ("item_range", ctypes.c_uint32),
        ("padding", ctypes.c_uint32),
    ]

class SearchPointItemEntry(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("count", ctypes.c_uint32),
    ]

def generate_skills_manifest(filename: str, skills: list[SkillsEntry], strings: list[str]):
    data: dict[str, list] = {"entries": skills, "strings": strings}

    with open(filename, "w+") as f:
        json.dump(data, f, cls=VesperiaStructureEncoder, indent=4)
        f.close()

def generate_skills_file(file: str, header: SkillsHeader, skills: list[SkillsEntry], strings: list[str]):
    with open(file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)

        size: int = (ctypes.sizeof(SkillsHeader) +
                     ctypes.sizeof(SkillsEntry) * len(skills) +
                     sum(len(i) + 1 for i in strings))
        mm.resize(size)

        mm.write(bytearray(header))
        for skill in skills:
            mm.write(bytearray(skill))

        for string in strings:
            mm.write(("x\00" + string).encode('utf-8'))

        mm.flush()
        f.close()