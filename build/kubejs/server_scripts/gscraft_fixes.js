// GSCraft server scripts - recipe repairs for the rebuilt pack.
// Factory Blocks ships two mason table recipes: mason_table.json in the Chipped 2.x format
// (fails to parse on Chipped 3.x) and mason_table_old.json in the 3.x format (works).
// The datapack /wasteland/datapacks/gscraft overrides mason_table.json with a valid 3.x copy so
// the boot stays clean; this removes that duplicate so only mason_table_old feeds the bench.
ServerEvents.recipes(event => {
  event.remove({ id: 'factory_blocks:mason_table' })
})
