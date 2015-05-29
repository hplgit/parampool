from parampool.generator.django import generate
from compute import compute_motion_and_forces_with_pool, \
     pool_definition_api

generate(compute_motion_and_forces_with_pool,
         pool_function=pool_definition_api,
         MathJax=True)
