
import datetime

from typing import Any, List, Tuple, Optional
from dateutil.relativedelta import relativedelta

from django.db.models import Subquery, Count, Min, Sum, Max, F
from django.db.models.expressions import OuterRef
from django.db.models.query import Q
from django.db.models import QuerySet

from core.utils import list_to_dict

from client_filter import (
    RangeCondition, BooleanCondition, DateRangeCondition, SelectCondition,
    MultiSelectCondition
)

from .models import PurchaseBase

# RFM Filters
class RFMScoreR(RangeCondition):
    def __init__(self):
        super().__init__()
        self.range(0, 5)
        self.config(postfix=' 分', max_postfix=' +')

    def filter(self, client_qs: QuerySet, rfm_r_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        q &= Q(rfm_recency__range=rfm_r_range)

        return client_qs, q

    def get_name():
        return '(R) 時間分數'

class RFMScoreF(RangeCondition):
    def __init__(self):
        super().__init__()
        self.range(0, 5)
        self.config(postfix=' 分', max_postfix=' +')

    def filter(self, client_qs: QuerySet, rfm_f_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        q &= Q(rfm_recency__range=rfm_f_range)

        return client_qs, q

    def get_name():
        return '(F) 頻率分數'

class RFMScoreM(RangeCondition):
    def __init__(self):
        super().__init__()
        self.range(0, 5)
        self.config(postfix=' 分', max_postfix=' +')

    def filter(self, client_qs: QuerySet, rfm_m_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        q &= Q(rfm_recency__range=rfm_m_range)

        return client_qs, q

    def get_name():
        return '(M) 消費分數'


# Purchase Behavior Filters
class PurchaseCount(RangeCondition):
    def __init__(self):
        super().__init__()
        self.add_options(datetime_range=DateRangeCondition())
        self.range(0, 15)
        self.config(postfix=' 次', max_postfix=' +')

    def filter(self, client_qs: QuerySet, purchase_count_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        datetime_range = self.options.get('datetime_range')
        orderbase_qs = PurchaseBase.objects.filter(clientbase_id=OuterRef('id'), datetime__range=datetime_range)
        client_qs = client_qs.annotate(purchase_count=Subquery(orderbase_qs.annotate(count=Count('external_id')).values('count')[:1]))

        q &= Q(purchase_count__range=purchase_count_range)

        return client_qs, q

    def get_name():
        return '總消費次數'


class PurchaseAmount(RangeCondition):
    def __init__(self):
        super().__init__()
        self.add_options(datetime_range = DateRangeCondition())
        self.range(0, 15)
        self.config(prefix='$ ', postfix=' 元', max_postfix=' +')

    def filter(self, client_qs: QuerySet, purchase_amount_range: Any) -> Tuple[QuerySet, Q]:
        q = Q()

        datetime_range = self.options.get('datetime_range')
        orderbase_qs = PurchaseBase.objects.filter(clientbase_id=OuterRef('id'), datetime__range=datetime_range)
        client_qs = client_qs.annotate(purchase_amount=Subquery(orderbase_qs.annotate(amount=Sum('total_price')).values('amount')[:1]))

        q &= Q(purchase_amount__range=purchase_amount_range)

        return client_qs, q

    def get_name():
        return '總消費金額'


class ProductCategoryCondition(MultiSelectCondition):
    def __init__(self):
        super().__init__()

    def filter(self, client_qs: QuerySet, category_ids: List[int]) -> Tuple[QuerySet, Q]:
        q = Q()

        intersection = self.options.get('intersection', False)
        if intersection:
            q &= Q(orderbase__orderproduct__productbase__category_ids__contains=category_ids)
        else:
            q &= Q(orderbase__orderproduct__productbase__category_ids__overlap=category_ids)

        return client_qs, q

    def real_time_init(self, team, *args, **kwargs):
        category_qs = team.productcategorybase_set.objects.filter(removed=False)
        id_name_map = list_to_dict(category_qs.values('id', 'name'), _key='id')
        self.choice(**id_name_map)

class ProductCondition(MultiSelectCondition):
    def __init__(self):
        super().__init__()

    def filter(self, client_qs: QuerySet, product_ids: List[int]) -> Tuple[QuerySet, Q]:
        q = Q()

        intersection = self.options.get('intersection', False)
        if intersection:
            q &= Q(orderbase__orderproduct__productbase__contains=product_ids)
        else:
            q &= Q(orderbase__orderproduct__productbase__overlap=product_ids)

        return client_qs, q

    def real_time_init(self, team, *args, **kwargs):
        product_qs = team.productbase_set.objects.filter(removed=False)
        id_name_map = list_to_dict(product_qs.values('id', 'name'), _key='id')
        self.choice(**id_name_map)

# valuetag



# class ValueTagCondition(MultiSelectCondition):
#     def __init__(self):
#         super().__init__()

#     def filter(self, client_qs: QuerySet, tag_ids: List[int]) -> Tuple[QuerySet, Q]:
#         q = Q()

#         intersection = self.options.get('intersection', False)
#         if intersection:
#             q &= Q(tag_ids__contains=tag_ids)
#         else:
#             q &= Q(tag_ids__overlap=tag_ids)

#         return client_qs, q

#     def real_time_init(self, team, *args, **kwargs):
#         product_qs = team.tagbase_set.objects.filter(removed=False)
#         id_name_map = list_to_dict(product_qs.values('id', 'name'), _key='id')
#         self.choice(**id_name_map)
