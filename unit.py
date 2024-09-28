from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from dataclasses import MISSING

from formal_vector import FormalVector

from combat import Volley


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
