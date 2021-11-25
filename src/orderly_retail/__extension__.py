import extension.extension as orderly_extension
from team.conditions import GenderCondition

class Extension(orderly_extension.Extension):
    def get_conditions():
        return [GenderCondition]

