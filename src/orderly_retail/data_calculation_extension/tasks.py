from config.celery import app
from data_calculation.decorators import calculation_function
from django.contrib.postgres.aggregates import ArrayAgg
from core.utils import ForestTimer, bulk_update
from team.models import Team
from ..team_extension.models import PurchaseBase

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
