from parampool.generator.django import generate
from compute import compute_lorenz
from pool_data import pool_function

generate(compute_lorenz, pool_function, enable_login=True)
