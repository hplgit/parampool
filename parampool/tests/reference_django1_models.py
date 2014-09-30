from django.db import models
from django.forms import ModelForm

class Mysimplefunc(models.Model):
    a = models.FloatField(verbose_name=' a')
    b = models.FloatField(verbose_name=' b')
    c = models.FloatField(verbose_name=' c')
    d = models.CharField(verbose_name=' d', default='None',max_length=28,)

class MysimplefuncForm(ModelForm):
    class Meta:
        model = Mysimplefunc
