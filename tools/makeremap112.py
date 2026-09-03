"""Build remap112.json (1.12.2 modded block -> 1.20.1 blockstate) from remap112_todo.json + rules.

usage: makeremap112.py [remap112_todo.json] [remap112.json]

Resolution order for a modded (name, meta):
  1. exact  "name[meta]"  in EXACT
  2. exact  "name"        in EXACT
  3. first PREFIX rule whose prefix matches the name (in order)
  4. unmapped -> PLACEHOLDER (light gray concrete) and listed in remap112_unmapped.json
Values are 1.20.1 block names, optionally with properties: "minecraft:oak_slab[type=top]".
"air" is a valid target. Terrain families (Chisel worldgen stone, ores, Dynamic Trees, BOP) are
included so the whole modded overlay of a volume resolves, not only the build blocks.
"""
import sys, json
from pathlib import Path

PLACEHOLDER = "minecraft:light_gray_concrete"
COLOURS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
           "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]

EXACT = {
    # --- Chisel: colour and family blocks
    **{f"chisel:antiblock[{i}]": f"minecraft:{c}_concrete" for i, c in enumerate(COLOURS)},
    "chisel:basalt1": "minecraft:polished_basalt", "chisel:basalt2": "minecraft:basalt",
    "chisel:marble2": "minecraft:stone", "chisel:limestone2": "minecraft:stone",
    "chisel:marble1": "minecraft:quartz_block", "chisel:limestone1": "minecraft:smooth_sandstone",
    "chisel:concrete_lightgray1": "minecraft:light_gray_concrete", "chisel:concrete_gray1": "minecraft:gray_concrete",
    "chisel:concrete_white1": "minecraft:white_concrete", "chisel:concrete_black1": "minecraft:black_concrete",
    "chisel:glass": "minecraft:glass", "chisel:glass1": "minecraft:tinted_glass", "chisel:glasspane": "minecraft:glass_pane",
    "chisel:ironpane": "minecraft:iron_bars", "chisel:blocksteel": "immersiveengineering:sheetmetal_steel",
    "chisel:factory": "factory_blocks:factory", "chisel:factory1": "factory_blocks:factory",
    "chisel:technical": "immersiveengineering:sheetmetal_iron", "chisel:technical1": "immersiveengineering:sheetmetal_iron",
    "chisel:technicalnew": "immersiveengineering:sheetmetal_iron", "chisel:laboratory": "minecraft:white_concrete",
    "chisel:futura": "minecraft:light_blue_concrete", "chisel:blockiron": "minecraft:iron_block",
    "chisel:blockgold": "minecraft:gold_block", "chisel:blockdiamond": "minecraft:diamond_block",
    "chisel:blockemerald": "minecraft:emerald_block", "chisel:blockcoal": "minecraft:coal_block",
    "chisel:blocklapis": "minecraft:lapis_block", "chisel:blockredstone": "minecraft:redstone_block",
    "chisel:tyrian": "minecraft:cyan_terracotta", "chisel:hexplating": "minecraft:gray_concrete",
    "chisel:valentines": "minecraft:pink_concrete", "chisel:voidstone": "minecraft:blackstone",
    "chisel:energizedvoidstone": "minecraft:crying_obsidian", "chisel:temple": "minecraft:sandstone",
    "chisel:templemossy": "minecraft:mossy_stone_bricks", "chisel:cloud": "minecraft:white_wool",
    "chisel:paper": "minecraft:white_wool", "chisel:waterstone": "minecraft:prismarine",
    "chisel:lavastone": "minecraft:magma_block", "chisel:charcoal": "minecraft:coal_block",
    "chisel:brownstone": "minecraft:bricks", "chisel:planks-oak": "minecraft:oak_planks",
    "chisel:planks-spruce": "minecraft:spruce_planks", "chisel:planks-birch": "minecraft:birch_planks",
    "chisel:planks-jungle": "minecraft:jungle_planks", "chisel:planks-acacia": "minecraft:acacia_planks",
    "chisel:planks-dark-oak": "minecraft:dark_oak_planks", "chisel:stonebrick": "minecraft:stone_bricks",
    "chisel:stonebrick1": "minecraft:stone_bricks", "chisel:stonebrick2": "minecraft:stone_bricks",
    "chisel:cobblestone": "minecraft:cobblestone", "chisel:cobblestone1": "minecraft:cobblestone",
    "chisel:cobblestone2": "minecraft:cobblestone", "chisel:cobblestonemossy": "minecraft:mossy_cobblestone",
    "chisel:andesite1": "minecraft:polished_andesite", "chisel:andesite2": "minecraft:andesite",
    "chisel:diorite1": "minecraft:polished_diorite", "chisel:diorite2": "minecraft:diorite",
    "chisel:granite1": "minecraft:polished_granite", "chisel:granite2": "minecraft:granite",
    "chisel:sandstoneyellow1": "minecraft:sandstone", "chisel:sandstoneyellow2": "minecraft:sandstone",
    "chisel:sandstonered1": "minecraft:red_sandstone", "chisel:sandstonered2": "minecraft:red_sandstone",
    "chisel:bricks": "minecraft:bricks", "chisel:bricks1": "minecraft:bricks", "chisel:bricks2": "minecraft:bricks",
    "chisel:netherbrick": "minecraft:nether_bricks", "chisel:quartz1": "minecraft:quartz_block",
    "chisel:quartz2": "minecraft:quartz_block", "chisel:prismarine1": "minecraft:prismarine",
    "chisel:prismarine2": "minecraft:prismarine", "chisel:obsidian": "minecraft:obsidian",
    "chisel:obsidian1": "minecraft:obsidian", "chisel:obsidian2": "minecraft:obsidian",
    "chisel:ice": "minecraft:packed_ice", "chisel:icepillar": "minecraft:packed_ice",
    "chisel:bookshelf_oak": "minecraft:bookshelf", "chisel:carpet": "minecraft:light_gray_carpet",
    "chisel:auto_chisel": "air",
    # --- Fureniku's Roads: meta 3 of generic_blocks is the asphalt everywhere; kerbs and lines by name
    "furenikusroads:generic_blocks[0]": "minecraft:gray_concrete", "furenikusroads:generic_blocks[1]": "minecraft:gray_concrete",
    "furenikusroads:generic_blocks[2]": "minecraft:light_gray_concrete", "furenikusroads:generic_blocks[3]": "minecraft:black_concrete",
    "furenikusroads:generic_blocks[4]": "minecraft:black_concrete", "furenikusroads:generic_blocks[5]": "minecraft:gray_concrete",
    "furenikusroads:generic_blocks": "minecraft:black_concrete",
    "furenikusroads:road_block_standard": "minecraft:black_concrete", "furenikusroads:road_block_concrete_2": "minecraft:gray_concrete",
    "furenikusroads:road_block_concrete": "minecraft:gray_concrete", "furenikusroads:road_block_worn": "minecraft:black_concrete",
    "furenikusroads:road_block_slab": "minecraft:smooth_stone_slab", "furenikusroads:road_block_slab_double": "minecraft:smooth_stone",
    "furenikusroads:road_block_stairs": "minecraft:stone_stairs",
    "furenikusroads:road_block_paint_white": "minecraft:white_concrete", "furenikusroads:road_block_paint_yellow": "minecraft:yellow_concrete",
    # --- Immersive Engineering 1.12 -> 1.20 (same mod, renamed blocks). stone_decoration meta order (1.12):
    # 0 cokebrick 1 blastbrick 2 blastbrick_reinforced 3 coke 4 hempcrete 5 concrete 6 concrete_tile 7 concrete_leaded
    # 8 insulating_glass 9 concrete_sprayed 10 alloybrick
    "immersiveengineering:stone_decoration[0]": "immersiveengineering:cokebrick",
    "immersiveengineering:stone_decoration[1]": "immersiveengineering:blastbrick",
    "immersiveengineering:stone_decoration[2]": "immersiveengineering:blastbrick_reinforced",
    "immersiveengineering:stone_decoration[3]": "immersiveengineering:coke",
    "immersiveengineering:stone_decoration[4]": "immersiveengineering:hempcrete",
    "immersiveengineering:stone_decoration[5]": "immersiveengineering:concrete",
    "immersiveengineering:stone_decoration[6]": "immersiveengineering:concrete_tile",
    "immersiveengineering:stone_decoration[7]": "immersiveengineering:concrete_leaded",
    "immersiveengineering:stone_decoration[8]": "immersiveengineering:insulating_glass",
    "immersiveengineering:stone_decoration[9]": "immersiveengineering:concrete_sprayed",
    "immersiveengineering:stone_decoration[10]": "immersiveengineering:alloybrick",
    "immersiveengineering:stone_decoration": "immersiveengineering:concrete",
    "immersiveengineering:stone_decoration_slab": "immersiveengineering:slab_concrete",
    "immersiveengineering:stone_decoration_stairs_concrete_tile": "immersiveengineering:stairs_concrete_tile",
    "immersiveengineering:stone_decoration_stairs_concrete": "immersiveengineering:stairs_concrete",
    "immersiveengineering:stone_decoration_stairs_concrete_leaded": "immersiveengineering:stairs_concrete_leaded",
    "immersiveengineering:stone_decoration_stairs_hempcrete": "immersiveengineering:stairs_hempcrete",
    "immersiveengineering:sheetmetal[0]": "immersiveengineering:sheetmetal_copper",
    "immersiveengineering:sheetmetal[1]": "immersiveengineering:sheetmetal_aluminum",
    "immersiveengineering:sheetmetal[2]": "immersiveengineering:sheetmetal_lead",
    "immersiveengineering:sheetmetal[3]": "immersiveengineering:sheetmetal_silver",
    "immersiveengineering:sheetmetal[4]": "immersiveengineering:sheetmetal_nickel",
    "immersiveengineering:sheetmetal[5]": "immersiveengineering:sheetmetal_uranium",
    "immersiveengineering:sheetmetal[6]": "immersiveengineering:sheetmetal_constantan",
    "immersiveengineering:sheetmetal[7]": "immersiveengineering:sheetmetal_electrum",
    "immersiveengineering:sheetmetal[8]": "immersiveengineering:sheetmetal_steel",
    "immersiveengineering:sheetmetal[9]": "immersiveengineering:sheetmetal_iron",
    "immersiveengineering:sheetmetal[10]": "immersiveengineering:sheetmetal_gold",
    "immersiveengineering:sheetmetal": "immersiveengineering:sheetmetal_iron",
    "immersiveengineering:sheetmetal_slab": "immersiveengineering:slab_sheetmetal_iron",
    "immersiveengineering:metal_decoration0": "immersiveengineering:steel_scaffolding_standard",
    "immersiveengineering:metal_decoration1[0]": "immersiveengineering:steel_fence",
    "immersiveengineering:metal_decoration1[1]": "immersiveengineering:steel_scaffolding_standard",
    "immersiveengineering:metal_decoration1[2]": "immersiveengineering:steel_scaffolding_grate_top",
    "immersiveengineering:metal_decoration1[3]": "immersiveengineering:steel_scaffolding_wooden_top",
    "immersiveengineering:metal_decoration1[4]": "immersiveengineering:alu_fence",
    "immersiveengineering:metal_decoration1[5]": "immersiveengineering:alu_scaffolding_standard",
    "immersiveengineering:metal_decoration1[6]": "immersiveengineering:alu_scaffolding_grate_top",
    "immersiveengineering:metal_decoration1[7]": "immersiveengineering:alu_scaffolding_wooden_top",
    "immersiveengineering:metal_decoration1": "immersiveengineering:steel_scaffolding_standard",
    "immersiveengineering:metal_decoration1_slab": "immersiveengineering:slab_steel_scaffolding_standard",
    "immersiveengineering:metal_decoration2": "immersiveengineering:steel_wallmount",
    "immersiveengineering:treated_wood": "immersiveengineering:treated_wood_horizontal",
    "immersiveengineering:treated_wood_slab": "immersiveengineering:slab_treated_wood_horizontal",
    "immersiveengineering:wooden_decoration": "immersiveengineering:treated_scaffold",
    "immersiveengineering:wooden_device0": "immersiveengineering:crate", "immersiveengineering:wooden_device1": "air",
    "immersiveengineering:storage": "minecraft:iron_block", "immersiveengineering:storage_slab": "minecraft:cut_copper_slab",
    "immersiveengineering:metal_device0": "air", "immersiveengineering:metal_device1": "air",
    "immersiveengineering:connector": "air", "immersiveengineering:conveyor": "air",
    "immersiveengineering:metal_multiblock": "immersiveengineering:sheetmetal_steel",
    "immersiveengineering:stone_device": "minecraft:cobblestone", "immersiveengineering:cloth_device": "minecraft:white_wool",
    "immersiveengineering:fake_light": "air", "immersiveengineering:metal_ladder": "minecraft:ladder",
    "immersivepetroleum:stone_decoration": "immersiveengineering:concrete",
    "immersivepetroleum:metal_multiblock": "immersiveengineering:sheetmetal_steel",
    # --- HBM: structure only, machines become shells
    "hbm:deco_steel": "immersiveengineering:sheetmetal_steel", "hbm:deco_titanium": "immersiveengineering:sheetmetal_iron",
    "hbm:deco_tungsten": "immersiveengineering:sheetmetal_iron", "hbm:deco_lead": "immersiveengineering:sheetmetal_lead",
    "hbm:deco_beryllium": "immersiveengineering:sheetmetal_aluminum", "hbm:deco_red_copper": "minecraft:copper_block",
    "hbm:deco_aluminium": "immersiveengineering:sheetmetal_aluminum", "hbm:deco_asbestos": "minecraft:white_concrete",
    "hbm:steel_wall": "immersiveengineering:sheetmetal_steel", "hbm:steel_corner": "immersiveengineering:sheetmetal_steel",
    "hbm:steel_roof": "immersiveengineering:sheetmetal_steel", "hbm:steel_beam": "immersiveengineering:steel_scaffolding_standard",
    "hbm:steel_scaffold": "immersiveengineering:steel_scaffolding_standard", "hbm:steel_grate": "immersiveengineering:steel_scaffolding_grate_top",
    "hbm:steel_poles": "minecraft:chain", "hbm:pole_top": "minecraft:chain", "hbm:pole_satellite_receiver": "minecraft:chain",
    "hbm:railing_normal": "minecraft:iron_bars", "hbm:railing_corner": "minecraft:iron_bars", "hbm:railing_ledge": "minecraft:iron_bars",
    "hbm:fence_metal": "minecraft:iron_bars", "hbm:barbed_wire": "minecraft:iron_bars", "hbm:concrete_pillar": "minecraft:gray_concrete",
    "hbm:brick_concrete": "minecraft:gray_concrete", "hbm:brick_concrete_mossy": "minecraft:gray_concrete",
    "hbm:brick_concrete_cracked": "minecraft:gray_concrete", "hbm:brick_concrete_broken": "minecraft:gray_concrete",
    "hbm:brick_concrete_marked": "minecraft:yellow_concrete", "hbm:brick_light": "minecraft:light_gray_concrete",
    "hbm:concrete": "minecraft:gray_concrete", "hbm:concrete_smooth": "minecraft:light_gray_concrete",
    "hbm:concrete_asbestos": "minecraft:white_concrete", "hbm:concrete_colored": "minecraft:light_gray_concrete",
    "hbm:reinforced_brick": "minecraft:stone_bricks", "hbm:reinforced_stone": "minecraft:deepslate_bricks",
    "hbm:reinforced_light": "minecraft:light_gray_concrete", "hbm:reinforced_sand": "minecraft:sandstone",
    "hbm:reinforced_glass": "minecraft:tinted_glass", "hbm:reinforced_lamp_on": "minecraft:sea_lantern",
    "hbm:reinforced_lamp_off": "minecraft:light_gray_concrete", "hbm:asphalt": "minecraft:black_concrete",
    "hbm:asphalt_light_on": "minecraft:sea_lantern", "hbm:asphalt_light_off": "minecraft:black_concrete",
    "hbm:glass_boron": "minecraft:glass", "hbm:glass_lead": "minecraft:tinted_glass", "hbm:glass_quartz": "minecraft:glass",
    "hbm:glass_uranium": "minecraft:lime_stained_glass", "hbm:glass_polonium": "minecraft:orange_stained_glass",
    "hbm:factory_titanium_hull": "immersiveengineering:sheetmetal_iron", "hbm:factory_titanium_furnace": "minecraft:blast_furnace",
    "hbm:factory_titanium_core": "minecraft:iron_block", "hbm:factory_advanced_hull": "immersiveengineering:sheetmetal_steel",
    "hbm:machine_tower_large": "minecraft:gray_concrete", "hbm:machine_tower_small": "minecraft:gray_concrete",
    "hbm:dummy_block_refinery": "immersiveengineering:sheetmetal_steel", "hbm:dummy_port_refinery": "immersiveengineering:sheetmetal_steel",
    "hbm:dummy_block_vault": "minecraft:iron_block", "hbm:dummy_port_vault": "minecraft:iron_block",
    "hbm:dummy_block_blast": "minecraft:iron_block", "hbm:dummy_port_blast": "minecraft:iron_block",
    "hbm:door_office": "minecraft:iron_door", "hbm:door_metal": "minecraft:iron_door", "hbm:door_bunker": "minecraft:iron_door",
    "hbm:tape_recorder": "minecraft:note_block", "hbm:red_barrel": "minecraft:red_concrete",
    "hbm:pink_barrel": "minecraft:pink_concrete", "hbm:yellow_barrel": "minecraft:yellow_concrete",
    "hbm:lox_barrel": "minecraft:white_concrete", "hbm:crate": "minecraft:barrel", "hbm:crate_lead": "minecraft:barrel",
    "hbm:crate_metal": "minecraft:barrel", "hbm:crate_weapon": "minecraft:barrel", "hbm:crate_iron": "minecraft:barrel",
    "hbm:crate_steel": "minecraft:barrel", "hbm:machine_battery": "minecraft:iron_block",
    "hbm:machine_generator": "minecraft:iron_block", "hbm:fusion_heater": "minecraft:iron_block",
    "hbm:reactor_element": "minecraft:iron_block", "hbm:cable_switch": "air", "hbm:red_cable": "air",
    "hbm:red_wire_coated": "air", "hbm:red_pylon": "minecraft:chain", "hbm:red_pylon_large": "minecraft:chain",
    "hbm:machine_difurnace_off": "minecraft:blast_furnace", "hbm:machine_electric_furnace_off": "minecraft:blast_furnace",
    "hbm:machine_difurnace_on": "minecraft:blast_furnace", "hbm:machine_electric_furnace_on": "minecraft:blast_furnace",
    "hbm:deco_pipe_rim": "minecraft:copper_block", "hbm:deco_pipe_rim_rusted": "minecraft:oxidized_copper",
    "hbm:sat_dock": "minecraft:iron_block", "hbm:launch_pad": "minecraft:iron_block", "hbm:machine_launch_pad": "minecraft:iron_block",
    "hbm:crashed_bomb": "air", "hbm:ladder_steel": "minecraft:ladder", "hbm:decal": "air",
    # --- Simply Light: neon
    "simplylight:illuminant_block_on": "minecraft:sea_lantern", "simplylight:illuminant_block": "minecraft:sea_lantern",
    "simplylight:illuminant_block_off": "minecraft:white_concrete", "simplylight:edge_light": "minecraft:end_rod",
    "simplylight:edge_light_top": "minecraft:end_rod", "simplylight:rodlamp": "minecraft:end_rod",
    "simplylight:lightbulb": "minecraft:end_rod", "simplylight:wall_lamp": "minecraft:end_rod",
    "simplylight:illuminant_slab": "minecraft:sea_lantern", "simplylight:lamp_post": "minecraft:chain",
    # --- Torchmaster / Serene Seasons / gore / furniture / guns / weather / NPCs: air
    "torchmaster:invisible_light": "air", "torchmaster:mega_torch": "minecraft:torch", "torchmaster:dread_lamp": "minecraft:lantern",
    "srparasites:infestremain": "air", "cfm:electric_fence": "minecraft:iron_bars",
    # --- Twilight Forest woods
    "twilightforest:twilight_log": "minecraft:dark_oak_log", "twilightforest:twilight_planks": "minecraft:dark_oak_planks",
    "twilightforest:magic_log": "minecraft:dark_oak_log", "twilightforest:tower_wood": "minecraft:dark_oak_planks",
    "twilightforest:twilight_leaves": "air", "twilightforest:magic_leaves": "air",
    # --- Macaw's bridges
    "mcwbridges:iron_bridge": "minecraft:iron_block", "mcwbridges:iron_bridge_pier": "minecraft:iron_block",
    "mcwbridges:rope_bridge": "minecraft:oak_planks", "mcwbridges:stone_bridge": "minecraft:stone_bricks",
    "mcwbridges:stone_brick_bridge": "minecraft:stone_bricks", "mcwbridges:stone_bridge_pier": "minecraft:stone_bricks",
    "mcwbridges:iron_bridge_stair": "minecraft:iron_block", "mcwbridges:stone_bridge_stair": "minecraft:stone_brick_stairs",
    "mcwbridges:balustrade_stone_bridge": "minecraft:stone_brick_wall", "mcwbridges:balustrade_iron_bridge": "minecraft:iron_bars",
    # --- worldgen strata / plants (the terrain part of the modded overlay)
    "hbm:stone_depth": "minecraft:deepslate", "hbm:stone_gneiss": "minecraft:tuff", "hbm:block_meteor_broken": "minecraft:blackstone",
    "hbm:meteor_polished": "minecraft:polished_blackstone", "hbm:meteor_brick": "minecraft:polished_blackstone_bricks",
    "hbm:gas_flammable": "air", "hbm:gas_explosive": "air", "hbm:gas_coal": "air", "hbm:gas_radon": "air",
    "hbm:sellafield_slaked": "minecraft:tuff", "hbm:sellafield": "minecraft:tuff", "hbm:waste_earth": "minecraft:coarse_dirt",
    "hbm:waste_grass": "minecraft:coarse_dirt", "hbm:grass_dead": "minecraft:coarse_dirt", "hbm:mycelium_dead": "minecraft:coarse_dirt",
    "hbm:waste_leaves": "air", "hbm:waste_log": "minecraft:dark_oak_log", "hbm:waste_planks": "minecraft:dark_oak_planks",
    "hbm:waste_trinitite": "minecraft:sand", "hbm:waste_trinitite_red": "minecraft:red_sand",
    "hbm:frozen_dirt": "minecraft:dirt", "hbm:frozen_grass": "minecraft:snow_block", "hbm:frozen_log": "minecraft:spruce_log",
    "hbm:frozen_leaves": "air", "hbm:frozen_planks": "minecraft:spruce_planks",
    "hbm:ore_oil": "minecraft:stone", "hbm:ore_coal_oil": "minecraft:coal_ore", "hbm:ore_lignite": "minecraft:coal_ore",
    "hbm:ore_copper": "minecraft:copper_ore", "hbm:ore_lead": "minecraft:stone", "hbm:ore_tungsten": "minecraft:stone",
    "hbm:ore_uranium": "minecraft:stone", "hbm:ore_thorium": "minecraft:stone", "hbm:ore_titanium": "minecraft:stone",
    "hbm:ore_sulfur": "minecraft:stone", "hbm:ore_niter": "minecraft:stone", "hbm:ore_aluminium": "minecraft:stone",
    "hbm:ore_fluorite": "minecraft:stone", "hbm:ore_beryllium": "minecraft:stone", "hbm:ore_rare": "minecraft:stone",
    "hbm:ore_depth_cinnebar": "minecraft:deepslate", "hbm:ore_depth_zirconium": "minecraft:deepslate",
    "hbm:ore_depth_borax": "minecraft:deepslate", "hbm:ore_depth_nether_neodymium": "minecraft:netherrack",
    "hbm:ore_nether_sulfur": "minecraft:netherrack", "hbm:ore_nether_fire": "minecraft:netherrack",
    "hbm:ore_nether_uranium": "minecraft:netherrack", "hbm:ore_nether_plutonium": "minecraft:netherrack",
    "hbm:ore_nether_tungsten": "minecraft:netherrack", "hbm:ore_nether_cobalt": "minecraft:netherrack",
    "hbm:cluster_iron": "minecraft:iron_ore", "hbm:cluster_titanium": "minecraft:stone", "hbm:cluster_aluminium": "minecraft:stone",
    "hbm:cluster_depth_iron": "minecraft:deepslate_iron_ore", "hbm:cluster_depth_titanium": "minecraft:deepslate",
    "hbm:cluster_depth_tungsten": "minecraft:deepslate", "hbm:cluster_depth_aluminium": "minecraft:deepslate",
    "hbm:cluster_depth_copper": "minecraft:deepslate_copper_ore",
    "mw:sulfurore": "minecraft:stone", "mw:leadore": "minecraft:stone", "mw:tinore": "minecraft:stone",
    "mw:graphiteore": "minecraft:coal_ore", "mw:copperore": "minecraft:copper_ore", "mw:silverore": "minecraft:stone",
    "immersiveengineering:ore[0]": "minecraft:copper_ore", "immersiveengineering:ore[1]": "immersiveengineering:ore_aluminum",
    "immersiveengineering:ore[2]": "immersiveengineering:ore_lead", "immersiveengineering:ore[3]": "immersiveengineering:ore_silver",
    "immersiveengineering:ore[4]": "immersiveengineering:ore_nickel", "immersiveengineering:ore[5]": "immersiveengineering:ore_uranium",
    "immersiveengineering:ore": "minecraft:stone",
    "biomesoplenty:dirt": "minecraft:dirt", "biomesoplenty:grass": "minecraft:grass_block", "biomesoplenty:dried_sand": "minecraft:sand",
    "biomesoplenty:white_sand": "minecraft:sand", "biomesoplenty:mud": "minecraft:mud", "biomesoplenty:ash_block": "minecraft:tuff",
    "biomesoplenty:hard_ice": "minecraft:packed_ice", "biomesoplenty:hard_dirt": "minecraft:coarse_dirt",
    "biomesoplenty:hard_sand": "minecraft:sandstone", "biomesoplenty:mud_brick_block": "minecraft:packed_mud",
    "biomesoplenty:gem_ore": "minecraft:stone", "biomesoplenty:crystal": "minecraft:amethyst_block",
}

