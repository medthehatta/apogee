from rect import Rect


def flatten(lst):
    return sum(lst, [])


class RectTree:

    def __init__(self, name, rect, children=None):
        self.name = name
        self.rect = rect
        self.children = children or []

    def ids_at(self, point):

        if not self.children:
            if self.rect.contains_point(point):
                return [[self.name]]
            else:
                return [[]]

        matching = [
            child for child in self.children
            if child.rect.contains_point(point)
        ]

        paths_without_children = [
            [self.name, child.name] for child in matching if not child.children
        ]

        paths_with_children = flatten(
            flatten(
                [[self.name, child.name] + ids_ for ids_ in c.ids_at(point)]
                for c in child.children
            )
            for child in matching if child.children
        )

        return paths_without_children + paths_with_children
