from parampool.generator.flask import generate
from compute import compute_motion_and_forces_with_pool, \
     pool_definition_list

generate(compute_motion_and_forces_with_pool,
         pool_function=pool_definition_list,
         MathJax=True)
