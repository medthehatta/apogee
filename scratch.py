import os
import random

from combat import perform_combat
from initiative import Initiative
from unit import Unit
from unit import Module
from unit import NormalDie
from unit import RiftDie
from util import short_id
from sample import random_unit
from sample import random_module
from svggen import svg_for_module
from svggen import svg_string_to_pil


#
# Scratch repo
#


SCRATCH_PATH = "scratch"
os.makedirs(SCRATCH_PATH, exist_ok=True)


#
# Functions
#


def setup_combat():
    seed = random.random()
    rng = random.Random(seed)
    ship = Unit(
        "ship",
        num_slots=5,
        modules=[
            Module(missile_dice=[NormalDie(1)]),
            Module(cannon_dice=[NormalDie(3), NormalDie(3)]),
            Module(hull_tank=5),
            Module(mitigation=1),
            Module(targeting=1),
        ],
    )

    opponent_names = ["adam", "betty", "charlie", "diane"]
    opponents = [random_unit(n, rng) for n in opponent_names]

    initiative = Initiative([ship] + opponents)
    for entry in initiative.one_round():
        print(entry)
        print(entry.stats)
        for m in entry.modules:
            print(m)
        print("")
    print("\n")

    return (rng, initiative)


def random_module_collage(num_modules, rng=None):
    rng = rng or random.Random()

    series = short_id()
    modules = []

    for i in range(num_modules):
        mod = random_module(rng)
        modules.append(mod)
        svg = svg_for_module(mod)
        img = svg_string_to_pil(svg)
        img.save(os.path.join(SCRATCH_PATH, f"mod-{series}-{i}.png"))

    return (modules, series)
