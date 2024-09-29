from rect import Rect
from rect import RectLRBT


def flatten(lst):
    return sum(lst, [])


class RectTree:

    @classmethod
    def from_leaves(cls, leaves, pre=None):
        if len(leaves) == 0:
            raise ValueError(f"Need to provide leaves.  ({pre=})")

        if len(leaves) == 1:
            (_, rect) = leaves[0]
            return cls(pre, rect)

        all_firsts = list(set(p[0] for (p, r) in leaves))

        def children_of(k):
            matching = [(p, r) for (p, r) in leaves if p[0] == k]
            return [(p[1:], r) for (p, r) in matching]

        children = [cls.from_leaves(children_of(k), pre=k) for k in all_firsts]
        child_rects = [c.rect for c in children]
        aabb = RectLRBT.aabb(child_rects)

        return cls(pre, aabb, children=children)

    def __init__(self, identifier, rect, children=None):
        self.identifier = identifier
        self.rect = rect
        self.children = children or []
        self.child_index = {c.identifier: c for c in self.children}

    def children_at(self, path):
        if len(path) == 0:
            return [self]

        if path[0] == self.identifier:
            return flatten([c.children_at(path[1:]) for c in self.children])

        return []

    def subtree_at(self, path):
        match path:

            case [self.identifier]:
                return [self]

            case [not_me]:
                return []

            case _:
                return flatten([c.subtree_at(path[1:]) for c in self.children])

    def subtrees_to(self, path, prefix=None):
        prefix = prefix or []

        match path:

            case [self.identifier]:
                return prefix + [self]

            case [not_me]:
                return []

            case _:
                return flatten([
                    c.subtrees_to(path[1:], prefix=[self])
                    for c in self.children
                ])

    def leaves(self, prefix=None):
        prefix = prefix or []
        path_to_me = list(prefix) + [self.identifier]

        if not self.children:
            return [(path_to_me, self.rect)]

        return flatten([c.leaves(prefix=path_to_me) for c in self.children])

    def insert_at(self, path, rect):
        subtree = self.subtree_at(path)
        all_leaves = subtree.leaves() + [(path, rect)]
        new_subtree = self.from_leaves(all_leaves)
        # TODO

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
