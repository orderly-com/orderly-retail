
from typing import List
import pandas as pd
from cerem.utils import PipelineBuilder
from analytics import analyzers

class OrderProductPipelineBuilder(PipelineBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_group_stage(self, group_keys: List[str]):
        group_stage = {}
        for key in group_keys:
            if key in ['day', 'week', 'month', 'year']:
                group_stage[key] = {
                    '$dateTrunc': {
                        'date': '$datetime',
                        'unit': key,
                        'timezone': '+08'
                    }
                }

            elif key == 'datasource':
                group_stage['datasource'] = '$datasource_id'

            elif key == 'category':
                group_stage['category'] = '$category_ids'

            elif key == 'price_floor':
                group_stage['price_floor'] = {
                    '$trunc': [
                        '$total_price', -2
                    ]
                }
            elif key == 'weekday':
                group_stage['weekday'] = {'$dayOfWeek': {'date': '$datetime', 'timezone': '+08'}}
            elif key in ['hour']:
                group_stage[key] = {f'${key}': {'date': '$datetime', 'timezone': '+08'}}
            else:
                group_stage[key] = f'${key}'

    def add_match_stage(self, filters):
        match_stage = {'status_key': 'CONFIRMED', 'internal_product': {'$ne': True}}
        if 'datasources' in filters:
            if filters['datasources']:
                match_stage['datasource_id'] = {
                    '$in': filters['datasources']
                }

        if 'productbase_id' in filters:
            match_stage['productbase_id'] = filters['productbase_id']

        if 'clientbase_id' in filters:
            match_stage['clientbase_id'] = filters['clientbase_id']

        if 'clientbase_ids' in filters:
            match_stage['clientbase_id'] = {
                '$in': filters['clientbase_ids']
            }

        if 'category_id' in filters:
            match_stage['category_ids'] = filters['category_id']

        if filters.get('date_start') or filters.get('date_end'):
            match_stage['datetime'] = {}

        if filters.get('date_start'):
            match_stage['datetime']['$gte'] = parser.parse(filters['date_start'])

        if filters.get('date_end'):
            match_stage['datetime']['$lte'] = parser.parse(filters['date_end'])

        if 'datasources' in filters:
            if filters['datasources']:
                match_stage['datasource_id'] = {
                    '$in': filters['datasources']
                }
        return match_stage

class OrderAnalyzer(analyzers.Analyzer):
    def analyze(self, date_start, date_end) -> pd.DataFrame:
        builder = OrderProductPipelineBuilder()
