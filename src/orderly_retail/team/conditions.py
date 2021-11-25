from orderly.client_filter.conditions import Condition

__all__ = ['GenderCondition']

class GenderCondition(Condition):
    def __init__(self):
        self.editor = 'choice'
        self.editor_data = {
            'choices': [
                {'zh_tw': '男'},
                {'zh_tw': '女'},
                {'zh_tw': '未知'}
            ]
        }
