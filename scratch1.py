from contextlib import contextmanager
from io import BytesIO
from itertools import cycle
from itertools import product
from pprint import pprint
import random
import string

import pyglet
import webcolors

from pyglet_utils import pil_to_sprite_at_rect
from rect import RectLRBT
from rect_tree import RectTree
from scratch import module_to_pil
from scratch import random_modules
from sample import random_rect_within


class ModuleCollage(pyglet.window.Window):

    def __init__(self, num_modules, num_columns=5, padding=2, margin=5):
        super().__init__()
        self.num_modules = num_modules
        self.num_columns = num_columns
        self.padding = padding
        self.margin = margin
        self.rng = None
        self.modules = []
        self.rect_tree = None
        self.batch = pyglet.graphics.Batch()
        self.entities = []
        self.setup()
        self.draw_background()
        self.draw_view()

    def setup(self):
        seed = 20
        self.rng = random.Random(seed)
        self.modules = random_modules(self.num_modules, rng=self.rng)
        self.module_lookup = {id(mod): mod for mod in self.modules}

    def draw_background(self):
        self.entities.append(
            pyglet.shapes.Rectangle(
                0,
                0,
                self.width,
                self.height,
                color=(255, 255, 255),
                batch=self.batch,
            )
        )

    def pil_to_sprite_at_rect(self, pil, rect):
        self.entities.append(
            sprite := pil_to_sprite_at_rect(pil, rect, batch=self.batch)
        )
        return sprite

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def draw_view(self):
        margin = self.margin
        padding = self.padding
        num_columns = self.num_columns
        modules = self.modules

        rect_tree_nodes = []

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

        for (rect, pil, mod) in zip(rows_then_columns, pils, modules):
            scaled_rect = rect.scale_centered_pct(90)
            self.pil_to_sprite_at_rect(pil, scaled_rect)
            rect_tree_nodes.append(([id(mod)], scaled_rect))

        self.rect_tree = RectTree.from_leaves(rect_tree_nodes)

    def on_mouse_press(self, x, y, button, modifiers):
        at_pos = self.rect_tree.ids_at((x, y))
        print([self.module_lookup[id_] for [_, id_] in at_pos])


def colors_and_names():
    color_sequence = [
        webcolors.name_to_rgb(name)
        for name in webcolors.names()
    ]
    colors = cycle(color_sequence)
    names = iter(
        list(string.ascii_uppercase)
        + [
            "".join(x)
            for x
            in product(string.ascii_uppercase, string.ascii_uppercase)
        ]
    )
    return zip(colors, names)


class RectTreeSample(pyglet.window.Window):

    def __init__(self):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        self.entities = []
        self.setup()
        self.draw_background()
        self.draw_view()

    def setup(self):
        outer_rect = RectLRBT.blwh((0, 0), 1024, 768)
        self.sections = (
            outer_rect
            .scale_centered_pct(90)
            .subdivisions(rows=3, columns=4)
            .as_iter_rows_columns()
        )
        rect_tree_nodes = []
        self.section_rects = []
        for (i, section) in enumerate(self.sections):
            rectlist = []
            for n in range(random.randint(2, 7)):
                rect = random_rect_within(section, 25, 25)
                rectlist.append(rect)
                rect_tree_nodes.append(((i, n), rect))

            self.section_rects.append((i, section, rectlist))

        self.rect_tree = RectTree.from_leaves(rect_tree_nodes)

    def draw_background(self):
        self.entities.append(
            pyglet.shapes.Rectangle(
                0,
                0,
                self.width,
                self.height,
                color=(255, 255, 255),
                batch=self.batch,
            )
        )

    def draw_view(self):
        cns = colors_and_names()
        for (i, section, rectlist) in self.section_rects:
            self.draw_rect(
                section,
                color=webcolors.name_to_rgb("aliceblue"),
                text=f"${i}",
            )
            for (rect, (color, name)) in zip(rectlist, cns):
                self.draw_rect(rect, color=color, text=name)
            aabb = RectLRBT.aabb(rectlist)
            self.draw_rect(aabb, text=f"{i}")

    def draw_rect(self, rect, color=(0, 0, 0), text=None):
        self.entities.append(
            pyglet.shapes.Box(
                rect.bottomleft.x,
                rect.bottomleft.y,
                rect.width,
                rect.height,
                color=color,
                thickness=2,
                batch=self.batch,
            )
        )

        if text:
            text_rect = rect.scale_centered_pct(40)
            self.entities.append(
                pyglet.text.Label(
                    text,
                    x=text_rect.center.x,
                    y=text_rect.center.y,
                    anchor_x="center",
                    anchor_y="center",
                    font_name="Arial",
                    font_size=text_rect.width,
                    color=color,
                    batch=self.batch,
                )
            )

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        print(self.rect_tree.ids_at((x, y)))


def annotated_pprint(stuff, description=None):
    if description:
        print(description)
    pprint(stuff)
    print("")
    return stuff


if __name__ == "__main__":
    view = ModuleCollage(20)

    pyglet.app.run()
