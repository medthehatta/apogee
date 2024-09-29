from rect import Rect
from rect import RectLRBT


def flatten(lst):
    return sum(lst, [])


def build_rect_tree(specs, pre=None):
    if len(specs) == 0:
        raise ValueError(f"Need to provide specs.  ({pre=})")

    if len(specs) == 1:
        (_, rect) = specs[0]
        return RectTree(pre, rect)

    all_firsts = list(set(p[0] for (p, r) in specs))

    def children_of(k):
        matching = [(p, r) for (p, r) in specs if p[0] == k]
        return [(p[1:], r) for (p, r) in matching]

    children = [build_rect_tree(children_of(k), pre=k) for k in all_firsts]
    child_rects = [c.rect for c in children]
    aabb = RectLRBT.aabb(child_rects)

    return RectTree(pre, aabb, children=children)


class RectTree:

    def __init__(self, identifier, rect, children=None):
        self.identifier = identifier
        self.rect = rect
        self.children = children or []

    def ids_at(self, point):
        if not self.children:
            if self.rect.contains_point(point):
                return [[self.identifier]]
            else:
                return [[]]

        matching = [
            child for child in self.children
            if child.rect.contains_point(point)
        ]

        paths_without_children = [
            [self.identifier, child.identifier] for child in matching if not child.children
        ]

        paths_with_children = flatten(
            flatten(
                [
                    [self.identifier, child.identifier] + ids_
                    for ids_ in c.ids_at(point)
                    if ids_
                ]
                for c in child.children
            )
            for child in matching if child.children
        )

        return paths_without_children + paths_with_children

    def __repr__(self):
        return f"RectTree({self.identifier}, {self.rect})"
