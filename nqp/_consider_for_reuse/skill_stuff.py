from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

__all__ = []

##################################################
# EFFECTS
# the building blocks for skills and afflictions
####################################################
class Effect(ABC):
    """
    A collection of parameters and instructions to apply a change to an entity's or tile's state.
    """

    def __init__(
        self,
        origin: EntityID,
        target: EntityID,
        success_effects: List[Effect],
        failure_effects: List[Effect],
        potency: float = 1.0,
    ):
        self.origin = origin
        self.target = target
        self.success_effects: List[Effect] = success_effects
        self.failure_effects: List[Effect] = failure_effects
        self.potency: float = potency

    @abstractmethod
    def evaluate(self):
        """
        Evaluate the effect, triggering more if needed. Must be overridden by subclass
        """
        pass


class AftershockEffect(Effect):
    def __init__(
        self,
        origin: EntityID,
        target: EntityID,
        success_effects: List[Effect],
        failure_effects: List[Effect],
    ):
        super().__init__(origin, target, success_effects, failure_effects)

    def evaluate(self) -> Tuple[bool, List[Effect]]:
        center_position = scripts.engine.core.matter.get_entitys_component(self.target, Position)
        affected_tiles = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        entities_hit = []
        for tile in affected_tiles:
            target_tile_pos = (tile[0] + center_position.x, tile[1] + center_position.y)
            target_tile = world.get_tile(target_tile_pos)
            if world.tile_has_tag(self.origin, target_tile, TileTag.ACTOR):
                entities_hit += scripts.engine.core.matter.get_entities_on_tile(target_tile)
        for entity in entities_hit:
            damage_effect = DamageEffect(
                origin=self.origin,
                success_effects=[],
                failure_effects=[],
                target=entity,
                stat_to_target=PrimaryStat.VIGOUR,
                accuracy=library.GAME_CONFIG.base_values.accuracy,
                damage=int(library.GAME_CONFIG.base_values.damage * self.potency),
                damage_type=DamageType.MUNDANE,
                mod_stat=PrimaryStat.CLOUT,
                mod_amount=0.1,
            )
            self.success_effects.append(damage_effect)

        return True, self.success_effects


class DamageEffect(Effect):
    def __init__(
        self,
        origin: EntityID,
        target: EntityID,
        success_effects: List[Effect],
        failure_effects: List[Effect],
        stat_to_target: PrimaryStatType,
        accuracy: int,
        damage: int,
        damage_type: DamageTypeType,
        mod_stat: PrimaryStatType,
        mod_amount: float,
        potency: float = 1.0,
    ):

        super().__init__(origin, target, success_effects, failure_effects, potency)

        self.accuracy = accuracy
        self.stat_to_target = stat_to_target
        self.damage = damage
        self.damage_type = damage_type
        self.mod_amount = mod_amount
        self.mod_stat = mod_stat
        self.hit_type_effects: Dict[HitTypeType, List[Effect]] = {HitType.HIT: [], HitType.GRAZE: [], HitType.CRIT: []}
        self.force_hit_type: Optional[HitTypeType] = None

    def evaluate(self) -> Tuple[bool, List[Effect]]:
        """
        Resolve the damage effect and return the conditional effects based on if the damage is greater than 0.
        """
        logging.debug("Evaluating Damage Effect...")
        if self.damage <= 0:
            logging.info(f"Damage given to DamageEffect is {self.damage} and was therefore not executed.")
            return False, self.failure_effects

        elif not scripts.engine.core.matter.entity_has_component(self.target, Resources):
            logging.info(f"Target doesnt have resources so damage cannot be applied.")
            return False, self.failure_effects

        elif not scripts.engine.core.matter.entity_has_component(self.target, CombatStats):
            logging.warning(f"Target doesnt have combatstats so damage cannot be calculated.")
            return False, self.failure_effects

        elif not scripts.engine.core.matter.entity_has_component(self.origin, CombatStats):
            logging.warning(f"Attacker doesnt have combatstats so damage cannot be calculated.")
            return False, self.failure_effects

        # get combat stats
        defenders_stats = scripts.engine.core.matter.get_entitys_component(self.target, CombatStats)
        attackers_stats = scripts.engine.core.matter.get_entitys_component(self.origin, CombatStats)

        # get hit type
        stat_to_target_value = getattr(defenders_stats, self.stat_to_target.lower())
        to_hit_score = scripts.engine.core.matter.calculate_to_hit_score(
            attackers_stats.accuracy, self.accuracy, stat_to_target_value
        )
        if self.force_hit_type:
            hit_type = self.force_hit_type
        else:
            hit_type = scripts.engine.core.matter.get_hit_type(to_hit_score)

        # calculate damage
        resist_value = getattr(defenders_stats, "resist_" + self.damage_type.lower())
        mod_value = getattr(attackers_stats, self.mod_stat.lower())
        damage = scripts.engine.core.matter.calculate_damage(self.damage, mod_value, resist_value, hit_type)

        # apply the damage
        if scripts.engine.core.matter.apply_damage(self.target, damage):
            # add effects relevant to the hit type to the stack
            self.success_effects += self.hit_type_effects[hit_type]

            defenders_resources = scripts.engine.core.matter.get_entitys_component(self.target, Resources)

            # post interaction event
            event = DamageEvent(
                origin=self.origin,
                target=self.target,
                amount=damage,
                damage_type=self.damage_type,
                remaining_hp=defenders_resources.health,
            )
            event_hub.post(event)

            # check if target is dead
            if damage >= defenders_resources.health:
                scripts.engine.core.matter.kill_entity(self.target)

            return True, self.success_effects
        else:
            return False, self.failure_effects


