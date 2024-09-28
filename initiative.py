from itertools import cycle


class Initiative:

    def __init__(self, units):
        self.units = units
        self.initiative = sorted(
            self.units,
            key=lambda u: u.stats["initiative"],
            reverse=True,
        )

    def one_round(self):
        return iter(self.initiative)

    def is_everybody_dead(self):
        return all(not u.is_alive() for u in self.initiative)

    def alive(self):
        for u in self.initiative:
            if u.is_alive():
                yield u

    def cycle_alive(self):
        while True:
            if self.is_everybody_dead():
                return
            yield from self.alive()

    def cycle(self):
        return cycle(self.initiative)
