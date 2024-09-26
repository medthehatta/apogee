from dataclasses import dataclass
from dataclasses import field
from functools import reduce
from itertools import cycle
import random

from formal_vector import FormalVector


MAX_ROUNDS = 100


class Stats(FormalVector):
    _ZERO = "Stats.zero()"


@dataclass
class Die:

    def roll(self, rng):
        raise NotImplementedError()


@dataclass
class NormalDie(Die):

    hits: int

    def roll(self, rng):
        accuracy = rng.choice([1, 2, 3, 4, 5, 6])
        if accuracy == 6:
            accuracy = None
        return {"accuracy": accuracy, "hits": self.hits}


@dataclass
class RiftDie(Die):

    def roll(self, rng):
        (hits, self_hits) = rng.choice(
            [(1, 0), (2, 0), (3, 1), (0, 1), (0, 0), (0, 0)]
        )
        return {"accuracy": None, "hits": hits, "self_hits": self_hits}


class Volley:

    @classmethod
    def from_dice(cls, rng, dice):
        rolls = []
        for die in dice:
            roll = die.roll(rng)
            rolls.append((die, roll))
        return cls(rolls)

    def __init__(self, rolls):
        self.rolls = rolls
        self.combined = self._combine_rolls(rolls)

    def _combine_rolls(self, rolls):
        combined = {}
        for (_, roll) in rolls:
            accuracy = roll.get("accuracy", None)
            hits = roll.get("hits", 0)
            self_hits = roll.get("self_hits", 0)
            combined["self_hits"] = combined.get("self_hits", 0) + self_hits
            if accuracy is None:
                combined["definite"] = combined.get("definite", 0) + hits
            else:
                combined[accuracy] = combined.get(accuracy, 0) + hits

        return combined

    def _add_accuracy(self, combined, amount):
        new_combined = {}

        for k in combined:
            if k == "definite":
                new_combined[k] = combined[k]
            elif k == "self_hits":
                new_combined[k] = combined[k]
            else:
                new_k = k + amount
                if new_k < 1:
                    continue
                else:
                    new_combined[new_k] = combined[k]

        return new_combined

    @property
    def accuracies(self):
        return [k for k in self.combined if isinstance(k, int)]

    def add_accuracy(self, amount):
        self.combined = self._add_accuracy(self.combined, amount)
        return self

    def all_hits(self):
        return self.hits_at_least_accuracy(5)

    def hits_at_least_accuracy(self, accuracy):
        return (
            self.combined.get("definite", 0) +
            sum(self.combined[k] for k in self.accuracies if k >= accuracy)
        )

    def self_hits(self):
        return self.combined.get("self_hits", 0)

    def __repr__(self):
        f_rolls = [
            f"{r['hits']}@{r['accuracy']}" if r["accuracy"] is not None else
            f"{r['hits']}"
            for (_, r) in self.rolls
        ]
        return f"<Volley [{', '.join(f_rolls)}]>"


@dataclass
class Module:

    missile_dice: list[Die] = field(default_factory=list)
    cannon_dice: list[Die] = field(default_factory=list)
    targeting: int = 0
    mitigation: int = 0
    hull_tank: int = 0
    power: int = 0
    speed: int = 1
    initiative: int = 0

    def stats(self):
        return Stats.from_triples(
            [
                ("targeting", self.targeting, None),
                ("mitigation", self.mitigation, None),
                ("hull_tank", self.hull_tank, None),
                ("power", self.power, None),
                ("speed", self.speed, None),
                ("initiative", self.initiative, None),
            ]
        )


class Initiative:

    def __init__(self, units):
        self.units = units
        self.initiative = sorted(self.units, key=lambda u: u.stats["initiative"])

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


class Unit:

    def __init__(self, name, modules):
        self.name = name
        self.absorbed_hits = 0
        self._modules = modules

    @property
    def modules(self):
        return self._modules

    @property
    def stats(self):
        return self.stats_from_modules()

    @property
    def missile_dice(self):
        return sum([m.missile_dice for m in self.modules], [])

    @property
    def cannon_dice(self):
        return sum([m.cannon_dice for m in self.modules], [])

    def stats_from_modules(self):
        return Stats.sum(m.stats() for m in self.modules)

    def is_alive(self):
        return not self.is_dead()

    def is_dead(self):
        return self.absorbed_hits > self.stats["hull_tank"]

    def select_missile_target(self, targets):
        return max(
            [t for t in targets if t is not self],
            key=lambda t: (-t.stats["hull_tank"], len(t.missile_dice)),
        )

    def select_cannon_target(self, targets):
        eligible = [t for t in targets if t is not self]
        if eligible:
            return max(
                eligible,
                key=lambda t: (-t.stats["hull_tank"], len(t.cannon_dice)),
            )
        else:
            return None

    def missile_volley(self, rng):
        dice = self.missile_dice
        return Volley.from_dice(rng, dice).add_accuracy(self.stats["targeting"])

    def cannon_volley(self, rng):
        dice = self.cannon_dice
        return Volley.from_dice(rng, dice).add_accuracy(self.stats["targeting"])

    def mitigate(self, volley):
        return volley.add_accuracy(-self.stats["mitigation"])

    def mitigate_self_damage(self, volley):
        # TODO: Self-damage mitigation doesn't exist yet
        return volley

    def absorb(self, damage):
        hits = damage.all_hits()
        self.absorbed_hits += damage.all_hits()
        return hits

    def absorb_self_damage(self, damage):
        self.absorbed_hits += damage.self_hits()
        return damage.self_hits()

    def clear_hits(self):
        self.absorbed_hits = 0
        return self

    def __repr__(self):
        return f"<{self.name}>"


def perform_combat(rng, ship, opponent):
    initiative = Initiative([ship, opponent])

    for attacker in initiative.one_round():
        if attacker.is_dead():
            print(f"Attacker {attacker} is dead!")
            continue
        defender = attacker.select_missile_target(initiative.alive())
        volley = attacker.missile_volley(rng)
        mitigated = defender.mitigate(volley)
        damage = defender.absorb(mitigated)
        print(
            f"{attacker} attacks {defender} with {volley} mitigated to "
            f"{mitigated.all_hits()} inflicting {damage}"
        )

    for (i, attacker) in zip(range(MAX_ROUNDS), initiative.cycle_alive()):
        defender = attacker.select_cannon_target(initiative.alive())
        if defender is None:
            print(f"No defenders remain!  {attacker} is victorious!")
            break
        volley = attacker.cannon_volley(rng)
        self_mitigated = attacker.mitigate_self_damage(volley)
        self_damage = attacker.absorb_self_damage(self_mitigated)
        mitigated = defender.mitigate(volley)
        damage = defender.absorb(mitigated)
        print(
            f"{attacker} attacks {defender} with {volley} mitigated to "
            f"{mitigated.all_hits()} inflicting {damage} (and receiving {self_damage})"
        )

    if initiative.is_everybody_dead():
        print("No combatants remain!")


def main():
    seed = random.random()
    rng = random.Random(seed)
    ship = Unit(
        "ship",
        [
            Module(missile_dice=[NormalDie(1)]),
            Module(cannon_dice=[NormalDie(3), NormalDie(3)]),
            Module(hull_tank=5),
            Module(mitigation=1),
            Module(targeting=1),
        ],
    )
    opponent = Unit(
        "opponent",
        [
            Module(cannon_dice=[NormalDie(1), RiftDie()]),
            Module(hull_tank=20),
            Module(targeting=1),
        ],
    )
    perform_combat(rng, ship, opponent)


if __name__ == "__main__":
    main()