class MoveSelfEffect(Effect):
    def __init__(
        self,
        origin: EntityID,
        target: EntityID,
        success_effects: List[Effect],
        failure_effects: List[Effect],
        direction: DirectionType,
        move_amount: int,
    ):

        super().__init__(origin, target, success_effects, failure_effects)

        self.direction = direction
        self.move_amount = move_amount

    def evaluate(self) -> Tuple[bool, List[Effect]]:
        """
        Resolve the move effect and return the conditional effects based on if the target moved the full amount.
        """
        logging.debug("Evaluating Move Self Effect...")

        entity = self.target
        success = False

        # confirm targeting self
        if self.origin != entity:
            logging.debug(
                f"Failed to move {scripts.engine.core.matter.get_name(entity)} as they are not the originator."
            )
            return False, self.failure_effects

        # check target has position
        if not scripts.engine.core.matter.entity_has_component(entity, Position):
            logging.debug(f"Failed to move {scripts.engine.core.matter.get_name(entity)} as they have no Position.")
            return False, self.failure_effects

        dir_x, dir_y = self.direction
        pos = scripts.engine.core.matter.get_entitys_component(entity, Position)

        # loop each target tile in turn
        for _ in range(0, self.move_amount):
            new_x = pos.x + dir_x
            new_y = pos.y + dir_y
            blocked = world.is_direction_blocked(entity, dir_x, dir_y)
            success = not blocked

            if not blocked:
                # named _position as typing was inferring from position above
                _position = scripts.engine.core.matter.get_entitys_component(entity, Position)

                # update position
                if _position:
                    logging.debug(
                        f"->'{scripts.engine.core.matter.get_name(self.target)}' moved from ({pos.x},{pos.y}) to ({new_x},"
                        f"{new_y})."
                    )
                    _position.set(new_x, new_y)

                    # post interaction event
                    event = MoveEvent(
                        origin=self.origin, target=self.target, direction=self.direction, new_pos=(new_x, new_y)
                    )
                    event_hub.post(event)

                    success = True

        if success:
            return True, self.success_effects
        else:
            return False, self.failure_effects


