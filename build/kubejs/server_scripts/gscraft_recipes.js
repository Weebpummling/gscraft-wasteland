// GSCraft - recipe stripping for the station-only rule and the designed rosters (crafting draft §2, §4;
// mod-capabilities §2, §6). Everything removed here comes back, where the design wants it, as a
// station order or a blueprint-gated recipe in Phase C. Nothing is added here.
//
// 1. Benches: crafting happens only at server-placed stations, so no bench is craftable - the vanilla
//    crafting table, the IE Engineer's Workbench and crafting table, the Refurbished Furniture
//    workbench, Superb Warfare's vehicle assembling table and reforging table, every Immersive Vehicles
//    bench and its fuel pump (Walker's yard and Michael's plant place them).
// 2. Superb Warfare defences: Marshall's Walls 1-3 hand these out as station orders.
// 3. Vehicles: only the designed roster keeps a recipe (speedboat, truck, LAV-150, the battery packs and
//    the reset kit on the SW side); every vvp / MCSP military vehicle and every SW vehicle outside the
//    roster loses its assembling recipe. The Humvee RWS, Black Hawk and Bradley return blueprint-gated
//    (quests W-M1, W-B3, X6). Immersive Vehicles' civilian roster is handled by its own craftingoverrides
//    file in Phase C, not here.

ServerEvents.recipes(event => {
  const removed = [];
  const rm = (filter, why) => { event.remove(filter); removed.push(why); };

  // --- 1. benches
  rm({ output: 'minecraft:crafting_table' }, 'crafting table');
  rm({ output: 'immersiveengineering:craftingtable' }, 'IE crafting table');
  rm({ output: 'immersiveengineering:workbench' }, 'IE engineer workbench');
  rm({ output: 'refurbished_furniture:workbench' }, 'RF workbench');
  rm({ output: 'superbwarfare:vehicle_assembling_table' }, 'SW assembling table');
  rm({ output: 'superbwarfare:reforging_table' }, 'SW reforging table');
  ['vehiclebench', 'gunbench', 'decorbench', 'custombench', 'itembench', 'instrumentbench', 'seatbench',
   'wheelbench', 'propellerbench', 'enginebench', 'fuelpump'].forEach(b => rm({ output: 'mts:mts.' + b }, 'IV ' + b));

  // --- 2. Superb Warfare defences (Walls 1-3 station orders)
  ['laser_tower', 'laser_unit', 'waveforce_tower', 'hpj_11', 'hpj_11_blueprint', 'claymore_mine', 'c4_bomb', 'c4_bomb_rc',
   'mortar_barrel', 'mortar_base_plate', 'mortar_bipod', 'mortar_deployer', 'mortar_shell', 'drone', 'swarm_drone',
   'sandbag', 'barbed_wire', 'jump_pad', 'fumo_25', 'aircraft_catapult', 'dps_generator_deployer', 'target_deployer',
   'tow_deployer'].forEach(d => rm({ output: 'superbwarfare:' + d }, 'SW ' + d));

  // --- 3. vehicles outside the roster
  rm({ type: 'superbwarfare:vehicle_assembling', mod: 'vvp' }, 'all vvp vehicles');
  rm({ type: 'superbwarfare:vehicle_assembling', mod: 'mcsp' }, 'all MCSP vehicles');
  ['a_10a', 'ah_6', 'annihilator', 'bl_132', 'bmp_2', 'mi_28', 'mk_42', 'mle_1934', 'plz_05', 'prism_tank', 'tom_6',
   'type_63', 'wheel_chair', 'yx_100'].forEach(v => rm({ id: 'superbwarfare:' + v }, 'SW vehicle ' + v));

  console.info('[gscraft] recipes stripped: ' + removed.length + ' rules (benches, SW defences, military and off-roster vehicles)');
});
