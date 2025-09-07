import ctypes
import array
import copy
import json
import mmap


class VesperiaFileEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ctypes.Structure):
            return obj.__dict__

        return super().default(obj)

class SkillsHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic_number", ctypes.c_char * 8),
        ("entries", ctypes.c_uint32),
        ("entry_end", ctypes.c_uint32),
    ]

    def __init__(self, entries: int, entry_end: int):
        super(SkillsHeader).__init__("T8BTSK  ", entries, entry_end)

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

    name: str = "SKILL_NONE"

class ArtesHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic_number", ctypes.c_char * 8),
        ("entries", ctypes.c_uint32),
        ("entry_end", ctypes.c_uint32),
    ]

    def __init__(self, entries: int, entry_end: int):
        super(ArtesHeader).__init__("T8BTMA  ", entries, entry_end)


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

        if len(args) >= 96 and args[-2] > 1:
            character_id_entry_size = args[-2]
            args = tuple([*args[:95], (ctypes.c_uint32 * character_id_entry_size)(*args[95:])])
        elif "character_id_entries" in kwargs and kwargs["character_id_entries"] > 1:
            character_id_entry_size = kwargs["character_id_entries"]
            kwargs["character_id_entries"] = (ctypes.c_uint32 * character_id_entry_size)(*args[95:])

        if character_id_entry_size > 1:
            local_fields = copy.deepcopy(cls._fields_)
            local_fields[-1] = ("character_ids", ctypes.c_uint32 * character_id_entry_size)

            class BaseArteEntry(ctypes.Structure):
                _pack_ = 1
                _fields_ = local_fields

            return BaseArteEntry(*args, **kwargs)

        return super().__new__(cls, *args, **kwargs)

def generate_skills_manifest(filename: str, skills: list[SkillsEntry], strings: list[str]):
    data: dict[str, list] = {"entries": skills, "strings": strings}

    with open(filename, "w+") as f:
        json.dump(data, f, cls=VesperiaFileEncoder, indent=4)
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