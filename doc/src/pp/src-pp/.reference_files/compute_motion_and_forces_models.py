from django.db import models
from django.forms import ModelForm

class MotionAndForces(models.Model):
    initial_velocity       = models.FloatField(verbose_name=' initial_velocity', default=5.0,)
    initial_angle          = models.FloatField(verbose_name=' initial_angle', default=45.0,)
    spinrate               = models.FloatField(verbose_name=' spinrate', default=50.0,)
    w                      = models.FloatField(verbose_name=' w', default=0.0,)
    m                      = models.FloatField(verbose_name=' m', default=0.1,)
    R                      = models.FloatField(verbose_name=' R', default=0.11,)
    method                 = models.CharField(verbose_name=' method', default='RK4',max_length=28,)
    dt                     = models.CharField(verbose_name=' dt', default='None',max_length=28,)
    plot_simplified_motion = models.CharField(verbose_name=' plot_simplified_motion', default='True',max_length=28,)
    new_plot               = models.CharField(verbose_name=' new_plot', default='True',max_length=28,)

class MotionAndForcesForm(ModelForm):
    class Meta:
        model = MotionAndForces