class MoveOtherEffect(Effect):
    def __init__(
        self,
        origin: EntityID,
        target: EntityID,
        success_effects: List[Effect],
        failure_effects: List[Effect],
        direction: DirectionType,
        move_amount: int,
    ):

        super().__init__(origin, target, success_effects, failure_effects)

        self.direction = direction
        self.move_amount = move_amount

    def evaluate(self) -> Tuple[bool, List[Effect]]:
        """
        Resolve the move effect and return the conditional effects based on if the target moved the full amount.
        """
        logging.debug("Evaluating Move Other Effect...")

        success = False
        entity = self.target

        # confirm not targeting self
        if self.origin == entity:
            logging.debug(f"Failed to move {scripts.engine.core.matter.get_name(entity)} as they are the originator.")
            return False, self.failure_effects

        # check target has position
        if not scripts.engine.core.matter.entity_has_component(entity, Position):
            logging.debug(f"Failed to move {scripts.engine.core.matter.get_name(entity)} as they have no Position.")
            return False, self.failure_effects

        pos = scripts.engine.core.matter.get_entitys_component(entity, Position)
        dir_x, dir_y = self.direction

        # loop each target tile in turn
        for _ in range(0, self.move_amount):
            new_x = pos.x + dir_x
            new_y = pos.y + dir_y
            blocked = world.is_direction_blocked(entity, dir_x, dir_y)
            success = not blocked

            if not blocked:
                # named _position as typing was inferring from position above
                _position = scripts.engine.core.matter.get_entitys_component(entity, Position)

                # update position
                if _position:
                    logging.debug(
                        f"->'{scripts.engine.core.matter.get_name(self.target)}' moved from ({pos.x},{pos.y}) to ({new_x},"
                        f"{new_y})."
                    )
                    _position.set(new_x, new_y)

                    # post interaction event
                    event = MoveEvent(
                        origin=self.origin, target=self.target, direction=self.direction, new_pos=(new_x, new_y)
                    )
                    event_hub.post(event)

                    success = True

        if success:
            return True, self.success_effects
        else:
            return False, self.failure_effects


class AffectStatEffect(Effect):
    def __init__(
        self,
        origin: EntityID,
        target: EntityID,
        success_effects: List[Effect],
        failure_effects: List[Effect],
        cause_name: str,
        stat_to_target: PrimaryStatType,
        affect_amount: int,
    ):

        super().__init__(origin, target, success_effects, failure_effects)

        self.stat_to_target = stat_to_target
        self.affect_amount = affect_amount
        self.cause_name = cause_name

    def evaluate(self) -> Tuple[bool, List[Effect]]:
        """
        Log the affliction and the stat modification in the Affliction component.
        """
        logging.debug("Evaluating Affect Stat Effect...")
        success = False
        stats = scripts.engine.core.matter.get_entitys_component(self.target, CombatStats)

        # if successfully  applied
        if stats.add_mod(self.stat_to_target, self.cause_name, self.affect_amount):

            # post interaction event
            event = AffectStatEvent(
                origin=self.origin,
                target=self.target,
                stat_to_target=self.stat_to_target,
                amount=self.affect_amount,
            )
            event_hub.post(event)

            success = True

        if success:
            return True, self.success_effects
        else:
            return False, self.failure_effects


class ApplyAfflictionEffect(Effect):
    def __init__(
        self,
        origin: EntityID,
        target: EntityID,
        success_effects: List[Effect],
        failure_effects: List[Effect],
        affliction_name: str,
        duration: int,
    ):
        super().__init__(origin, target, success_effects, failure_effects)

        self.affliction_name = affliction_name
        self.duration = duration

    def evaluate(self) -> Tuple[bool, List[Effect]]:
        """
        Applies an affliction to an entity
        """
        logging.debug("Evaluating Apply Affliction Effect...")
        affliction_name = self.affliction_name
        origin = self.origin
        target = self.target
        duration = self.duration

        affliction_instance = scripts.engine.core.matter.create_affliction(affliction_name, origin, target, duration)

        # check for immunities
        if scripts.engine.core.matter.entity_has_immunity(target, affliction_name):
            logging.debug(
                f"'{scripts.engine.core.matter.get_name(self.origin)}' failed to apply {affliction_name} to  "
                f"'{scripts.engine.core.matter.get_name(self.target)}' as they are immune."
            )
            return False, self.failure_effects

        # add the affliction to the afflictions component
        if scripts.engine.core.matter.entity_has_component(target, Afflictions):
            afflictions = scripts.engine.core.matter.get_entitys_component(target, Afflictions)
            afflictions.add(affliction_instance)
            scripts.engine.core.matter.apply_affliction(affliction_instance)

            # add immunities to prevent further applications for the duration
            scripts.engine.core.matter.add_immunity(target, affliction_name, duration + 2)

            # post interaction event
            event = AfflictionEvent(
                origin=origin,
                target=target,
                affliction_name=affliction_name,
            )
            event_hub.post(event)

            return True, self.success_effects

        # didn't have the component, fail
        return False, self.failure_effects


