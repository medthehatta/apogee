from rect import Rect
from rect import RectLRBT


def flatten(lst):
    return sum(lst, [])


class RectTree:

    @classmethod
    def from_leaf(cls, path, rect):
        (pre, *rest) = path
        return cls.from_leaves([(rest, rect)], pre=pre)

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

    def rect_from_children_aabb(self):
        self.rect = RectLRBT.aabb(c.rect for c in self.children)
        return self.rect

    def insert_child(self, new_child):
        self.children.append(new_child)
        self.child_index[new_child.identifier] = new_child
        self.rect_from_children_aabb()
        return self

    def remove_child(self, child_id):
        child = self.child_index.pop(child_id)
        self.children.remove(child)
        return child

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

    def subtrees_closest_to(self, path, prefix=None):
        prefix = prefix or []

        assert len(path) > 1
        assert path[0] == self.identifier

        matching_child = self.child_index.get(path[1])

        if matching_child:
            return (
                prefix +
                matching_child.subtrees_closest_to(path[1:], prefix=prefix + [self])
            )
        else:
            return prefix + [self]

    def leaves(self, prefix=None):
        prefix = prefix or []
        path_to_me = list(prefix) + [self.identifier]

        if not self.children:
            return [(path_to_me, self.rect)]

        return flatten([c.leaves(prefix=path_to_me) for c in self.children])

    def insert_at(self, path, rect):
        subtrees = self.subtrees_closest_to(path)
        remaining_path = path[len(subtrees):]
        subtree = subtrees[-1]
        child = type(self).from_leaf(remaining_path, rect)
        subtree.insert_child(child)

        for parent in reversed(subtrees[:-1]):
            parent.rect_from_children_aabb()

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
