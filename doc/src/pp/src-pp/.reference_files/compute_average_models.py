from django.db import models
from django.forms import ModelForm

class Average(models.Model):
    data_array = models.CharField(verbose_name=' data_array', default='[1]',max_length=28,)
    filename   = models.FileField(verbose_name=' filename', upload_to='uploads/', blank=True)

class AverageForm(ModelForm):
    class Meta:
        model = Average
