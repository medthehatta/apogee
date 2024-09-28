from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from dataclasses import MISSING
from functools import reduce
from itertools import cycle
import random

from choice import Choice
from formal_vector import FormalVector
from initiative import Initiative


#
# Constants
#


MAX_ROUNDS = 100


#
# Choice helpers
#


def _weighted(*seq):
    return Choice.flat(Choice.weighted(*x) for x in seq)


#
# Classes
#


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
    speed: int = 0
    initiative: int = 0
    power_cost: int = 0

    def stats(self):
        return Stats.from_triples(
            [
                ("targeting", self.targeting, None),
                ("mitigation", self.mitigation, None),
                ("hull_tank", self.hull_tank, None),
                ("power", self.power, None),
                ("speed", self.speed, None),
                ("initiative", self.initiative, None),
                ("power_cost", self.power_cost, None),
            ]
        )

    def __repr__(self):
        field_dict = asdict(self)
        non_defaults = [
            (f.name, field_dict[f.name]) for f in fields(self)
            if f.default is not MISSING and f.default != field_dict[f.name]
        ]
        fs = ", ".join(f"{f}={v}" for (f, v) in non_defaults)
        return f"{self.__class__.__name__}({fs})"


class Unit:

    def __init__(self, name, num_slots, modules=None):
        self.name = name
        self.num_slots = num_slots
        self.absorbed_hits = 0
        self._modules = modules or []
        if len(self._modules) > num_slots:
            raise ValueError(
                f"Number of modules ({len(self._modules)}) exceeds number of "
                f"slots ({self.num_slots})"
            )

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

    def slot_module(self, slot, module):
        if slot >= self.num_slots:
            raise ValueError(f"Not a valid slot number: {slot}")

        if (
            (
                self.stats["power"] - self.stats["power_cost"]
                - self.modules[slot].power + self.modules[slot].power_cost
                + module.power - module.power_cost
            )
            < 0
        ):
            raise ValueError(f"Module exceeds power budget: {module}")

        self._modules[slot] = module

    def __repr__(self):
        return f"<{self.name}>"


#
# Main functions
#


def _combat_turn_text(
    attacker,
    defender,
    volley,
    mitigated,
    damage,
    self_damage=None,
):
    if volley.all_hits() == 0:
        volley_text = f"{attacker} attacks {defender} with {volley} and misses!"
    else:
        volley_text = (
            f"{attacker} attacks {defender} with {volley} mitigated to "
            f"{mitigated.all_hits()} inflicting {damage}"
        )

    if self_damage:
        self_damage_text = f" (they also inflict {self_damage} on themselves)"
    else:
        self_damage_text = ""

    if defender.is_dead():
        death_text = f"\n{defender} has been defeated!"
    else:
        death_text = ""

    if attacker.is_dead():
        attacker_death_text = f"\nBut {attacker} has destroyed themselves!"
    else:
        attacker_death_text = ""

    return f"{volley_text}{self_damage_text}{death_text}{attacker_death_text}"


def perform_combat(rng, initiative):
    for attacker in initiative.one_round():
        if attacker.is_dead():
            print(f"Would-be attacker {attacker} is dead!")
            continue
        defender = attacker.select_missile_target(initiative.alive())
        volley = attacker.missile_volley(rng)
        mitigated = defender.mitigate(volley)
        damage = defender.absorb(mitigated)
        print(_combat_turn_text(attacker, defender, volley, mitigated, damage))

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
            _combat_turn_text(
                attacker,
                defender,
                volley,
                mitigated,
                damage,
                self_damage,
            )
        )

    if initiative.is_everybody_dead():
        print("No combatants remain!")


def _dice():
    num_dice = _weighted((15, 1), (8, 2), (2, 3), (1, 4))
    num_pips = _weighted((8, 1), (3, 2), (3, 3), (1, 4))
    kind = _weighted((10, NormalDie), (2, RiftDie))

    @Choice.delayed
    def _die_list(k, d, p):
        return [k(p) if k is not RiftDie else k()]*d

    return _die_list(kind, num_dice, num_pips)


def random_module(rng=None):
    rng = rng or random.Random()

    def _weighted(*seq):
        return Choice.flat(Choice.weighted(*x) for x in seq)

    num_effects = _weighted((10, 1), (3, 2), (1, 3)).evaluate(rng)

    props = [
        "missile_dice",
        "missile_dice",
        "cannon_dice",
        "cannon_dice",
        "cannon_dice",
        "hull_tank",
        "hull_tank",
        "mitigation",
        "mitigation",
        "targeting",
        "power",
        "power",
        "power",
        "power",
        "speed",
        "initiative",
        "initiative",
    ]
    rng.shuffle(props)
    taken_props = props[:num_effects]
    prop_values = {
        "missile_dice": _dice(),
        "cannon_dice": _dice(),
        "targeting": _weighted((10, 1), (5, 2), (1, 3)),
        "mitigation": _weighted((10, 1), (5, 2), (1, 3)),
        "hull_tank": _weighted((10, 1), (5, 2), (1, 3)),
        "power": _weighted((3, 1), (10, 2), (5, 3), (1, 4)),
        "speed": _weighted((10, 1), (5, 2), (1, 3)),
        "initiative": _weighted((10, 1), (5, 2), (1, 3)),
    }
    params = {p: prop_values[p].evaluate(rng) for p in taken_props}

    def _die_value(dice):
        match dice:
            case [RiftDie(), *rest]:
                return 5
            case [NormalDie(x), *rest]:
                return x
            case _:
                return 0

    value_estimate = (
        sum(v for (k, v) in params.items() if isinstance(v, int))
        + _die_value(params.get("missile_dice"))
        + _die_value(params.get("cannon_dice"))
    )

    params["power_cost"] = int(value_estimate // 1.5)
    return Module(**params)


def random_unit(name, rng=None):
    rng = rng or random.Random()

    num_slots = _weighted((10, 5), (5, 8), (2, 10)).evaluate(rng)
    starting_modules = [
        Module(power=3),
        Module(cannon_dice=[NormalDie(2)]*2),
        Module(cannon_dice=[NormalDie(1)]*1),
        Module(cannon_dice=[NormalDie(1)]*1),
    ]
    leftovers = num_slots - len(starting_modules)
    unit = Unit(
        name,
        num_slots=num_slots,
        modules=starting_modules + [Module()]*leftovers,
    )
    for _ in range(300):
        try:
            slot = random.randint(0, num_slots-1)
            unit.slot_module(slot, random_module(rng))
        except ValueError:
            pass

    return unit


def main():
    seed = random.random()
    rng = random.Random(seed)
    ship = Unit(
        "ship",
        num_slots=5,
        modules=[
            Module(missile_dice=[NormalDie(1)]),
            Module(cannon_dice=[NormalDie(3), NormalDie(3)]),
            Module(hull_tank=5),
            Module(mitigation=1),
            Module(targeting=1),
        ],
    )

    opponent_names = ["adam", "betty", "charlie", "diane"]
    opponents = [random_unit(n, rng) for n in opponent_names]

    initiative = Initiative([ship] + opponents)
    for entry in initiative.one_round():
        print(entry)
        print(entry.stats)
        for m in entry.modules:
            print(m)
        print("")
    print("\n")

    perform_combat(rng, initiative)


if __name__ == "__main__":
    main()
