Developer Guide
=========================

So you want to contribute to Not Quite Paradise2? Huzzah! Any support is welcome and **greatly** appreciated!

Tools Used
-------------------
The following tools are used as standard to ensure a consistent and reliable codebase.

* `black <https://black.readthedocs.io/en/stable/>`_ - an opinionated `linter <https://en.wikipedia.org/wiki/Lint_(software)>`_.
* `isort <https://pycqa.github.io/isort/>`_ - manage the order of imports.

When you submit a pull request the CI, Github Actions, will run black and isort automatically.


Style Guide
----------------

General
^^^^^^^^^^
PEP8 compliant.
Make use of type hints, with a view to reintroducing MyPy in the future.

Naming
^^^^^^^^^^^^
* If checking a bool use IsA or HasA.
* If setting a variable from statically held data prefix with "load_[data]"
    * Where a variable name contains "name" the variable may include spaces and other special characters. Where it includes "key" it may contain alphanumeric values only.

Reporting
^^^^^^^^^^^
Functions that change state should confirm when they have done so, via the log.

Architecture Overview
---------------------------

Game is key
^^^^^^^^^^^^^^^^^^^
All of the functionality is channeled through ``Game``, with most classes having a reference to that class in order to access other aspects of the code base.

Core
^^^^^^^^^^^^^^
The core aspects of the engine are held in a series of classes stored in the aptly named ``/core`` directory. Each of these classes handle a critical element of the engine and their purposes are intended to overlap as little as possible.

Scenes
^^^^^^^^^^^^^^^^^^^^
In game interactions are handled via ``Scene`` s. Each ``Scene`` has a directory in the scene folder and is made up of 2 classes, ``Scene`` and ``UI``.

Scenes can be stacked on top of another and are rendered in the order in which they are added, those added earlier being rendered sooner.  Scenes also have a concept of input blocking, allowing input to flow onto scenes further down the stack, or not, as required.

Data
^^^^^^^^^^^^^^
Where possible, static data should be defined in external files. See :ref:`Game Config` for examples.


Contributing
---------------------

Forking
^^^^^^^^^^^^^^^

To get started, `fork the repository <https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/fork-a-repo>`_ and open it up in your favorite editor. Next, open your terminal and point it to where you just saved the NQP2 repository. If you want to use `poetry <https://python-poetry.org/>`_ you would then run::

    pip install poetry
    poetry install

This will install all of the dependencies needed, using poetry.

To run NQP2, navigate the terminal to the game directory and then use::

    python nqp2.py


If you're not sure where to start helping out you can look at the existing feature requests and issues, `here <https://github.com/Snayff/nqp2/issues>`_. Pick one you think you'd like to tackle and make the relevant changes to your fork.

Merging
^^^^^^^^^^^^^^^^^^^
When you're ready, submit a `pull request <https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request>`_ to have your changes added to the main repository. Any pull request must pass the checks in the Github Actions. The code must remain compatible with the building of the `Sphinx <https://www.sphinx-doc.org/en/master/>`_ documentation, so that the docs are always up to date.

Bug, Issues and Defects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you find any problems in the existing code you can raise a `new issue <https://github.com/Snayff/nqp2/issues/new?assignees=&labels=bug&template=bug_report.md&title=>`_ on Not Quite Paradise 2's GitHub page.


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
To open or close the developer console use the back tick ``````.

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

