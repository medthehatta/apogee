from contextlib import contextmanager
from itertools import cycle
from itertools import product
from pprint import pprint
import random
import string

import arcade

from rect import RectLRBT
from rect_tree import RectTree
from scratch import module_to_pil
from scratch import random_modules
from sample import random_rect_within


class ShipBuilder(arcade.View):

    def __init__(
        self,
        ship_slots,
        num_modules,
        num_columns=5,
        padding=2,
        margin=5,
    ):
        super().__init__()
        self.ship_slots = ship_slots
        self.num_modules = num_modules
        self.num_columns = num_columns
        self.padding = padding
        self.margin = margin
        self.rng = None
        self.modules = []
        self.rect_tree = None

    def setup(self):
        seed = 20
        self.rng = random.Random(seed)
        self.modules = random_modules(self.num_modules, rng=self.rng)
        self.module_lookup = {id(mod): mod for mod in self.modules}

    def on_show_view(self):
        margin = self.margin
        padding = self.padding
        num_columns = self.num_columns
        modules = self.modules

        rect_tree_nodes = []

        arcade.set_background_color(arcade.color.WHITE)

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

        module_rects = []
        for (rect, mod) in zip(rows_then_columns, modules):
            scaled_rect = rect.scale_centered_pct(90)
            module_rects.append(scaled_rect)
            rect_tree_nodes.append((["inventory", id(mod)], rect))

        arcade.start_render()
        for (rect, pil) in zip(module_rects, pils):
            tex = arcade.Texture(
                name=str(hash(pil.tobytes())),
                image=pil,
                hit_box_algorithm=None,
            )
            tex.draw_sized(
                rect.center.x,
                rect.center.y,
                rect.width,
                rect.height,
            )
        arcade.finish_render()
        self.rect_tree = RectTree.from_leaves(rect_tree_nodes)

    def on_mouse_press(self, x, y, button, modifiers):
        at_pos = self.rect_tree.ids_at((x, y))
        print([self.module_lookup[path[-1]] for path in at_pos])


class ModuleCollage(arcade.View):

    def __init__(self, num_modules, num_columns=5, padding=2, margin=5):
        super().__init__()
        self.num_modules = num_modules
        self.num_columns = num_columns
        self.padding = padding
        self.margin = margin
        self.rng = None
        self.modules = []
        self.rect_tree = None

    def setup(self):
        seed = 20
        self.rng = random.Random(seed)
        self.modules = random_modules(self.num_modules, rng=self.rng)
        self.module_lookup = {id(mod): mod for mod in self.modules}

    def on_show_view(self):
        margin = self.margin
        padding = self.padding
        num_columns = self.num_columns
        modules = self.modules

        rect_tree_nodes = []

        arcade.set_background_color(arcade.color.WHITE)

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

        arcade.start_render()
        for (rect, pil, mod) in zip(rows_then_columns, pils, modules):
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
            rect_tree_nodes.append(([id(mod)], rect))
        arcade.finish_render()
        self.rect_tree = RectTree.from_leaves(rect_tree_nodes)

    def on_mouse_press(self, x, y, button, modifiers):
        at_pos = self.rect_tree.ids_at((x, y))
        print([self.module_lookup[id_] for [_, id_] in at_pos])


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


class RectSample(arcade.View):

    def setup(self):
        pass

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        artist = RectSeriesArtist()
        arcade.start_render()
        outer_rect = RectLRBT.blwh((0, 0), 1024, 768)
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
        arcade.finish_render()


class RectTreeSample(arcade.View):

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

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        artist = RectSeriesArtist()
        arcade.start_render()
        for (i, section, rectlist) in self.section_rects:
            draw_rect(section, color=arcade.color.ALICE_BLUE, text=f"${i}")
            for rect in rectlist:
                artist.draw(rect)
            draw_rect(RectLRBT.aabb(rectlist), text=f"{i}")
        arcade.finish_render()

    def on_mouse_press(self, x, y, button, modifiers):
        print(self.rect_tree.ids_at((x, y)))


window = arcade.Window(1024, 768, "Arcade")
view = ShipBuilder(ship_slots=6, num_modules=30, num_columns=9)
# view = RectTreeSample()
view.setup()
window.show_view(view)
print("children")
pprint(view.rect_tree.children)
print("subtree at [None, inventory]")
pprint(view.rect_tree.subtree_at([None, "inventory"]))
print("subtrees to [None, inventory]")
pprint(view.rect_tree.subtrees_to([None, "inventory"]))
print("children at [None, inventory]")
pprint(view.rect_tree.children_at([None, "inventory"]))
print("all leaves")
pprint(view.rect_tree.leaves())
arcade.run()
