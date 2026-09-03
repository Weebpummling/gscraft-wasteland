#!/usr/bin/env python3
"""
makeremap.py - complete the block remap for the transplant.

    python makeremap.py --todo remap_todo.json --base remap.json --out remap_full.json

Explicit mappings first (worldgen strata and ores from cut mods become the vanilla rock they stand
in for; Spore's infested blocks become their clean counterparts), then suffix rules for whatever is
left (stairs stay stairs, slabs stay slabs, planks stay planks...), and only then air. Prints what
went to air so it can be eyeballed.
"""

import json
import sys
from collections import Counter
from pathlib import Path

EXPLICIT = {
    # --- Warium worldgen
    "crusty_chunks:tar": "minecraft:blackstone",
    "crusty_chunks:bauxite": "minecraft:terracotta",
    "crusty_chunks:uranium_ore": "minecraft:stone",
    "crusty_chunks:sulfur_ore": "minecraft:stone",
    "crusty_chunks:lead_ore": "minecraft:stone",
    "crusty_chunks:zinc_ore": "minecraft:stone",
    "crusty_chunks:nickel_ore": "minecraft:stone",
    "crusty_chunks:lithium_ore": "minecraft:stone",
    "crusty_chunks:beryllium_ore": "minecraft:stone",
    "crusty_chunks:pyrochlore_ore": "minecraft:stone",
    "crusty_chunks:deepslate_lead_ore": "minecraft:deepslate",
    "crusty_chunks:red_armor_slab": "minecraft:smooth_stone_slab",
    "crusty_chunks:red_armor_stairs": "minecraft:stone_brick_stairs",
    "crusty_chunks:gray_armor_optic": "minecraft:gray_concrete",
    # --- Create strata and ores
    "create:limestone": "minecraft:stone",
    "create:ochrum": "minecraft:tuff",
    "create:veridium": "minecraft:tuff",
    "create:crimsite": "minecraft:granite",
    "create:asurine": "minecraft:deepslate",
    "create:scoria": "minecraft:blackstone",
    "create:zinc_ore": "minecraft:stone",
    "create:deepslate_zinc_ore": "minecraft:deepslate",
    "create:metal_girder": "minecraft:iron_bars",
    "create:andesite_ladder": "minecraft:ladder",
    "create:track_station": "minecraft:air",
    "create:hand_crank": "minecraft:air",
    "create:controls": "minecraft:air",
    "create:small_bogey": "minecraft:air",
    "create:gearshift": "minecraft:air",
    "create:creative_motor": "minecraft:air",
    # --- Survival Instinct ores
    "survival_instinct:steellium_ore": "minecraft:stone",
    "survival_instinct:sulfur_ore": "minecraft:stone",
    "survival_instinct:deepslate_sulfur_ore": "minecraft:deepslate",
    # --- Iron's Spellbooks
    "irons_spellbooks:arcane_debris": "minecraft:deepslate",
    "irons_spellbooks:pedestal": "minecraft:air",
    "irons_spellbooks:inscription_table": "minecraft:air",
    "irons_spellbooks:arcane_anvil": "minecraft:anvil",
    "irons_spellbooks:alchemist_cauldron": "minecraft:cauldron",
    "irons_spellbooks:scroll_forge": "minecraft:air",
    # --- Alex's Caves (surface structures and build material)
    "alexscaves:cinder_block": "minecraft:light_gray_concrete",
    "alexscaves:cinder_block_slab": "minecraft:smooth_stone_slab",
    "alexscaves:cinder_block_stairs": "minecraft:stone_brick_stairs",
    "alexscaves:cinder_block_wall": "minecraft:stone_brick_wall",
    "alexscaves:scrap_metal_plate": "immersiveengineering:sheetmetal_iron",
    "alexscaves:scrap_metal": "immersiveengineering:sheetmetal_iron",
    "alexscaves:rusty_scrap_metal_plate": "factory_blocks:rust",
    "alexscaves:rusty_scrap_metal": "factory_blocks:rust",
    "alexscaves:smooth_limestone": "minecraft:smooth_stone",
    "alexscaves:smooth_limestone_wall": "minecraft:stone_brick_wall",
    "alexscaves:metal_rebar": "minecraft:iron_bars",
    "alexscaves:rusty_rebar": "minecraft:iron_bars",
    "alexscaves:rusty_scaffolding": "immersiveengineering:steel_scaffolding_standard",
    "alexscaves:rusty_barrel": "minecraft:barrel",
    "alexscaves:metal_barrel": "minecraft:barrel",
    "alexscaves:waste_drum": "minecraft:barrel",
    "alexscaves:hazmat_block": "minecraft:yellow_concrete",
    "alexscaves:hazmat_skull_block": "minecraft:yellow_concrete",
    "alexscaves:block_of_azure_neodymium": "minecraft:iron_block",
    "alexscaves:uranium_rod": "minecraft:iron_bars",
    "alexscaves:galena_pillar": "minecraft:polished_deepslate",
    "alexscaves:radrock_wall": "minecraft:cobblestone_wall",
    "alexscaves:smooth_bone_wall": "minecraft:bone_block",
    "alexscaves:siren_light": "minecraft:redstone_lamp",
    "alexscaves:nuclear_siren": "minecraft:air",
    "alexscaves:hologram_projector": "minecraft:air",
    "alexscaves:copper_valve": "minecraft:air",
    "alexscaves:magnetic_activator": "minecraft:air",
    "alexscaves:spelunkery_table": "minecraft:air",
    "alexscaves:nuclear_furnace_component": "minecraft:iron_block",
    "alexscaves:nuclear_furnace": "minecraft:air",
    "alexscaves:quarry": "minecraft:air",
    "alexscaves:thornwood_door": "minecraft:dark_oak_door",
    # --- Spore (long gone; today these are holes)
    "spore:infested_deepslate": "minecraft:deepslate",
    "spore:infested_stone": "minecraft:stone",
    "spore:infested_dirt": "minecraft:dirt",
    "spore:infested_clay": "minecraft:clay",
    "spore:infested_gravel": "minecraft:gravel",
    "spore:infested_laboratory_block": "minecraft:light_gray_concrete",
    "spore:infested_laboratory_block1": "minecraft:light_gray_concrete",
    "spore:infested_laboratory_block2": "minecraft:light_gray_concrete",
    "spore:infested_laboratory_block3": "minecraft:light_gray_concrete",
    "spore:lab_block": "minecraft:white_concrete",
    "spore:lab_block1": "minecraft:white_concrete",
    "spore:lab_block2": "minecraft:white_concrete",
    "spore:lab_block3": "minecraft:white_concrete",
    "spore:lab_slab": "minecraft:smooth_stone_slab",
    "spore:lab_stair": "minecraft:stone_brick_stairs",
    "spore:rotten_stair": "minecraft:oak_stairs",
    "spore:rotten_slab": "minecraft:oak_slab",
    "spore:reinforced_door": "minecraft:iron_door",
    "spore:iron_ladder": "minecraft:ladder",
    "spore:vent_plate": "minecraft:iron_trapdoor",
    # --- Twilight Forest blocks used in overworld builds
    "twilightforest:sorting_planks": "minecraft:jungle_planks",
    "twilightforest:sorting_slab": "minecraft:jungle_slab",
    "twilightforest:mossy_towerwood": "minecraft:dark_oak_planks",
    "twilightforest:infested_towerwood": "minecraft:dark_oak_planks",
    "twilightforest:cracked_towerwood": "minecraft:dark_oak_planks",
    "twilightforest:towerwood": "minecraft:dark_oak_planks",
    "twilightforest:weathered_deadrock": "minecraft:deepslate",
    "twilightforest:deadrock": "minecraft:deepslate",
    "twilightforest:cracked_deadrock": "minecraft:cracked_deepslate_bricks",
    "twilightforest:nagastone_pillar": "minecraft:polished_deepslate",
    "twilightforest:spiral_bricks": "minecraft:stone_bricks",
    "twilightforest:mossy_underbrick": "minecraft:mossy_stone_bricks",
    "twilightforest:iron_ladder": "minecraft:ladder",
    "twilightforest:canopy_bookshelf": "minecraft:bookshelf",
    "twilightforest:liveroot_block": "minecraft:rooted_dirt",
    "twilightforest:root": "minecraft:rooted_dirt",
    "twilightforest:firefly": "minecraft:air",
    "twilightforest:dark_slab": "minecraft:dark_oak_slab",
    "twilightforest:twilight_oak_log": "minecraft:oak_log",
    "twilightforest:rainbow_oak_leaves": "minecraft:oak_leaves",
    "twilightforest:transformation_leaves": "minecraft:birch_leaves",
    "twilightforest:transformation_wood": "minecraft:birch_wood",
    "twilightforest:ironwood_block": "minecraft:iron_block",
    "twilightforest:wrought_iron_fence": "minecraft:iron_bars",
    "twilightforest:twilight_portal": "minecraft:water",
    "twilightforest:transformation_log_core": "minecraft:oak_log",
    "twilightforest:canopy_chest": "minecraft:chest",
    "twilightforest:candelabra": "minecraft:lantern",
    "backrooms:cement": "minecraft:light_gray_concrete",
    "backrooms:pipe_cluster": "minecraft:iron_bars",
    "backrooms:pipe_e": "minecraft:iron_bars",
    "backrooms:pipe_i": "minecraft:iron_bars",
    "backrooms:pipe_l": "minecraft:iron_bars",
    "backrooms:pipe_t": "minecraft:iron_bars",
    "backrooms:pipe_tc": "minecraft:iron_bars",
    "backrooms:pipe_ltc": "minecraft:iron_bars",
    "backrooms:cable_cluster": "minecraft:iron_bars",
    "backrooms:fuse_box": "minecraft:iron_block",
    "backrooms:pallet": "minecraft:oak_slab",
    "backrooms:cardboard_box": "minecraft:barrel",
    "from_the_caves:step": "minecraft:smooth_stone_slab",
    "waystones:mossy_waystone": "minecraft:lodestone",
    "horror_element_mod:light_on": "minecraft:redstone_lamp",
    "horror_element_mod:broken_light": "minecraft:redstone_lamp",
    "horror_element_mod:hospital_bed": "minecraft:white_bed",
    "horror_element_mod:barricadeoak": "minecraft:oak_fence",
    "horror_element_mod:barricade_oak_bloody": "minecraft:oak_fence",
    "horror_element_mod:woodden_shutter": "minecraft:oak_trapdoor",
}