# (prefix, target) - first match wins; "*leaves*" style handled by contains() below
PREFIX = [
    ("dynamictrees:leaves", "minecraft:oak_leaves"), ("dynamictreesbop:leaves", "minecraft:oak_leaves"),
    ("dynamictrees:oakbranch", "minecraft:oak_log"), ("dynamictrees:sprucebranch", "minecraft:spruce_log"),
    ("dynamictrees:birchbranch", "minecraft:birch_log"), ("dynamictrees:junglebranch", "minecraft:jungle_log"),
    ("dynamictrees:acaciabranch", "minecraft:acacia_log"), ("dynamictrees:darkoakbranch", "minecraft:dark_oak_log"),
    ("dynamictrees:", "minecraft:oak_log"), ("dynamictreesbop:", "minecraft:oak_log"),
    ("biomesoplenty:log_", "minecraft:oak_log"), ("biomesoplenty:leaves_", "minecraft:oak_leaves"),
    ("biomesoplenty:planks_", "minecraft:oak_planks"), ("biomesoplenty:sapling", "air"),
    ("biomesoplenty:plant_", "air"), ("biomesoplenty:flower_", "air"), ("biomesoplenty:mushroom", "air"),
    ("biomesoplenty:double_plant", "air"), ("biomesoplenty:coral", "air"), ("biomesoplenty:seaweed", "air"),
    ("biomesoplenty:bamboo", "minecraft:bamboo_block"), ("biomesoplenty:", "minecraft:dirt"),
    ("harvestcraft:", "air"), ("sereneseasons:", "air"), ("randomportals:", "air"), ("futuremc:", "air"),
    ("hbm:ore_", "minecraft:stone"), ("hbm:cluster_", "minecraft:stone"), ("hbm:gas_", "air"),
    ("hbm:deco_pipe_quad_green_rusted", "minecraft:oxidized_copper"), ("hbm:deco_pipe_framed_green_rusted", "minecraft:oxidized_copper"),
    ("hbm:deco_pipe_quad_rusted", "minecraft:weathered_copper"), ("hbm:deco_pipe_framed_rusted", "minecraft:weathered_copper"),
    ("hbm:deco_pipe_quad_green", "minecraft:copper_block"), ("hbm:deco_pipe_framed_green", "minecraft:copper_block"),
    ("hbm:deco_pipe_quad_red", "minecraft:red_concrete"), ("hbm:deco_pipe_framed_red", "minecraft:red_concrete"),
    ("hbm:deco_pipe_quad_marked", "minecraft:yellow_concrete"), ("hbm:deco_pipe_framed_marked", "minecraft:yellow_concrete"),
    ("hbm:deco_pipe_quad", "minecraft:copper_block"), ("hbm:deco_pipe_framed", "minecraft:copper_block"),
    ("hbm:deco_pipe", "minecraft:copper_block"), ("hbm:deco_", "immersiveengineering:sheetmetal_steel"),
    ("hbm:brick_", "minecraft:gray_concrete"), ("hbm:concrete", "minecraft:gray_concrete"),
    ("hbm:reinforced_", "minecraft:stone_bricks"), ("hbm:steel_", "immersiveengineering:sheetmetal_steel"),
    ("hbm:machine_", "minecraft:iron_block"), ("hbm:dummy_", "immersiveengineering:sheetmetal_steel"),
    ("hbm:door_", "minecraft:iron_door"), ("hbm:crate", "minecraft:barrel"), ("hbm:block_", "minecraft:iron_block"),
    ("hbm:fluid_duct", "air"), ("hbm:ff_", "air"), ("hbm:cable", "air"), ("hbm:red_", "air"), ("hbm:wire", "air"),
    ("hbm:tile", "air"), ("hbm:", "immersiveengineering:sheetmetal_steel"),
    ("chisel:antiblock", "minecraft:white_concrete"), ("chisel:factory", "factory_blocks:factory"),
    ("chisel:technical", "immersiveengineering:sheetmetal_iron"), ("chisel:concrete_", "minecraft:gray_concrete"),
    ("chisel:glass", "minecraft:glass"), ("chisel:planks-", "minecraft:oak_planks"), ("chisel:", "minecraft:light_gray_concrete"),
    ("furenikusroads:road_block_paint", "minecraft:white_concrete"), ("furenikusroads:road_block_slab", "minecraft:smooth_stone_slab"),
    ("furenikusroads:", "minecraft:black_concrete"),
    ("immersiveengineering:stone_decoration_stairs", "immersiveengineering:stairs_concrete"),
    ("immersiveengineering:stone_decoration", "immersiveengineering:concrete"),
    ("immersiveengineering:sheetmetal", "immersiveengineering:sheetmetal_iron"),
    ("immersiveengineering:metal_decoration", "immersiveengineering:steel_scaffolding_standard"),
    ("immersiveengineering:treated_wood", "immersiveengineering:treated_wood_horizontal"),
    ("immersiveengineering:wooden_", "immersiveengineering:treated_wood_horizontal"),
    ("immersiveengineering:metal_device", "air"), ("immersiveengineering:", "air"),
    ("immersivepetroleum:", "immersiveengineering:sheetmetal_steel"),
    ("simplylight:", "minecraft:sea_lantern"), ("torchmaster:", "air"), ("srparasites:", "air"),
    ("cfm:", "air"), ("mw:", "air"), ("weather2:", "air"), ("customnpcs:", "air"), ("coroutil:", "air"),
    ("openmodularturrets:", "minecraft:iron_block"), ("omlib:", "air"), ("vehicle:", "air"), ("thuttech:", "air"),
    ("twilightforest:", "minecraft:dark_oak_planks"), ("mcwbridges:", "minecraft:stone_bricks"),
    ("cookingforblockheads:", "air"), ("betterquesting:", "air"), ("opframe:", "air"), ("ichunutil:", "air"),
    ("simplylight", "minecraft:sea_lantern"), ("unknown:", "air"),
]


