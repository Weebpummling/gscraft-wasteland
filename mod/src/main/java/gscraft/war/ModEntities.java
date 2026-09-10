package gscraft.war;

import gscraft.war.entity.Scavenger;
import gscraft.war.entity.Soldier;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, GscraftWar.MODID);

    // One type per faction, so loot tables, Jade, spawn eggs and other mods can tell the armies apart.
    public static final RegistryObject<EntityType<Soldier>> NATO_SOLDIER = soldier("nato_soldier", "nato");
    public static final RegistryObject<EntityType<Soldier>> RUAF_SOLDIER = soldier("ruaf_soldier", "ruaf");

    public static final RegistryObject<EntityType<Scavenger>> SCAVENGER = ENTITIES.register("scavenger",
            () -> EntityType.Builder.of(Scavenger::new, MobCategory.CREATURE)
                    .sized(0.6F, 1.95F)
                    .clientTrackingRange(10)
                    .build(GscraftWar.MODID + ":scavenger"));

    private ModEntities() {}

    private static RegistryObject<EntityType<Soldier>> soldier(String name, String faction) {
        return ENTITIES.register(name, () -> EntityType.Builder
                .<Soldier>of((type, level) -> new Soldier(type, level, faction), MobCategory.MONSTER)
                .sized(0.6F, 1.95F)
                .clientTrackingRange(10)
                .build(GscraftWar.MODID + ":" + name));
    }

    static void attributes(EntityAttributeCreationEvent event) {
        event.put(NATO_SOLDIER.get(), Soldier.createAttributes().build());
        event.put(RUAF_SOLDIER.get(), Soldier.createAttributes().build());
        event.put(SCAVENGER.get(), Scavenger.createAttributes().build());
    }
}
