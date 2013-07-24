from django.db import models
from django.forms import ModelForm
from parampool.html5.django.models import MinMaxFloat

class MotionAndForcesWithMenu(models.Model):

    Initial_velocity = models.CharField(
        verbose_name=' Initial velocity',
        default='5.0',
        max_length=50)

    Initial_angle = models.CharField(
        verbose_name=' Initial angle',
        default='45',
        max_length=50)

    Spinrate = models.CharField(
        verbose_name=' Spinrate',
        default='50',
        max_length=50)

    Wind_velocity = models.CharField(
        verbose_name=' Wind velocity',
        default='0.0',
        max_length=50)

    Mass = models.CharField(
        verbose_name=' Mass',
        default='0.1',
        max_length=50)

    Radius = models.CharField(
        verbose_name=' Radius',
        default='0.11',
        max_length=50)

    Method = models.CharField(
        verbose_name=' Method',
        max_length=50,
        default='RK4',
        choices=[('RK4', 'RK4'), ('RK2', 'RK2'), ('ForwardEuler', 'ForwardEuler')])

    Time_step = models.CharField(
        verbose_name=' Time step',
        default='None',
        max_length=50)

    Plot_simplified_motion = models.BooleanField(
        verbose_name=' Plot simplified motion',
        default=True)

    New_plot = models.BooleanField(
        verbose_name=' New plot',
        default=True)

class MotionAndForcesWithMenuForm(ModelForm):
    class Meta:
        model = MotionAndForcesWithMenu
