#
# Constants
#


MAX_ROUNDS = 100


#
# Classes
#


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
