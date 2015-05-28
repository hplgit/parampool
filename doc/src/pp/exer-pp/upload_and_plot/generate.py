from parampool.generator.flask import generate
from upload_and_plot import compute, pool_def_api

generate(compute, pool_function=pool_def_api, MathJax=True)
