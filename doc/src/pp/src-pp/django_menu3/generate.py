from parampool.generator.django import generate
from compute import compute_motion_and_forces_with_menu, \
     menu_definition_api_with_separate_submenus

generate(compute_motion_and_forces_with_menu,
         menu_function=menu_definition_api_with_separate_submenus,
         MathJax=True)