class AffectCooldownEffect(Effect):
    def __init__(
        self,
        origin: EntityID,
        target: EntityID,
        success_effects: List[Effect],
        failure_effects: List[Effect],
        skill_name: str,
        affect_amount: int,
    ):
        super().__init__(origin, target, success_effects, failure_effects)

        self.skill_name = skill_name
        self.affect_amount = affect_amount

    def evaluate(self) -> Tuple[bool, List[Effect]]:
        """
        Reduces the cooldown of a skill of an entity
        """
        logging.debug("Evaluating Reduce Skill Cooldown Effect...")

        knowledge = scripts.engine.core.matter.get_entitys_component(self.target, Knowledge)

        if knowledge:
            current_cooldown = knowledge.cooldowns[self.skill_name]
            knowledge.set_skill_cooldown(self.skill_name, current_cooldown - self.affect_amount)

            # post interaction event
            event = AffectCooldownEvent(
                origin=self.origin,
                target=self.target,
                amount=self.affect_amount,
            )
            event_hub.post(event)

            logging.debug(
                f"Reduced cooldown of skill '{self.skill_name}' from {current_cooldown} to "
                f"{knowledge.cooldowns[self.skill_name]}"
            )
            return True, self.success_effects

        return False, self.failure_effects


############################################################
# AFFLICTIONS
# These were status effects
############################################################

##########
# json Data
###########
{
    "BoggedDown": {
        "__dataclass__": "AfflictionData",
        "category": "bane",
        "description": "It weakens mundane defence and makes you a little bit slower.",
        "icon_path": "skills/root.png",
        "name": "bogged down",
        "identity_tags": ["affect_stat"],
        "triggers": ["movement"],
    },
    "Flaming": {
        "__dataclass__": "AfflictionData",
        "category": "bane",
        "description": "It does damage.",
        "icon_path": "skills/torch.png",
        "name": "flaming",
        "identity_tags": ["damage"],
        "triggers": ["movement"],
    },
}

############
# base classes
#############
class Action(ABC):
    """
    Action taken during the game. A container for Effects.
    """

    # details to be overwritten by external data
    name: str  # name of the class
    description: str
    icon_path: str

    # details to be overwritten in subclass
    target_tags: List[TileTagType]
    shape: ShapeType
    shape_size: int

    # set by instance
    effects: List[Effect]

    @abstractmethod
    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[Effect]:
        """
        Build the effects of this skill applying to a single entity. Must be overridden in subclass.
        """
        pass