def resolve(name: str, meta: int):
    k = f"{name}[{meta}]"
    if k in EXACT: return EXACT[k], "exact-meta"
    if name in EXACT: return EXACT[name], "exact"
    for pre, to in PREFIX:
        if name.startswith(pre): return to, f"prefix:{pre}"
    return PLACEHOLDER, "unmapped"


def main(a):
    todo = Path(a[1]) if len(a) > 1 else Path(__file__).parent / "remap112_todo.json"
    out = Path(a[2]) if len(a) > 2 else Path(__file__).parent / "remap112.json"
    d = json.load(open(todo))
    table, unmapped, how = {}, [], {}
    for row in d["blocks"]:
        for m in row["metas"]:
            to, why = resolve(row["name"], m)
            table[f"{row['name']}[{m}]"] = to
            how[why.split(":")[0]] = how.get(why.split(":")[0], 0) + row["count"] / max(1, len(row["metas"]))
            if why == "unmapped":
                unmapped.append({"name": row["name"], "meta": m, "count": row["count"], "rects": row["rects"]})
    json.dump({"placeholder": PLACEHOLDER, "exact": EXACT, "prefix": PREFIX, "resolved": table},
              open(out, "w"), indent=1)
    json.dump(unmapped, open(out.with_name("remap112_unmapped.json"), "w"), indent=1)
    tot = sum(how.values())
    print(f"{len(table)} (name,meta) resolved -> {out}")
    print("  by rule:", {k: f"{100 * v / tot:.1f}%" for k, v in sorted(how.items(), key=lambda t: -t[1])})
    print(f"  unmapped names: {len(unmapped)} ({sum(u['count'] for u in unmapped):,} blocks) -> remap112_unmapped.json")
    for u in sorted(unmapped, key=lambda u: -u['count'])[:25]:
        print(f"    {u['count']:>8,}  {u['name']} [{u['meta']}]  {u['rects']}")


if __name__ == "__main__":
    main(sys.argv)
