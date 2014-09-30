from django.db import models
from django.forms import ModelForm

class DragFreeLanding(models.Model):
    initial_velocity = models.FloatField(verbose_name=' initial_velocity')
    initial_angle    = models.FloatField(verbose_name=' initial_angle')

class DragFreeLandingForm(ModelForm):
    class Meta:
        model = DragFreeLanding