class Affliction(Action):
    """
    A subclass of Affliction represents an affliction (a semi-permanent modifier) and holds all the data that is
    not dependent on the individual instances -  stuff like applicable targets etc.

    An instance of Affliction represents an individual application of that affliction,
    and holds only the data that is tied to the individual use - stuff like
    the user and target.
    """

    # to be overwritten in subclass, including being set by external data
    identity_tags: List[EffectTypeType]
    triggers: List[ReactionTriggerType]
    category: AfflictionCategoryType

    def __init__(self, origin: EntityID, affected_entity: EntityID, duration: int):
        self.origin = origin
        self.affected_entity = affected_entity
        self.duration = duration

    @abstractmethod
    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[Effect]:
        """
        Build the effects of this skill applying to a single entity. Must be overridden in subclass.
        """
        pass

    @classmethod
    def _init_properties(cls):
        """
        Sets the class properties of the affliction from the class key
        """
        from nqp.engine.internal import library

        cls.data = library.AFFLICTIONS[cls.__name__]
        cls.name = cls.__name__
        cls.description = cls.data.description
        cls.icon_path = cls.data.icon_path
        cls.category = cls.data.category
        cls.identity_tags = cls.data.identity_tags
        cls.triggers = cls.data.triggers

    def apply(self) -> Iterator[Tuple[EntityID, List[Effect]]]:
        """
        Apply the affliction to the affected entity.
        An iterator over pairs of (affected entity, [effects]). Use affected entity position.  Applies to each
        entity only once.
        """
        from nqp.engine.core import world

        entity_names = []
        entities = set()
        position = matter.get_entitys_component(self.affected_entity, Position)

        for coordinate in position.coordinates:
            for entity in matter.get_affected_entities(coordinate, self.shape, self.shape_size):
                if entity not in entities:
                    entities.add(entity)
                    yield entity, self._build_effects(entity)
                    entity_names.append(matter.get_name(entity))

    def trigger(self):
        """
        Trigger the affliction on the affected entity
        """
        yield self.affected_entity, self._build_effects(self.affected_entity)


################
# affliction classes
################
class BoggedDown(Affliction):

    # targeting
    target_tags: List[TileTagType] = [TileTag.OTHER_ENTITY]
    shape: ShapeType = Shape.TARGET
    shape_size: int = 1

    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[AffectStatEffect]:  # type: ignore

        affect_stat_effect = AffectStatEffect(
            origin=self.origin,
            cause_name=self.name,
            success_effects=[],
            failure_effects=[],
            target=self.affected_entity,
            stat_to_target=PrimaryStat.BUSTLE,
            affect_amount=2,
        )

        return [affect_stat_effect]


class Flaming(Affliction):

    # targeting
    target_tags: List[TileTagType] = [TileTag.OTHER_ENTITY]
    shape: ShapeType = Shape.TARGET
    shape_size: int = 1

    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[DamageEffect]:  # type: ignore
        """
        Build the effects of this skill applying to a single entity.
        """
        damage_effect = DamageEffect(
            origin=self.origin,
            success_effects=[],
            failure_effects=[],
            target=entity,
            stat_to_target=PrimaryStat.BUSTLE,
            accuracy=library.GAME_CONFIG.base_values.accuracy,
            damage=int(library.GAME_CONFIG.base_values.damage / 2),
            damage_type=DamageType.BURN,
            mod_stat=PrimaryStat.SKULLDUGGERY,
            mod_amount=0.1,
        )

        return [damage_effect]


############################################################
# SKILLS
# These were the active skills
############################################################

# json data
{
    "Move": {
        "__dataclass__": "SkillData",
        "cooldown": 0,
        "description": "This is normal movement",
        "icon_path": "skills/basic_attack.png",
        "name": "move",
        "resource_cost": 0,
        "resource_type": "stamina",
        "types": ["all", "self"],
        "time_cost": 20,
    },
    "BasicAttack": {
        "__dataclass__": "SkillData",
        "cooldown": 1,
        "description": "A simple attack.",
        "icon_path": "skills/basic_attack.png",
        "name": "basic attack",
        "resource_cost": 10,
        "resource_type": "stamina",
        "types": ["all", "attack"],
        "time_cost": 20,
    },
    "Lunge": {
        "__dataclass__": "SkillData",
        "cooldown": 4,
        "description": "Launch forwards and hit the enemy in your way.",
        "icon_path": "skills/lunge.png",
        "name": "lunge",
        "resource_cost": 15,
        "resource_type": "stamina",
        "types": ["all", "attack"],
        "time_cost": 30,
    },
}

############
# base classes
#############
class Action(ABC):
    """
    Action taken during the game. A container for Effects.
    """

    # details to be overwritten by external data
    name: str  # name of the class
    description: str
    icon_path: str

    # details to be overwritten in subclass
    target_tags: List[TileTagType]
    shape: ShapeType
    shape_size: int

    # set by instance
    effects: List[Effect]

    @abstractmethod
    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[Effect]:
        """
        Build the effects of this skill applying to a single entity. Must be overridden in subclass.
        """
        pass


