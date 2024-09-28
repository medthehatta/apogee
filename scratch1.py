from contextlib import contextmanager
import random

import arcade

from rect import RectLRBT
from scratch import module_to_pil
from scratch import random_modules


@contextmanager
def arcade_window(
    width,
    height,
    name="Arcade",
    bgcolor=arcade.color.WHITE,
):
    arcade.open_window(width, height, name)
    arcade.set_background_color(bgcolor)
    arcade.start_render()
    try:
        yield
    finally:
        arcade.finish_render()
    arcade.run()


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

    with arcade_window(width, height, "Module collage"):
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

    print("done")


def draw_rect(rect, color=arcade.color.BLACK):
    print(f"Drawing {rect}")
    arcade.draw_rectangle_outline(
        rect.center.x,
        rect.center.y,
        rect.width,
        rect.height,
        color=color,
        border_width=2,
    )


def render_rect_sample():
    outer_rect = RectLRBT.blwh((0, 0), 500, 500)
    with arcade_window(500, 500):
        draw_rect(outer_rect)
        inset_rect = outer_rect.scale_centered_pct(90)
        draw_rect(inset_rect)


# seed = 20
# rng = random.Random(seed)
# render_module_collage(random_modules(20, rng))
render_rect_sample()
