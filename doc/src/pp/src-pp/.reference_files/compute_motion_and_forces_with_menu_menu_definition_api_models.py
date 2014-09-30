from django.db import models
from django.forms import ModelForm
from parampool.html5.django.models import MinMaxFloat
from parampool.html5.django.forms.widgets import \
     TextInput, NumberInput, RangeInput, Textarea, EmailInput, URLInput

# Note: The verbose_name attribute starts with a blank to avoid
# that Django forces the first character to be upper case.

class MotionAndForcesWithMenu(models.Model):

    Initial_velocity       = models.CharField(
        verbose_name=' Initial velocity',
        default='5.0',
        max_length=50)

    Initial_angle          = MinMaxFloat(
        verbose_name=' Initial angle',
        default=45,
        min_value=0, max_value=90)

    Spinrate               = models.CharField(
        verbose_name=' Spinrate',
        default='50',
        max_length=50)

    Wind_velocity          = MinMaxFloat(
        verbose_name=' Wind velocity',
        default=0,
        min_value=-50, max_value=50)

    Mass                   = models.CharField(
        verbose_name=' Mass',
        default='0.1',
        max_length=50)

    Radius                 = models.CharField(
        verbose_name=' Radius',
        default='0.11',
        max_length=50)

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

class MotionAndForcesWithMenuForm(ModelForm):
    class Meta:
        model = MotionAndForcesWithMenu
        widgets = {
            'Initial_velocity'    : TextInput(attrs={'size': 11}),
            'Initial_angle'       : RangeInput(attrs={'size': 11, 'min': 0, 'max': 90, 'step': 0, 'onchange': 'showValue(this.value)'}),
            'Spinrate'            : TextInput(attrs={'size': 11}),
            'Wind_velocity'       : NumberInput(attrs={'size': 11, 'min': -50, 'max': 50, 'step': 0.5}),
            #'Wind_velocity'       : NumberInput(attrs={'size': 11, 'step': 'any'}),
            'Mass'                : TextInput(attrs={'size': 11}),
            'Radius'              : TextInput(attrs={'size': 11}),
            'Time_step'           : TextInput(attrs={'size': 11}),}
