from svgcomposer import empty_svg_string
from svgcomposer import interpolate_svg_to_string
from svgcomposer import svg_string_to_pil


def svg_for_attr(icon, value):
    return interpolate_svg_to_string(
        filepath="svgs/attr_row.svg",
        text_replacements={
            "attr_value": value,
        },
        svg_replacements={
            "attrIcon": interpolate_svg_to_string(f"svgs/{icon}.svg"),
        },
    )


def svg_for_power_cost(cost):
    if cost == 0:
        return empty_svg_string()
    else:
        return interpolate_svg_to_string(
            filepath="svgs/power_draw.svg",
            text_replacements={"power_draw": cost},
        )


def svg_for_module(module):

    attr_svgs = []

    if module.missile_dice:
        value = len(module.missile_dice)
        first_die = module.missile_dice[0]
        icon = (
            "die_rift" if first_die.__class__.__name__ == "RiftDie" else
            f"die_{first_die.hits}pip"
        )
        attr_svgs.append(svg_for_attr(icon, value))

    if module.cannon_dice:
        value = len(module.cannon_dice)
        first_die = module.cannon_dice[0]
        icon = (
            "die_rift" if first_die.__class__.__name__ == "RiftDie" else
            f"die_{first_die.hits}pip"
        )
        attr_svgs.append(svg_for_attr(icon, value))

    for (stat, value, _) in module.stats().triples():
        if stat == "power_cost":
            continue
        if value == 0:
            continue
        icon = stat
        attr_svgs.append(svg_for_attr(icon, value))

    match attr_svgs:
        case []:
            attr_replacements = {}
        case [x]:
            attr_replacements = {"attrOdd1": x}
        case [x, y]:
            attr_replacements = {"attrEven1": x, "attrEven2": y}
        case [x, y, z]:
            attr_replacements = {"attrOdd1": x, "attrOdd2": y, "attrOdd3": z}
        case _:
            raise ValueError(f"Too many attrs ({len(attr_svgs)})!  {module}")

    return interpolate_svg_to_string(
        filepath="svgs/module.svg",
        svg_replacements={
            "powerDraw": svg_for_power_cost(module.stats()["power_cost"]),
            **attr_replacements
        },
    )
