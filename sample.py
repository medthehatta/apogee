import random

from choice import Choice

from unit import Unit
from unit import Module
from unit import NormalDie
from unit import RiftDie

from rect import RectLRBT


#
# Choice helpers
#


def _weighted(*seq):
    return Choice.flat(Choice.weighted(*x) for x in seq)


#
# Functions
#


def _dice():
    num_dice = _weighted((15, 1), (8, 2), (2, 3), (1, 4))
    num_pips = _weighted((8, 1), (3, 2), (3, 3), (1, 4))
    kind = _weighted((10, NormalDie), (2, RiftDie))

    @Choice.delayed
    def _die_list(k, d, p):
        return tuple([k(p) if k is not RiftDie else k()]*d)

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
                return 5*len(dice)
            case [NormalDie(x), *rest]:
                return x*len(dice)
            case _:
                return 0

    # Can't provide power with modules that provide attack
    if (
        params.get("power") and
        (params.get("missile_dice") or params.get("cannon_dice"))
    ):
        del params["power"]

    value_estimate = (
        sum(v for (k, v) in params.items() if isinstance(v, int))
        + _die_value(params.get("missile_dice"))
        + _die_value(params.get("cannon_dice"))
    )

    if params.get("power", 0) == 0:
        params["power_cost"] = int(value_estimate // 1.5)
    else:
        params["power_cost"] = 0

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


def random_rect_within(rect, width, height, rng=None):
    x = random.randint(
        int(rect.topleft.x),
        int(rect.topright.x),
    )
    y = random.randint(
        int(rect.bottomleft.y),
        int(rect.topleft.y),
    )
    return RectLRBT.cwh((x, y), width, height)
