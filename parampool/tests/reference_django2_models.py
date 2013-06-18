from django.db import models
from django.forms import ModelForm

class Myfunc(models.Model):
    a = models.FloatField(verbose_name=' a', default=1.2,)
    b = models.IntegerField(verbose_name=' b', default=2,)
    c = models.CharField(verbose_name=' c', default='some text',max_length=28,)
    d = models.CharField(verbose_name=' d', default='None',max_length=28,)
    e = models.CharField(verbose_name=' e', default='[1, 2, 3]',max_length=28,)
    f = models.CharField(verbose_name=' f', default='(4, 5, 6)',max_length=28,)
    g = models.CharField(verbose_name=' g', default='[-1, 1]',max_length=28,)
    h = models.CharField(verbose_name=' h', default='MySpecialClass(6)',max_length=28,)
    i = models.CharField(verbose_name=' i', default='True',max_length=28,)

class MyfuncForm(ModelForm):
    class Meta:
        model = Myfunc
