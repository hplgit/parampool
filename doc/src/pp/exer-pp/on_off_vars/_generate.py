from parampool.generator.flask import generate
from compute import formula as compute

generate(compute, default_field='FloatField')
