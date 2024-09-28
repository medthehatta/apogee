import random

import arcade

from rect import RectLRBT
from scratch import module_to_pil
from scratch import random_modules


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


seed = 20
rng = random.Random(seed)
render_module_collage(random_modules(20, rng))
