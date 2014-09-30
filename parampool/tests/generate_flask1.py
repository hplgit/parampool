from parampool.generator.flask import generate
from compute import mysimplefunc
generate(mysimplefunc, default_field='FloatField')