class Skill(Action):
    """
    A subclass of Skill represents a skill and holds all the data that is
    not dependent on the individual cast - stuff like shape, base accuracy, etc.

    An instance of Skill represents an individual use of that skill,
    and additionally holds only the data that is tied to the individual use - stuff like
    the user and target.
    """

    # core data, to be overwritten by external data
    resource_type: ResourceType
    resource_cost: int
    time_cost: int
    base_cooldown: int

    # targeting details, to be overwritten in subclass
    targeting_method: TargetingMethodType  # Tile, Direction, Auto
    cast_tags: List[TileTagType]
    target_directions: List[DirectionType]  # needed for Direction
    range: int  # needed for Tile, Auto

    # delivery methods, to be overwritten in subclass
    uses_projectile: bool  # usable by for Tile, Direction, Auto
    projectile_data: Optional[ProjectileData]
    is_delayed: bool  # usable by Tile, Auto  - Doesnt make sense for Direction to have a delayed cast.
    delayed_skill_data: Optional[DelayedSkillData]

    # blessing related attributes
    blessings: List[SkillModifier]
    types: List[str]

    def __init__(self, user: EntityID, target_tile: Tile, direction: DirectionType):
        self.user: EntityID = user
        self.target_tile: Tile = target_tile
        self.direction: DirectionType = direction
        self.projectile: Optional[EntityID] = None
        self.delayed_skill: Optional[EntityID] = None

        # vars needed to keep track of changes
        self.ignore_entities: List[EntityID] = []  # to ensure entity not hit more than once

        self.inactive_effects: List[str] = []

    def _post_build_effects(self, entity: EntityID, potency: float = 1.0, skill_stack=None) -> List[Effect]:
        """
        Build the effects of this skill applying to a single entity. This function will be used to apply any dynamic tweaks to the effects stack after the subclass generates its stack.
        """
        # handle mutable default
        if skill_stack is None:
            skill_stack = []
        skill_blessings = matter.get_entitys_component(self.user, Knowledge).skill_blessings
        relevant_blessings: List[SkillModifier] = []
        if self.__class__.__name__ in skill_blessings:
            relevant_blessings = skill_blessings[self.__class__.__name__]
        for blessing in relevant_blessings:
            blessing.apply(self.user)
        return skill_stack

    @classmethod
    def _init_properties(cls):
        """
        Sets the class properties of the skill from the class key
        """
        from nqp.engine.internal import library

        cls.data = library.SKILLS[cls.__name__]
        cls.name = cls.__name__
        cls.description = cls.data.description
        cls.base_cooldown = cls.data.cooldown
        cls.time_cost = cls.data.time_cost
        cls.icon_path = cls.data.icon_path
        cls.resource_type = cls.data.resource_type
        cls.resource_cost = cls.data.resource_cost
        cls.types = cls.data.types

    def apply(self) -> Iterator[Tuple[EntityID, List[Effect]]]:
        """
        An iterator over pairs of (affected entity, [effects]). Uses target tile. Can apply to an entity multiple
        times.
        """
        entity_names = []
        for entity in matter.get_affected_entities(
            (self.target_tile.x, self.target_tile.y), self.shape, self.shape_size, self.direction
        ):
            yield entity, [
                effect
                for effect in self._build_effects(entity)
                if effect.__class__.__name__ not in self.inactive_effects
            ]
            entity_names.append(matter.get_name(entity))

    def use(self) -> bool:
        """
        If uses_projectile then create a projectile to carry the skill effects. Otherwise call self.apply
        """
        logging.debug(f"'{matter.get_name(self.user)}' used '{self.__class__.__name__}'.")

        # handle the delivery method of the skill
        if self.uses_projectile:
            self._create_projectile()
            is_successful = True
        elif self.is_delayed:
            self._create_delayed_skill()
            is_successful = True
        else:
            is_successful = matter.apply_skill(self)

        if is_successful:
            # post interaction event
            event = UseSkillEvent(origin=self.user, skill_name=self.__class__.__name__)
            event_hub.post(event)

        return is_successful

    def _create_projectile(self):
        """
        Create a projectile carrying the skill's effects
        """
        projectile_data = self.projectile_data

        # update projectile instance values
        projectile_data.creator = self.user
        projectile_data.skill_name = self.name
        projectile_data.skill_instance = self
        projectile_data.direction = self.direction

        # create the projectile
        projectile = matter.create_projectile(self.user, (self.target_tile.x, self.target_tile.y), projectile_data)

        # add projectile to ignore list
        self.ignore_entities.append(projectile)

        # save the reference to the projectile entity
        self.projectile = projectile

    def _create_delayed_skill(self):
        delayed_skill_data = self.delayed_skill_data

        # update delayed skill instance values
        delayed_skill_data.creator = self.user
        delayed_skill_data.skill_name = self.name
        delayed_skill_data.skill_instance = self

        # create the delayed skill
        delayed_skill = matter.create_delayed_skill(
            self.user, (self.target_tile.x, self.target_tile.y), delayed_skill_data
        )

        # add to ignore list
        self.ignore_entities.append(delayed_skill)

        # save reference
        self.delayed_skill = delayed_skill

    @abstractmethod
    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[Effect]:
        """
        Build the effects of this skill applying to a single entity. Must be overridden in subclass.
        """
        pass


