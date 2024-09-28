from contextlib import contextmanager
from itertools import cycle
from itertools import product
import random
import string

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


def draw_rect(rect, color=arcade.color.BLACK, text=None):
    if text:
        print(f"Drawing {rect} ({text})")
    else:
        print(f"Drawing {rect}")

    arcade.draw_rectangle_outline(
        rect.center.x,
        rect.center.y,
        rect.width,
        rect.height,
        color=color,
        border_width=2,
    )

    if text:
        text_rect = rect.scale_centered_pct(40)
        arcade.draw_text(
            text,
            start_x=text_rect.center.x,
            start_y=text_rect.center.y,
            anchor_x="center",
            anchor_y="center",
            font_size=text_rect.width,
            color=color,
        )


class RectSeriesArtist:

    def __init__(self):
        color_sequence = (
            getattr(arcade.color, x)
            for x in dir(arcade.color)
            if isinstance(getattr(arcade.color, x), tuple)
        )
        self.colors = cycle(color_sequence)
        self.names = iter(
            list(string.ascii_uppercase)
            + [
                "".join(x)
                for x
                in product(string.ascii_uppercase, string.ascii_uppercase)
            ]
        )

    def draw(self, rect):
        draw_rect(rect, next(self.colors), text=next(self.names))

    def draw_all(self, rects):
        color = next(self.colors)
        text = next(self.names)
        for rect in rects:
            draw_rect(rect, color, text=text)


def render_rect_sample():
    artist = RectSeriesArtist()

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


def render_rect_tree_sample():
    artist = RectSeriesArtist()

    outer_rect = RectLRBT.blwh((0, 0), 1024, 768)
    with arcade_window(outer_rect.width + 10, outer_rect.height + 10):
        sections = (
            outer_rect
            .scale_centered_pct(90)
            .subdivisions(rows=3, columns=4)
            .as_iter_rows_columns()
        )
        for (i, section) in enumerate(sections):
            draw_rect(section, color=arcade.color.ALICE_BLUE, text=f"${i}")
            rectlist = []
            for _ in range(5):
                x = random.randint(
                    int(section.topleft.x),
                    int(section.topright.x),
                )
                y = random.randint(
                    int(section.bottomleft.y),
                    int(section.topleft.y),
                )
                rect = RectLRBT.cwh((x, y), 25, 25)
                rectlist.append(rect)
                artist.draw(rect)
            draw_rect(RectLRBT.aabb(rectlist), text=f"{i}")


# seed = 20
# rng = random.Random(seed)
# render_module_collage(random_modules(20, rng))
# render_rect_sample()
render_rect_tree_sample()
