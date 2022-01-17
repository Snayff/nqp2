Developer Notes
=========================

Commanders
-------------------

Adding New
^^^^^^^^^^^^^^^^^^^^^^^
To add a new commander you need to add 3 things:
1. a json with the commander's name in the ``data/commanders`` folder
2. a folder with the commander's name in the ``assets/commanders`` folder
3. 2 folders in the ``assets/commanders/[commander's name]`` folder; ``icon`` and ``move``.
    1. a 16x16 sprite in the ``icon`` folder.
    2. a set of 16x16 sprites, one for each sprite frame, in the ``move`` folder.

json Explained
^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: json

    {
        "type": "isla",  # str, used as an identifier. Must be the same as the json file name and the relevant asset folder.
        "name": "Isla",  # str, used as the display value of the commander in game
        "backstory": "Overthrowing...",  # str, story/setting
        "charisma": 7,  # int
        "leadership": 6,  # int
        "morale": 1,  # int
        "gold": 300,  # int
        "rations": 1,  # int
        "allies": [  # list of str, specifies which units and skills the commander has access to. Must match a listed ``home`` in the unit jsons.
            "castle",
            "fortress"
        ],
        "starting_units": [  # list of str, specifies what units the commander starts with. Must match a listed ``type`` in the unit jsons.
            "spearman",
            "spearman",
            "guerrilla_fighter",
            "skirmisher"
        ]
    }


json Example
^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: json

    {
        "type": "isla",
        "name": "Isla",
        "backstory": "Overthrowing the patriarchy is her only desire.",
        "charisma": 7,
        "leadership": 6,
        "morale": 1,
        "gold": 300,
        "rations": 1,
        "allies": [
            "castle",
            "fortress"
        ],
        "starting_units": [
            "spearman",
            "spearman",
            "guerrilla_fighter",
            "skirmisher"
        ]
    }


Directory Examples
^^^^^^^^^^^^^^^^^^^^^^^
Asset folder:

.. image:: https://i.imgur.com/H3Qb7yo.png

Data Folder:

.. image:: https://i.imgur.com/hGGHh87.png


Events
------------------

Adding New
^^^^^^^^^^^^^^^^
To add a new event you need to add only 1 thing:
1. a json with the event's name in the ``data/events`` folder

json Explained
^^^^^^^^^^^^^^^^^
.. code-block:: json

    {
        "type": "test",  # str, used as an identifier.
        "description": "this is happening.",  # str
        "conditions": [],  # work in progress!
        "level_available": 1,  # int, determines on what level the event can occur. Likely to be moved into conditions.
        "tier": 1,  # int, the rarity of the event. Tier 1 is most likely.
        "resources": [  # list of str, used to preload resources used within the event.
            "existing_unit:random1",  # str, resource key : resource instance identifier.
            ],
        "options": [  # list of dicts, used to offer options to the player.
            {
                "text": "this is the first choice",  # str, the flavour text shown to the player.
                "result": [  # list of strs, determines the results if picked.
                    "injury:2@random1"  # str, result key : result value @ target. The @ and target are only required for some result key's.
                ],
                "displayed_result": "+injury"  # str, information given to the player about the outcome of the decision.
            }
        ]
    }



Parameters
^^^^^^^^^^^^^^^^^

Conditions
""""""""""""""""

Syntax is key:value@target

.. list-table:: Title
   :widths: 50 50 50 100
   :header-rows: 1

   * - Key
     - Value
     - Target
     - Example
   * - ``flag``
     - [any]
     -
     - ``flag:camp_party_unlocked``


Resources
""""""""""""""""

Syntax is key:value

**Note: Value is used to specify an ID for the resource. Any str (except "@" and ":") can be given and then used in the rest of the event as an ID.**

.. list-table:: Title
   :widths: 50 50 50 50 100
   :header-rows: 1

   * - Key
     - Value
     - Qualifier
     - Example
     - Additional Notes
   * - ``existing_unit``
     - [str]
     -
     - ``existing_unit:resource_1
     - Creates a resource for a random, existing unit.
   * - ``new_specific_unit``
     - [str]
     - [unit_type]
     - ``new_specific_unit:new_unit@pikeman``
     - Creates a resource for a new unit of the specified unit type.
   * - ``new_random_unit``
     - [str]
     - Optional[tier]
     - ``new_random_unit:randomunit@1``
     - Creates a resource for a new random unit from the player's allies, within the given tier. If no tier is specified then all tiers are used.



Results
"""""""""""""""""""""

Syntax is key:value@target

.. list-table:: Title
   :widths: 50 50 50 50 50
   :header-rows: 1

   * - Key
     - Value
     - Target
     - Example
     - Additional Notes
   * - ``gold``
     - [int]
     -
     - ``gold:10``
     -
   * - ``rations``
     - [int]
     -
     - ``rations:10``
     -
   * - ``morale``
     - [int]
     -
     - ``morale:10``
     -
  * - ``charisma``
     - [int]
     -
     - ``charisma:10``
     -
  * - ``leadership``
     - [int]
     -
     - ``leadership:10``
     -
  * - ``injury``
     - [int]
     - [resource_id]
     - ``injury:1@resource_1``
     -
  * - ``unlock_event``
     - [event_type]
     -
     - ``unlock_event:camp_party``
     -  This adds the given event to the list of prioritised events and adds a flag ``[event_type]_unlocked``.
  * - ``add_unit_resource``
     - [resource_id]
     -
     - ``random_unit:resource_1``
     - Resource specified must be a new unit.
  * - ``add_specific_unit``
     - [unit_type]
     -
     - ``specific_unit:pikeman``
     -


json Example
^^^^^^^^^^^^^^^^^
.. code-block:: json

    {
        "type": "test",
        "description": "this is what will show and will describe what is happening.",
        "conditions": [],
        "level_available": 1,
        "tier": 1,
        "resources": [
            "existing_unit:random1",
            "existing_unit:random2"
            ],
        "options": [
            {
                "text": "this is the first choice",
                "result": [
                    "injury:2@random1"
                ],
                "displayed_result": "+injury"
            },
            {
                "text": "this is the second choice",
                "result": [
                    "gold:-10"
                ],
                "displayed_result": "-gold"
            },
            {
                "text": "this is the third choice",
                "result": [
                    "gold:100"
                    ],
                "displayed_result": "+gold"
            }
        ]
    }


Game Config
--------------------
Many of the values used throughout NQP2 are held in external data files. Those that relate to how the game functions are held in ``config.json``.

Config Explained
^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: json

    {
        "unit_tier_occur_rates": {
            "1": 100, # the weight ascribed to a tier 1 unit when generating
            "2": 50,  # the weight for a tier 2 unit...
            "3": 25,
            "4": 1
        },
        "event_tier_occur_rates": {
            "1": 100,  # the weight of a tier 1 event when generating
            "2": 75,  # the weight of a tier 2 event...
            "3": 50,
            "4": 25
        },
        "combat_tier_occur_rates": {
            "1": 100,  # the weight of a tier 1 combat when generating
            "2": 75,  # the weight of a tier 2 combat...
            "3": 50,
            "4": 25
        },
        "unit_base_values": {
            "tier_1": {  # base values used for tier 1 units
                "health": 0,
                "defence": 0,
                "attack": 0,
                "range": 0,
                "attack_speed": 0,
                "move_speed": 0,
                "ammo": 0,
                "count": 0,
                "size": 0,
                "weight": 0,
                "gold_cost": 0
            },
            "tier_2": {  # base values used for tier 2 units
                "health": 0,
                "defence": 0,
                "attack": 0,
                "range": 0,
                "attack_speed": 0,
                "move_speed": 0,
                "ammo": 0,
                "count": 0,
                "size": 0,
                "weight": 0,
                "gold_cost": 0
            },
            "tier_3": {  # base values used for tier 3 units
                "health": 0,
                "defence": 0,
                "attack": 0,
                "range": 0,
                "attack_speed": 0,
                "move_speed": 0,
                "ammo": 0,
                "count": 0,
                "size": 0,
                "weight": 0,
                "gold_cost": 0
            },
            "tier_4": {  # base values used for tier 4 units
                "health": 0,
                "defence": 0,
                "attack": 0,
                "range": 0,
                "attack_speed": 0,
                "move_speed": 0,
                "ammo": 0,
                "count": 0,
                "size": 0,
                "weight": 0,
                "gold_cost": 0
            }
        },
        "starting_values": {  # starting values of different resources
            "gold": 0,
            "rations": 0,
            "morale": 0,
            "charisma": 0,
            "leadership": 0
        },
        "upgrade": {
            "tier_cost_multiplier": 1.2,  # the multiplier applied to the upgrade cost. Only applies to tiers > 1. (tier * tier_cost_multiplier) * cost
            "cost":25  # the base cost of an upgrade
        },
        "overworld": {
            "node_weights": {  # the weight assigned to each node during generation.
                "combat": 0.5,
                "event": 0.2,
                "inn": 0.1,
                "training": 0.1,
                "unknown": 0.2
            }
        },
        "post_combat": {
            "gold_min": 10,  # minimum gold given as reward post combat
            "gold_max": 50,  # maximum gold given
            "gold_level_multiplier": 1.1  # the multiplier applied to the gold rewards. Only applied post level 1. (level * gold_level_multiplier) * gold_min (and gold_max)
        }
    }


Developer Console
--------------------------
To open or close the developer console use the back tick `.

Commands
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table:: Title
   :widths: 50 50 100
   :header-rows: 1

   * - Syntax
     - Example
     - Additional Notes
   * - event [event_type]
     - ``event camp_party``
     - Load specified event.
   * - godmode
     - ``godmode``
     - Toggles godmode where player units take no damage and deal increased damage.
   * - create_unit_jsons
     - ``create_unit_jsons``
     - A template json is created for each unit, based on the folder names in the asset folder.
   * - gallery
     - ``gallery``
     - Load the unit gallery.
   * - data_editor
     - ``data_editor``
     - Load the data editor.
   * - load_unit_csv
     - ``load_unit_csv ``
     - Load a csv named ``units.csv`` into the unit's json files, or creates new ones as appropriate. Does not handle ``size``, ``weight``, ``gold_cost``, ``default_behaviour`` or ``type``.
   * - combat_result [result]
     - ``combat_result win``
     - Expects "win" or "lose". Instantly ends the current combat with the given result.

