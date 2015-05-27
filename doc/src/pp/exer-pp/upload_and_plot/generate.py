from parampool.generator.flask import generate
from integrate import compute, pool_def_api

generate(compute, pool_function=pool_def_api, MathJax=True)