###############
# skill classes
##############
class Move(Skill):
    """
    Basic move for an entity.
    """

    # casting
    cast_tags: List[TileTagType] = [TileTag.NO_BLOCKING_TILE]

    # targeting
    range: int = 1
    target_tags: List[TileTagType] = [TileTag.SELF]
    targeting_method: TargetingMethodType = TargetingMethod.DIRECTION
    target_directions: List[DirectionType] = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
    shape: ShapeType = Shape.TARGET
    shape_size: int = 1

    # delivery
    uses_projectile: bool = False
    projectile_data: Optional[ProjectileData] = None
    is_delayed: bool = False
    delayed_skill_data: Optional[DelayedSkillData] = None

    def __init__(self, user: EntityID, target_tile: Tile, direction):
        """
        Move needs an init as it overrides the target tile
        """

        # override target
        position = scripts.engine.core.matter.get_entitys_component(user, Position)
        tile = world.get_tile((position.x, position.y))

        super().__init__(user, tile, direction)

    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[Effect]:  # type:ignore
        """
        Build the effects of this skill applying to a single entity.
        """
        move_effect = MoveSelfEffect(
            origin=self.user,
            target=entity,
            success_effects=[],
            failure_effects=[],
            direction=self.direction,
            move_amount=1,
        )

        return self._post_build_effects(entity, potency, [move_effect])


class BasicAttack(Skill):
    """
    Basic attack for an entity
    """

    # casting
    cast_tags: List[TileTagType] = [TileTag.ACTOR]

    # targeting
    range: int = 1
    target_tags: List[TileTagType] = [TileTag.ACTOR]
    targeting_method: TargetingMethodType = TargetingMethod.TILE
    target_directions: List[DirectionType] = [
        Direction.UP,
        Direction.DOWN,
        Direction.LEFT,
        Direction.RIGHT,
        Direction.UP_LEFT,
        Direction.UP_RIGHT,
        Direction.DOWN_LEFT,
        Direction.DOWN_RIGHT,
    ]
    shape: ShapeType = Shape.TARGET
    shape_size: int = 1

    # delivery
    uses_projectile: bool = False
    projectile_data: Optional[ProjectileData] = None
    is_delayed: bool = False
    delayed_skill_data: Optional[DelayedSkillData] = None

    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[Effect]:  # type:ignore
        """
        Build the effects of this skill applying to a single entity.
        """
        damage_effect = DamageEffect(
            origin=self.user,
            success_effects=[],
            failure_effects=[],
            target=entity,
            stat_to_target=PrimaryStat.VIGOUR,
            accuracy=library.GAME_CONFIG.base_values.accuracy,
            damage=int(library.GAME_CONFIG.base_values.damage * potency),
            damage_type=DamageType.MUNDANE,
            mod_stat=PrimaryStat.CLOUT,
            mod_amount=0.1,
        )

        return self._post_build_effects(entity, potency, [damage_effect])


