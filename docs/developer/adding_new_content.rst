Adding New Content
====================

Combat
-------------------

Adding New
^^^^^^^^^^^^^^^^^^^^^^^
To add a new commander you need to add 1 thing:
1. a yaml with the combat's name in the ``data/combat`` folder

yaml Explained
^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: yaml

    ---
    type: test_combat   # str, must match the file name
    category: basic     # str, "basic" or "boss"
    units:              # list of str. strs must match the unit type as per data/units
    - goblin
    - gremlin
    level_available: 1  # int, the level number at which the combat is available
    biome: plains       # str, the level in which the combat can occur
    tier: 1             # int, 1-4. How likely the combat is, with 1 being easiest.
    gold_reward:        # list of ints. Must contain only 1 values, indicating the lower and upper reward bounds.
    - 50
    - 110


yaml Example
^^^^^^^^^^^^^^^^^^^^^^^
Basic combat

.. code-block:: yaml

    ---
    type: test_combat
    category: basic
    units:
    - goblin
    - gremlin
    level_available: 1
    biome: plains
    tier: 1
    gold_reward:
    - 50
    - 110


Boss Combat

.. code-block:: yaml

    ---
    type: test_boss_combat
    category: boss
    units:
    - peasant_spearman
    - peasant_spearman
    - conscript_bowman
    level_available: 1
    tier: 1
    gold_reward:
    - 700
    - 900
    upgrades_for_scaling:
    - minor_attack
    - minor_defence
    boss_type: test_boss


Commanders
-------------------

Adding New
^^^^^^^^^^^^^^^^^^^^^^^
To add a new commander you need to add 3 things:
1. a yaml with the commander's name in the ``data/commanders`` folder
2. a folder with the commander's name in the ``assets/commanders`` folder
3. 2 folders in the ``assets/commanders/[commander's name]`` folder; ``icon`` and ``move``.
    1. a 16x16 sprite in the ``icon`` folder.
    2. a set of 16x16 sprites, one for each sprite frame, in the ``move`` folder.

yaml Explained
^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: yaml

    ---
    type: isla                  # str, used as an identifier. Must be the same as the yaml file name and the relevant asset folder.
    name: Isla                  # str, used as the display value of the commander in game
    backstory: Overthrowing...  # str, story/setting
    charisma: 7      # int
    leadership: 6    # int
    morale: 1        # int
    gold: 300        # int
    rations: 1       # int
    allies:          # list of str, specifies which units and skills the commander has access to. Must match a listed ``home`` in the unit data.
    - castle
    - fortress
    starting_units:  # list of str, specifies what units the commander starts with. Must match a listed ``type`` in the unit data.
    - spearman
    - spearman
    - guerrilla_fighter
    - skirmisher


yaml Example
^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: yaml

    ---
    type: isla
    name: Isla
    backstory: Overthrowing the patriarchy is her only desire.
    charisma: 7
    leadership: 6
    morale: 1
    gold: 300
    rations: 1
    allies:
    - castle
    - fortress
    starting_units:
    - spearman
    - spearman
    - guerrilla_fighter
    - skirmisher



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
1. a yaml with the event's name in the ``data/events`` folder

yaml Explained
^^^^^^^^^^^^^^^^^
.. code-block:: yaml

    ---
    type: test                        # str, used as an identifier.
    description: this is happening.   # str
    conditions: []                    # work in progress!
    level_available: 1                # int, determines on what level the event can occur. Likely to be moved into conditions.
    tier: 1                           # int, the rarity of the event. Tier 1 is most likely.
    resources:                        # list of str, used to preload resources used within the event.
    - existing_unit:random1           # str, resource key : resource instance identifier.
    image: image_name                 # str, must match name of an image, preferably in /event_images.
    options:                          # list of dicts, used to offer options to the player.
    - text: this is the first choice  # str, the flavour text shown to the player.
      result:                         # list of strs, determines the results if picked.
      - injury:2@random1              # str, result key : result value @ target. The @ and target are only required for some result key's.
      displayed_result: "+injury"     # str, information given to the player about the outcome of the decision.


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


yaml Example
^^^^^^^^^^^^^^^^^
.. code-block:: yaml

    ---
    type: test
    description: this is what will show and will describe what is happening.
    conditions: []
    level_available: 1
    tier: 1
    resources:
    - existing_unit:random1
    - existing_unit:random2
    image: axe
    options:
    - text: this is the first choice
      result:
      - injury:2@random1
      displayed_result: "+injury"
    - text: this is the second choice
      result:
      - gold:-10
      displayed_result: "-gold"
    - text: this is the third choice
      result:
      - gold:100
      displayed_result: "+gold"


Items and Traits
-------------------

Adding New
^^^^^^^^^^^^^^^^^^^^^^^
To add a new Item or Trait you need to add 1 thing:
1. a yaml with the items' or traits' name in their respective folder, i.e.  ``data/items`` or ``data/traits``

yaml Explained
^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: yaml

    ---
    name: Albrom's Signature Item
    is_signature: true
    effects:
      - name: StatsEffect  # name of the effect to use
        target: team  #  matched against Allegiance.team or unit
        unit_type: ranged  # is matched against Allegiance.unit.type
        attribute: attack # name of a stat on the Stats component
        modifier: 20%  # int, the amount to change by


yaml Example
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    ---
    name: Albrom's Signature Item
    is_signature: true
    effects:
      - name: StatsEffect
        target: team
        unit_type: ranged
        attribute: attack
        modifier: 20%

Parameters
^^^^^^^^^^^^

Name
""""""""""
.. list-table:: Title
   :widths: 50 50 50
   :header-rows: 1

   * - Key
     - Definition
     - Additional Notes
   * - ``StatsEffect``
     - Modify the Stats or Attributes of a Unit, or Resources of a Commander
     -

Target
""""""""""
.. list-table:: Title
   :widths: 50 50 50
   :header-rows: 1

   * - Key
     - Definition
     - Additional Notes
   * - all
     - Affects everyone
     - This means enemy and ally units/entities.
   * - team
     - Affects same team as affected unit/entities
     -
   * - unit
     - Affects the unit the affected entity/unit is in
     - Cannot be used is affected is commander
   * - self
     - Affects the affected only
     -

Unit Type
""""""""""

.. warning::
    This currently uses ranged/melee but elsewhere means the name of the unit.
    Needs to be clarified.

.. list-table:: Title
   :widths: 50 50 50
   :header-rows: 1

   * - Key
     - Definition
     - Additional Notes
   * -
     -
     -

Attribute
""""""""""

.. note::
    See `Stats` or `Attribute` component's attrs for options.

Modifier
""""""""""
.. list-table:: Title
   :widths: 50 50 50
   :header-rows: 1

   * - Key
     - Definition
     - Additional Notes
   * - [int]
     -
     - can be + (implied) or -.  Appending a percent will calculate the value from the base value of the stat


Trigger
""""""""""
.. list-table:: Title
   :widths: 50 50 50
   :header-rows: 1

   * - Key
     - Definition
     - Additional Notes
   * - OnAttacked
     - When Entity receives an attack
     -
   * - EnterNewRoom
     - When player moves to a new room
     -


Attack Type
""""""""""
.. list-table:: Title
   :widths: 50 50 50
   :header-rows: 1

   * - Key
     - Definition
     - Additional Notes
   * - ranged
     - A ranged Unit
     -
   * - melee
     - A Melee Unit
     -

State
""""""""""
.. list-table:: Title
   :widths: 50 50 50
   :header-rows: 1

   * - Key
     - Definition
     - Additional Notes
   * - true
     -
     -
   * - false
     -
     -