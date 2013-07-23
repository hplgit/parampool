from django.db import models
from django.forms import ModelForm

class DragFreeMotionPlot(models.Model):
    initial_velocity = models.FloatField(verbose_name=' initial_velocity', default=5.0,)
    initial_angle    = models.FloatField(verbose_name=' initial_angle', default=45.0,)

class DragFreeMotionPlotForm(ModelForm):
    class Meta:
        model = DragFreeMotionPlot