# Suffix rules for whatever remains (checked in order).
RULES = [
    ("deepslate_", "_ore", "minecraft:deepslate"),
    ("", "_ore", "minecraft:stone"),
    ("", "_stairs", "minecraft:stone_brick_stairs"),
    ("", "_stair", "minecraft:stone_brick_stairs"),
    ("", "_slab", "minecraft:smooth_stone_slab"),
    ("", "_wall", "minecraft:cobblestone_wall"),
    ("", "_trapdoor", "minecraft:iron_trapdoor"),
    ("", "_door", "minecraft:iron_door"),
    ("", "_fence_gate", "minecraft:oak_fence_gate"),
    ("", "_fence", "minecraft:oak_fence"),
    ("", "_banister", "minecraft:oak_fence"),
    ("", "_pane", "minecraft:glass_pane"),
    ("", "_planks", "minecraft:oak_planks"),
    ("", "_log", "minecraft:oak_log"),
    ("", "_wood", "minecraft:oak_wood"),
    ("", "_leaves", "minecraft:oak_leaves"),
    ("", "_sapling", "minecraft:air"),
    ("", "_bookshelf", "minecraft:bookshelf"),
    ("", "_ladder", "minecraft:ladder"),
    ("", "_glass", "minecraft:glass"),
    ("", "_bricks", "minecraft:stone_bricks"),
    ("", "_brick", "minecraft:stone_bricks"),
    ("", "_concrete", "minecraft:gray_concrete"),
    ("", "_carpet", "minecraft:gray_carpet"),
    ("", "_wool", "minecraft:gray_wool"),
    ("", "_lamp", "minecraft:redstone_lamp"),
    ("", "_light", "minecraft:sea_lantern"),
    ("", "_lantern", "minecraft:lantern"),
    ("", "_torch", "minecraft:torch"),
    ("", "_block", "minecraft:stone"),
    ("", "stone", "minecraft:stone"),
    ("", "rock", "minecraft:stone"),
    ("", "dirt", "minecraft:dirt"),
    ("", "grass", "minecraft:grass_block"),
    ("", "sand", "minecraft:sand"),
    ("", "gravel", "minecraft:gravel"),
]


