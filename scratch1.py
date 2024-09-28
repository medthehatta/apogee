import random

from scratch import random_modules
from scratch import render_module_collage

seed = 20
rng = random.Random(seed)
render_module_collage(random_modules(20, rng))
