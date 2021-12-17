from config.celery import app

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F

from team.models import Team
from data_calculation.decorators import calculation_function
from data_calculation.models import DataCalculation
from cerem.tasks import insert_collection
from core.utils import ForestTimer, bulk_update

from ..team_extension.models import PurchaseBase

COLLECTION_ORDERPRODUCT = 'retail_orderproduct'
COLLECTION_PURCHASEBASE = 'retail_purchasebase'

@app.task(bind=True)
@calculation_function
def calculate_order_ordinal(team_id, *args, **kwargs):

    ft = kwargs.get('ft')

    if ft is None:

        ft = ForestTimer()

    if team_id is None:
        return False

    team = Team.objects.filter(id=team_id).only('id').first()

    if team is None:
        return False

    qs = team.purchasebase_set.filter(removed=False, status_key=PurchaseBase.STATUS_CONFIRMED)

    orders_of_clients = qs.values('clientbase_id').annotate(orders=ArrayAgg('id', ordering='datetime'))

    ft.for_step(f'{team}: build orders_of_clients')

    items_to_update = []

    for orders_data in orders_of_clients:

        orders = orders_data['orders']

        for ordinal, order in enumerate(orders):

            obj = PurchaseBase(id=order, ordinal=ordinal + 1)

            items_to_update.append(obj)

    ft.for_step(f'{team}: loop orders_of_clients done')

    items_to_update, is_deleted = bulk_update(team.slug, PurchaseBase, items_to_update, ['ordinal'], ft)

    return True


@app.task(bind=True)
@calculation_function
def sync_cerem__retail(team_id, *args, **kwargs):
    data_calculation_id = kwargs.get('data_calculation_id')
    team = Team.objects.get(id=team_id)

    data_calculation = DataCalculation.objects.get(id=data_calculation_id)
    datetime_min = data_calculation.data_datetime_min
    datetime_max = data_calculation.data_datetime_max

    order_list_ids = list(
        team.orderlist_set.filter(order_datetime_min__lte=datetime_max, order_datetime_max__gte=datetime_min)
        .values_list('id', flat=True)
    )


    team = Team.objects.get(id=team_id)
    # purchasebase
    qs = team.purchasebase_set.available_only()

    data = {}
    data = list(
        qs.values(
            'c_at',
            'u_at',
            'external_id',
            'total_price',
            'status_key',
            'datetime',
            'ordinal',
            'datasource_id',
            'clientbase_id',
            clientbase_external_id=F('clientbase__external_id'),
            clientbase_mobile=F('clientbase__mobile'),
            clientbase_email=F('clientbase__email'),
            postgre_id=F('id')
        )
    )
    insert_collection(team_id, COLLECTION_PURCHASEBASE, data)

    # orderproduct

    qs = team.orderproduct_set.available_only().filter(orderbase__orderlist_ids__overlap=order_list_ids)

    data = {}
    data = list(
        qs.values(
            'c_at',
            'u_at',
            'productbase_id',
            'clientbase_id',
            'orderbase_id',
            'quantity',
            'total_price',
            'datetime',
            category_ids=F('productbase__category_ids'),
            postgre_id=F('id'),
            orderbase_ordinal=F('orderbase__ordinal'),
            datasource_id=F('orderbase__datasource_id'),
            status_key=F('orderbase__status_key'),
            internal_product=F('productbase__internal_product'),
            clientbase_email=F('clientbase__email'),
            clientbase_mobile=F('clientbase__mobile'),
            clientbase_external_id=F('clientbase__external_id'),
        )
    )
    insert_collection(team_id, COLLECTION_ORDERPRODUCT, data)
