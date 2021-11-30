
import datetime

from typing import Any, List, Tuple, Optional, Dict
from dateutil.relativedelta import relativedelta

from django.db.models import Subquery, Count, Min, Sum, Max, F
from django.db.models.expressions import OuterRef
from django.db.models.fields import IntegerField
from django.db.models.query import Q
from django.db.models import QuerySet

from core.utils import list_to_dict

from client_filter.conditions import (
    RangeCondition, BooleanCondition, DateRangeCondition, SelectCondition
)

from .models import PurchaseBase

# RFM Filters
class RFMScoreR(RangeCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.range(0, 5)
        self.config(postfix=' 分', max_postfix=' +')

    def filter(self, client_qs: QuerySet, options: Dict, rfm_r_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        q &= Q(rfm_recency__range=rfm_r_range)

        return client_qs, q


class RFMScoreF(RangeCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.range(0, 5)
        self.config(postfix=' 分', max_postfix=' +')

    def filter(self, client_qs: QuerySet, options: Dict, rfm_f_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        q &= Q(rfm_recency__range=rfm_f_range)

        return client_qs, q


class RFMScoreM(RangeCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.range(0, 5)
        self.config(postfix=' 分', max_postfix=' +')

    def filter(self, client_qs: QuerySet, options: Dict, rfm_m_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        q &= Q(rfm_recency__range=rfm_m_range)

        return client_qs, q


# Purchase Behavior Filters
class PurchaseCount(RangeCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_options(datetime_range=DateRangeCondition('時間區間'))
        self.range(0, 15)
        self.config(postfix=' 次', max_postfix=' +')

    def filter(self, client_qs: QuerySet, options: Dict, purchase_count_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        datetime_range = options.get('datetime_range')
        orderbase_qs = PurchaseBase.objects.filter(clientbase_id=OuterRef('id'), datetime__range=datetime_range)
        client_qs = client_qs.annotate(purchase_count=Subquery(orderbase_qs.annotate(count=Count('external_id')).values('count')[:1], output_field=IntegerField()))

        q &= Q(purchase_count__range=purchase_count_range)

        return client_qs, q


class PurchaseAmount(RangeCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_options(datetime_range=DateRangeCondition('時間區間'))
        self.range(0, 15)
        self.config(prefix='$ ', postfix=' 元', max_postfix=' +')

    def filter(self, client_qs: QuerySet, options: Dict, purchase_amount_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        datetime_range = options.get('datetime_range')
        orderbase_qs = PurchaseBase.objects.filter(clientbase_id=OuterRef('id'), datetime__range=datetime_range)
        client_qs = client_qs.annotate(purchase_amount=Subquery(orderbase_qs.annotate(amount=Sum('total_price')).values('amount')[:1], output_field=IntegerField()))

        q &= Q(purchase_amount__range=purchase_amount_range)

        return client_qs, q


class ProductCategoryCondition(SelectCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def filter(self, client_qs: QuerySet, options: Dict, category_ids: List[int]) -> Tuple[QuerySet, Q]:
        q = Q()

        intersection = options.get('intersection', False)
        if intersection:
            q &= Q(orderbase__orderproduct__productbase__category_ids__contains=category_ids)
        else:
            q &= Q(orderbase__orderproduct__productbase__category_ids__overlap=category_ids)

        return client_qs, q

    def real_time_init(self, team, *args, **kwargs):
        category_qs = team.productcategorybase_set.values(text='name', id='uuid')
        self.choice(*category_qs)


class ProductCondition(SelectCondition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def filter(self, client_qs: QuerySet, options: Dict, product_ids: List[int]) -> Tuple[QuerySet, Q]:
        q = Q()

        intersection = options.get('intersection', False)
        if intersection:
            q &= Q(orderbase__orderproduct__productbase__contains=product_ids)
        else:
            q &= Q(orderbase__orderproduct__productbase__overlap=product_ids)

        return client_qs, q

    def real_time_init(self, team, *args, **kwargs):
        product_qs = team.productbase_set.filter(removed=False).values(text='name', id='uuid')
        self.choice(*product_qs)

# valuetag



# class ValueTagCondition(SelectCondition):
#     def __init__(self):
#         super().__init__()

#     def filter(self, client_qs: QuerySet, options: Dict, tag_ids: List[int]) -> Tuple[QuerySet, Q]:
#         q = Q()

#         intersection = options.get('intersection', False)
#         if intersection:
#             q &= Q(tag_ids__contains=tag_ids)
#         else:
#             q &= Q(tag_ids__overlap=tag_ids)

#         return client_qs, q

#     def real_time_init(self, team, *args, **kwargs):
#         product_qs = team.tagbase_set.objects.filter(removed=False)
#         id_name_map = list_to_dict(product_qs.values('id', 'name'), _key='id')
#         self.choice(**id_name_map)
