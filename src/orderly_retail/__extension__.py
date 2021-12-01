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
            [RFMScoreR('(R) 時間分數'), RFMScoreF('(F) 頻率分數'), RFMScoreM('(M) 消費分數')],
            icon='icon-height'
        )

        self.register_filter_tab(
            'order',
            {'zh_tw': '購買行為篩選'},
            [PurchaseCount('購買次數'), PurchaseAmount('購買金額'), ProductCategoryCondition('購買商品類別'), ProductCondition('購買商品')],
            icon='icon-cart2'
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
