from contextlib import contextmanager
from itertools import cycle
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


def render_module_collage(modules, num_columns=5, padding=2, margin=5):
    if not modules:
        raise ValueError("Must provide a nonempty list of modules")
    pils = [module_to_pil(mod) for mod in modules]
    pil_width = pils[0].width
    pil_height = pils[0].height
    basis_rect = (
        RectLRBT.blwh((0, 0), pil_width, pil_height)
        .displace((margin, margin))
    )

    num_rows = len(pils) // num_columns
    rows_then_columns = basis_rect.tiled(
        rows=num_rows,
        columns=num_columns,
        xpad=padding,
        ypad=padding,
    ).as_iter_rows_columns()

    width = num_columns * (pil_width + padding) - padding + 2*margin
    height = num_rows * (pil_height + padding) - padding + 2*margin

    with arcade_window(width, height, "Module collage"):
        for (rect, pil) in zip(rows_then_columns, pils):
            tex = arcade.Texture(
                name=str(hash(pil.tobytes())),
                image=pil,
                hit_box_algorithm=None,
            )
            scaled_rect = rect.scale_centered_pct(90)
            tex.draw_sized(
                scaled_rect.center.x,
                scaled_rect.center.y,
                scaled_rect.width,
                scaled_rect.height,
            )

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


class RectSeriesArtist:

    def __init__(self, color_sequence):
        self.colors = cycle(color_sequence)

    def draw(self, rect):
        draw_rect(rect, next(self.colors))

    def draw_all(self, rects):
        color = next(self.colors)
        for rect in rects:
            draw_rect(rect, color)


def render_rect_sample():
    artist = RectSeriesArtist(
        [
            arcade.color.BLACK,
            arcade.color.BLUE,
            arcade.color.RED,
            arcade.color.GREEN,
        ]
    )

    outer_rect = RectLRBT.blwh((0, 0), 1024, 768)
    with arcade_window(outer_rect.width + 10, outer_rect.height + 10):
        artist.draw(inset_rect := outer_rect.scale_centered_pct(90))
        artist.draw(bottom_right_rect := inset_rect.subdivisions(2, 2).cell(row=0, column=1))
        artist.draw(bottom_right_inset := bottom_right_rect.scale_to_topleft_pct(90))
        artist.draw(
            lil_square_sub :=
            bottom_right_inset
            .subdivisions(rows=2, columns=3).cell(row=1, column=0)
        )
        artist.draw(
            lil_square :=
            lil_square_sub
            .at_center_with_width_height(
                lil_square_sub.width,
                lil_square_sub.width,
            )
            .scale_centered_pct(90)
        )
        artist.draw_all(
            rect.scale_centered_pct(90) for rect in
            inset_rect.subdivisions(rows=2, columns=5).row(1)
        )


seed = 20
rng = random.Random(seed)
render_module_collage(random_modules(20, rng))
# render_rect_sample()
