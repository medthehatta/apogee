import os
import random

from combat import perform_combat
from initiative import Initiative
from unit import Unit
from unit import Module
from unit import NormalDie
from unit import RiftDie
from util import short_id
from rect import Point
from rect import RectLRBT
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


def random_modules(num_modules, rng=None):
    rng = rng or random.Random()
    return [random_module(rng) for _ in range(num_modules)]


def module_to_pil(module):
    return svg_string_to_pil(svg_for_module(module))


def save_module_collage(modules, series=None):
    series = series or short_id()
    pils = [module_to_pil(mod) for mod in modules]

    for (i, img) in enumerate(pils):
        img.save(os.path.join(SCRATCH_PATH, f"mod-{series}-{i}.png"))

    return (pils, series)


if __name__ == "__main__":
    rect = RectLRBT.tlwh((5, 5), 10, 10)
