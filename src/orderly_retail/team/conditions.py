from client_filter.conditions import Condition

class GenderCondition(Condition):
    def __init__(self):
        self.editor = 'selector'
        self.data = {
            'choices': ['男', '女', '未知']
        }
        self.localization = {
            'zh_tw': '性別篩選'
        }

class AgeCondition(Condition):
    def __init__(self):
        self.editor = 'range-slider'
        self.data = {
            'from': 0,
            'to': 100,
            'min': 0,
            'max': 100
        }
        self.localization = {
            'zh_tw': '年齡範圍'
        }
