from parampool.generator.django import generate
from compute import compute_drag_free_landing

generate(compute_drag_free_landing, default_field='FloatField')

