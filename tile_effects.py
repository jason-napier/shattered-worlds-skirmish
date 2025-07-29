# tile_effects.py

class TileEffect:
    def __init__(self, label, effect_type, value, flavor_text=""):
        """
        A single Evolution Grid tile's effect.
        
        :param label: Short name (e.g., "+2 ATK")
        :param effect_type: One of ['stat', 'ability', 'trait']
        :param value: Depends on effect_type:
            - 'stat': ('atk', +2), ('hp', +3), etc.
            - 'ability': ability_id string
            - 'trait': trait_id string
        :param flavor_text: Optional description or lore
        """
        self.label = label
        self.effect_type = effect_type
        self.value = value
        self.flavor_text = flavor_text

    def apply_to(self, unit):
        """Apply this tile's effect to a unit."""
        if self.effect_type == 'stat':
            stat, amount = self.value
            if hasattr(unit, stat):
                setattr(unit, stat, getattr(unit, stat) + amount)

        elif self.effect_type == 'ability':
            unit.abilities.append(self.value)

        elif self.effect_type == 'trait':
            unit.traits.append(self.value)

    def __repr__(self):
        return f"<TileEffect: {self.label}>"

def get_militia_tile_map():
    """Return a dict mapping (row, col) -> TileEffect for Militia units."""
    return {
        (2, 1): TileEffect("+2 ATK", "stat", ("atk", 2), "Train in brutal offense."),
        (1, 2): TileEffect("+3 HP", "stat", ("hp", 3), "Hardened constitution."),
        (2, 3): TileEffect("Shield Bearer", "trait", "block_chance", "Gain a chance to block incoming damage."),
        (3, 2): TileEffect("Taunt", "ability", "taunt_aoe", "Draw enemy aggression in an area."),
        (0, 2): TileEffect("War Cry", "ability", "war_cry", "Boost allies' morale."),
        (4, 2): TileEffect("Iron Stance", "trait", "resist_knockback", "Immune to knockback."),
        (2, 0): TileEffect("+1 MOV", "stat", ("mov", 1), "Improve combat footwork."),
        (2, 4): TileEffect("+1 RNG", "stat", ("rng", 1), "Learn to strike just a bit further."),
        (0, 0): TileEffect("Warlord Capstone", "trait", "leadership_aura", "Boost nearby allies."),
        (4, 4): TileEffect("Juggernaut Capstone", "trait", "unstoppable", "Ignore terrain and break through lines."),
    }

def get_archer_tile_map():
    return {
        (2, 1): TileEffect("+1 RNG", "stat", ("rng", 1), "Learn to fire from farther away."),
        (1, 2): TileEffect("+2 ATK", "stat", ("atk", 2), "Sharpened accuracy."),
        (2, 3): TileEffect("Multi-Shot", "ability", "multi_shot", "Attack multiple enemies in a line."),
        (3, 2): TileEffect("Focus Fire", "trait", "focus_fire", "Deal more damage to marked targets."),
        (0, 2): TileEffect("+3 HP", "stat", ("hp", 3), "Gain stamina to survive longer."),
        (2, 0): TileEffect("Smoke Arrow", "ability", "smoke_arrow", "Create a smoke field for cover."),
        (2, 4): TileEffect("Piercing Shot", "ability", "pierce_arrow", "Ignore enemy defense."),
        (4, 2): TileEffect("Hunter's Instinct", "trait", "detect_stealth", "Reveal hidden enemies."),
        (0, 0): TileEffect("Sniper Capstone", "trait", "longshot", "Ignore distance penalties."),
        (4, 4): TileEffect("Volley Master Capstone", "ability", "volley", "Rain arrows over a wide area."),
    }

def get_acolyte_tile_map():
    return {
        (2, 1): TileEffect("Heal Nearby", "ability", "group_heal", "Restore health to nearby allies."),
        (1, 2): TileEffect("+2 DEF", "stat", ("def_", 2), "Magical shielding."),
        (2, 3): TileEffect("Drain Touch", "ability", "drain_touch", "Deal damage and heal yourself."),
        (3, 2): TileEffect("Cleanse", "ability", "cleanse", "Remove debuffs from allies."),
        (0, 2): TileEffect("Soul Mend", "ability", "soul_mend", "Revive a fallen unit at low health."),
        (2, 0): TileEffect("+2 HP", "stat", ("hp", 2), "Greater resilience."),
        (2, 4): TileEffect("+1 MOV", "stat", ("mov", 1), "Move faster in battle."),
        (4, 2): TileEffect("Aura of Warding", "trait", "resist_burn_poison", "Grants resistance to damage over time."),
        (0, 0): TileEffect("Divine Capstone", "trait", "divine_shield", "Negate the first damage taken each turn."),
        (4, 4): TileEffect("Plague Capstone", "ability", "disease_burst", "Unleash a curse in a wide area."),
    }

def get_scout_tile_map():
    return {
        (2, 1): TileEffect("+1 MOV", "stat", ("mov", 1), "Quickstep training."),
        (1, 2): TileEffect("Backstab", "ability", "backstab", "Deal bonus damage from behind."),
        (2, 3): TileEffect("Mark Target", "ability", "mark_target", "Reveal and debuff an enemy."),
        (3, 2): TileEffect("Trap Set", "ability", "trap_set", "Lay a hidden snare."),
        (0, 2): TileEffect("Dash", "ability", "dash", "Move again after attacking."),
        (2, 0): TileEffect("+2 ATK", "stat", ("atk", 2), "Precision bladework."),
        (2, 4): TileEffect("Disengage", "ability", "disengage", "Escape combat without penalty."),
        (4, 2): TileEffect("Shadowstep", "trait", "stealth_movement", "Move through enemies undetected."),
        (0, 0): TileEffect("Assassin Capstone", "trait", "crit_kill", "Critical hits instantly KO low-HP enemies."),
        (4, 4): TileEffect("Recon Master Capstone", "trait", "map_reveal", "Reveal enemy positions at battle start."),
    }