def by_rule(name: str):
    local = name.split(":", 1)[1]
    for prefix, suffix, target in RULES:
        if local.startswith(prefix) and local.endswith(suffix):
            return target
    return "minecraft:air"


def main(argv):
    a = dict(zip(argv[1::2], argv[2::2]))
    todo = json.loads(Path(a["--todo"]).read_text(encoding="utf-8"))
    base = json.loads(Path(a["--base"]).read_text(encoding="utf-8"))
    out = dict(base)
    to_air = Counter()
    by_source = Counter()
    for name, count in todo.items():
        if name in out:
            continue
        if name in EXPLICIT:
            out[name] = EXPLICIT[name]; by_source["explicit"] += count
        else:
            out[name] = by_rule(name); by_source["rule" if out[name] != "minecraft:air" else "air"] += count
        if out[name] == "minecraft:air":
            to_air[name] += count
    Path(a["--out"]).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"remap entries: {len(out)}  (blocks covered: explicit {by_source['explicit']:,}, by rule {by_source['rule']:,}, to air {by_source['air']:,})")
    print("\nmapped to AIR (check these are genuinely disposable):")
    for name, n in to_air.most_common(60):
        print(f"  {n:>8}  {name}")
    print(f"\n-> {a['--out']}")


if __name__ == "__main__":
    main(sys.argv)
