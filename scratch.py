import os
import random

import arcade

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

    for img in pils:
        img.save(os.path.join(SCRATCH_PATH, f"mod-{series}-{i}.png"))

    return (pils, series)


def render_module_collage(modules, num_columns=10, padding=2, margin=5):
    if not modules:
        raise ValueError("Must provide a nonempty list of modules")
    pils = [module_to_pil(mod) for mod in modules]
    pil_width = pils[0].width
    pil_height = pils[0].height
    basis_rect = (
        RectLRBT.tlwh((0, 0), pil_width, pil_height)
        .displace((margin, margin))
    )

    width = num_columns * (pil_width + padding) - padding + 2*margin
    num_rows = len(pils) // num_columns
    height = num_rows * (pil_height + padding) - padding + 2*margin

    arcade.open_window(width, height, "Module collage")
    arcade.set_background_color(arcade.color.WHITE)

    arcade.start_render()

    row = -1  # start at -1 so we can increment at 0
    for (col, pil) in enumerate(pils):
        if col % num_columns == 0:
            row += 1
        rect = basis_rect.in_grid(
            row,
            col % num_columns,
            xpad=padding,
            ypad=padding,
        )
        tex = arcade.Texture(
            name=str(hash(pil.tobytes())),
            image=pil,
            hit_box_algorithm=None,
        )
        tex.draw_scaled(rect.center.x, rect.center.y)

    arcade.finish_render()
    arcade.run()
    print("done")
