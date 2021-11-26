import extension.extension as orderly_extension
from .team.conditions import (
    RFMScoreR, RFMScoreF, RFMScoreM, PurchaseCount, PurchaseAmount, ProductCategoryCondition, ProductCondition
)

class Extension(orderly_extension.Extension):
    def __init__(self):
        super().__init__()

        self.register_filter_tab(
            'rfm',
            {'zh_tw': 'RFM'},
            [RFMScoreR(), RFMScoreF(), RFMScoreM]
        )

        self.register_filter_tab(
            'order',
            {'zh_tw': '購買行為篩選'},
            [PurchaseCount(), PurchaseAmount(), ProductCategoryCondition(), ProductCondition()]
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
