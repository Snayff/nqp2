Effects
============================================

..  toctree::

    add_item
    attribute_modifier
    sildreths_signature
    stats_effect


Using Effects
^^^^^^^^^^^^^^^
Effects are defined in data files and then built during play. As the state cannot be known ahead of time we must account
for this "unknowability".

.. note::
    See the Adding New Content section for the data schema.

At a high level, there are a few parts:

* *Effect components, which track the changes to a stats object
* *EffectSentinel components, which can find the right targets for stats using the data from yaml
* Stat/Attribute objects, which can have multiple modifiers against the base value

Let's take a specific example, the `StatEffect`.
StatEffects will add themselves and a modifier function to a Stat object.  Whenever the value of a Stat object
is queried (stat.value), the `base_value` is computed against all modifiers. When a StatsEffect object is removed
from play, the modifier is also removed, lazily, the next time the Stat value is computed.
StatsEffectSentinels bridge the gap between the YAML and the game, and are a sort of simple query language, for
matching stats in the YAML to game entities in play.

Creating the effect looks like this:

.. code-block:: python
    from nqp.effects.stats_effect import apply_effects, new_stats_effect

    # apply a modifier without yaml
    # `stats` is the Stats component for the game entity in the ecs

    entity_id = new_stats_effect(
        stat=stats.attack_speed,
        stats=stats,
        modifier="50%",
    )

    # for an aoe buff, you could get a list of nearby entities and apply, then remove when the distance is too great
    # can be deleted, and the stat will revert
    snecs.schedule_for_deletion(entity_id)

And when creating a new entity it should look like this:

.. code-block:: python
    # when a new game entity is added to play, call `apply_effects` to search for and apply the correct effects
    from nqp.effects.stats_effect import apply_effects

    entity_id = make_new_game_entity(..., ...)
    apply_effects([entity_id])

A Word on EffectSentinels
""""""""""""""""""""""""""""""""
The Sentinels are regular ecs components, and if removed from the ecs, will no longer apply effects to new game
entities.

Sentinels are not required if an *`Effect` is applied directly, only if we want to use the Sentinel to apply the effect
when required.