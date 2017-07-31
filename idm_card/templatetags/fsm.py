import django_fsm
from django import template

register = template.Library()

@register.filter('available_state_transitions')
def available_state_transitions(value, arg):
    return {transition.name
            for transition in value.get_available_user_state_transitions(arg)}
    print(dir(next(value)))
    return {transition.name
            for transition in value
            if transition.has_perm(transition.__self__, arg)}
