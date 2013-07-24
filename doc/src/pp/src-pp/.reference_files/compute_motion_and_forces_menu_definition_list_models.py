from django.db import models
from django.forms import ModelForm
from parampool.html5.django.models import MinMaxFloat

class MotionAndForces(models.Model):

    Initial_velocity       = models.FloatField(
        verbose_name=' Initial velocity',
        default=5)

    Initial_angle          = MinMaxFloat(
        verbose_name=' Initial angle',
        default=45,
        min_value=0, max_value=90)

    Spinrate               = models.FloatField(
        verbose_name=' Spinrate',
        default=50)

    Wind_velocity          = models.FloatField(
        verbose_name=' Wind velocity',
        default=0)

    Mass                   = models.FloatField(
        verbose_name=' Mass',
        default=0.1)

    Radius                 = models.FloatField(
        verbose_name=' Radius',
        default=0.11)

    Method                 = models.CharField(
        verbose_name=' Method',
        max_length=50,
        default='RK4',
        choices=[('RK4', 'RK4'), ('RK2', 'RK2'), ('ForwardEuler', 'ForwardEuler')])

    Time_step              = models.CharField(
        verbose_name=' Time step',
        default='None',
        max_length=50)

    Plot_simplified_motion = models.BooleanField(
        verbose_name=' Plot simplified motion',
        default=True)

    New_plot               = models.BooleanField(
        verbose_name=' New plot',
        default=True)

class MotionAndForcesForm(ModelForm):
    class Meta:
        model = MotionAndForces