class Lunge(Skill):
    """
    Lunge skill for an entity
    """

    # casting
    cast_tags: List[TileTagType] = [TileTag.ACTOR]

    # targeting
    range: int = 1
    target_tags: List[TileTagType] = [TileTag.ACTOR]
    targeting_method: TargetingMethodType = TargetingMethod.DIRECTION
    target_directions: List[DirectionType] = [
        Direction.UP,
        Direction.DOWN,
        Direction.LEFT,
        Direction.RIGHT,
        Direction.UP_LEFT,
        Direction.UP_RIGHT,
        Direction.DOWN_LEFT,
        Direction.DOWN_RIGHT,
    ]
    shape: ShapeType = Shape.TARGET
    shape_size: int = 1

    # delivery
    uses_projectile: bool = False
    projectile_data: Optional[ProjectileData] = None
    is_delayed: bool = False
    delayed_skill_data: Optional[DelayedSkillData] = None

    def __init__(self, user: EntityID, tile: Tile, direction: DirectionType):
        """
        Set the target tile as the current tile since we need to move.
        N.B. ignores provided tile.
        """
        position = scripts.engine.core.matter.get_entitys_component(user, Position)
        if position:
            _tile = world.get_tile((position.x, position.y))
        else:
            _tile = world.get_tile((0, 0))  # should always have position but just in case
        super().__init__(user, _tile, direction)
        self.move_amount = 2

    def _build_effects(self, entity: EntityID, potency: float = 1.0) -> List[Effect]:
        """
        Build the skill effects
        """
        # chain the effects conditionally

        cooldown_effect = self._build_cooldown_reduction_effect(entity=entity)
        damage_effect = self._build_damage_effect(success_effects=[cooldown_effect], potency=potency)
        move_effect = self._build_move_effect(entity=entity, success_effects=([damage_effect] if damage_effect else []))

        return [move_effect]

    def _build_move_effect(self, entity: EntityID, success_effects: List[Effect]) -> MoveSelfEffect:
        """
        Return the move effect for the lunge
        """
        move_effect = MoveSelfEffect(
            origin=self.user,
            target=entity,
            success_effects=success_effects,
            failure_effects=[],
            direction=self.direction,
            move_amount=self.move_amount,
        )
        return move_effect

    def _build_damage_effect(self, success_effects: List[Effect], potency: float = 1.0) -> Optional[DamageEffect]:
        """
        Return the damage effect for the lunge
        """
        target = self._find_target()
        damage_effect = None
        if target:
            damage_effect = DamageEffect(
                origin=self.user,
                success_effects=success_effects,
                failure_effects=[],
                target=target,
                stat_to_target=PrimaryStat.VIGOUR,
                accuracy=library.GAME_CONFIG.base_values.accuracy,
                damage=int(library.GAME_CONFIG.base_values.damage * potency),
                damage_type=DamageType.MUNDANE,
                mod_stat=PrimaryStat.CLOUT,
                mod_amount=0.1,
            )
        return damage_effect

    def _find_target(self) -> Optional[EntityID]:
        """
        Find the first entity that will be affected by the lunge
        """
        increment = (self.direction[0] * (self.move_amount + 1), self.direction[1] * (self.move_amount + 1))
        target_tile_pos = (self.target_tile.x + increment[0], self.target_tile.y + increment[1])
        entities = scripts.engine.core.matter.get_entities_on_tile(world.get_tile(target_tile_pos))

        if not entities:
            return None
        return entities[0]

    def _build_cooldown_reduction_effect(self, entity: EntityID) -> AffectCooldownEffect:
        """
        Returns an effect that executes the cooldown effect for the lunge
        """
        cooldown_effect = AffectCooldownEffect(
            origin=self.user,
            target=entity,
            skill_name=self.name,
            affect_amount=2,
            success_effects=[],
            failure_effects=[],
        )
        return cooldown_effect
