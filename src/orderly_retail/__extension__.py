import extension.extension as orderly_extension
from .team.conditions import GenderCondition, AgeCondition

class Extension(orderly_extension.Extension):
    def __init__(self):
        super().__init__()

        self.register_filter_tab(
            {'zh_tw': '購買行為篩選'},
            [GenderCondition(), AgeCondition()]
        )

    def get_localization():
        return {
            'zh_tw': '電商 / 零售'
        }

    def get_filter_tab_localization():
        return {
            'zh_tw': ''
        }

    def setup():
        pass
