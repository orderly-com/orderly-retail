from django.db import models

from team.models import ProductBase, ClientBase, OrderBase


class SkuBase(ProductBase):
    class Meta:
        proxy = True


class PurchaseBase(OrderBase):
    class Meta:
        indexes = [
            models.Index(fields=['team', ]),
            models.Index(fields=['clientbase']),
            models.Index(fields=['uniq_id']),

            models.Index(fields=['team', 'external_id']),
            models.Index(fields=['team', 'datetime']),
            models.Index(fields=['team', 'delivery_datetime']),
            models.Index(fields=['team', 'clientbase']),
            models.Index(fields=['team', 'uniq_id']),


            models.Index(fields=['team', 'external_id', 'datasource_id']),
            models.Index(fields=['team', 'status_key', 'removed']),
            models.Index(fields=['team', 'clientbase', 'datetime']),

        ]

    # total price, get from order data
    total_price = models.FloatField(default=0)

    # list of status_key
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_ABANDONED = 'ABANDONED'
    STATUS_KEEP = 'KEEP'

    # OrderStatus
    status = models.CharField(max_length=64, blank=False, null=False, default='')
    status_key = models.CharField(max_length=64, blank=False, null=False, default='')  # CONFIRMED, ABANDONED or KEEP

    # shipping_address
    shipping_address = models.CharField(max_length=512, blank=True, null=True, default='')

    # shipping_cost
    shipping_cost = models.FloatField(default=0)

    def get_purchase_behaviors(self):

        from orderly.models import DataSource

        if self.team.has_child:
            teams = self.team.get_children()
            orderbase_qs = PurchaseBase.objects.filter(team__in=teams, removed=False).order_by('-datetime')

        else:
            orderbase_qs = PurchaseBase.objects.filter(team=self.team, removed=False).order_by('-datetime')

        datasource_dict = {}

        behaviors = []

        # # orderbases
        qs = orderbase_qs.filter(clientbase=self).only('id', 'datetime', 'status_key', 'total_price')

        for orderbase in qs.all():

            if orderbase.datasource_id in datasource_dict:
                datasource = datasource_dict[orderbase.datasource_id]
            else:

                _ = DataSource.objects.filter(id=orderbase.datasource_id).only('id').first()

                datasource = {
                    'name': _.get_family_root_name(),
                    'url': _.get_detail_url(),
                }

                datasource_dict[orderbase.datasource_id] = datasource

            obj = {
                'datetime': orderbase.datetime,
                'trigger_by': 'client',
                'action': orderbase.status_key,
                'value': orderbase.total_price,
                'data': {
                    'action': orderbase.status_key,
                    'datasource': datasource,
                    'orderbase': {'url': orderbase.get_detail_url(), 'external_id': orderbase.external_id},
                    'orderproducts': list(orderbase.orderproduct_set.exclude(productbase__internal_product=True).values('external_id', 'productbase__uuid', 'name', 'spec', 'price', 'quantity', 'refound', 'append')),
                },
            }

            behaviors.append(obj)

        return behaviors


class OrderProduct(BaseModel):

    class Meta:
        indexes = [
            models.Index(fields=['team', ]),
            models.Index(fields=['productbase', ]),
            models.Index(fields=['orderbase', ]),
            models.Index(fields=['clientbase', ]),

            models.Index(fields=['team', 'productbase']),
            models.Index(fields=['team', 'orderbase']),
            models.Index(fields=['team', 'clientbase']),
        ]

    # remove later
    had_sync = models.BooleanField(default=False)

    team = models.ForeignKey(Team, blank=False, on_delete=models.CASCADE)
    orderlist_id = models.IntegerField(blank=True, null=True)  # so we can trace back to it's original orderlist
    uploadedfile_id = models.IntegerField(blank=True, null=True)  # so we can trace back to it's uploadedfile # NOT IMPLEMENTED

    productbase = models.ForeignKey(ProductBase, blank=False, null=False, on_delete=models.CASCADE)
    orderbase = models.ForeignKey(OrderBase, blank=False, null=False, on_delete=models.CASCADE)
    clientbase = models.ForeignKey(ClientBase, blank=False, null=True, default=None, on_delete=models.CASCADE)

    datetime = models.DateTimeField(blank=False, null=False)  # orderbase.datetime

    # from raw data
    external_id = models.CharField(max_length=256, blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    spec = models.CharField(max_length=128, blank=True, null=True)
    # end

    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    total_price = models.FloatField(default=0.0)  # calculated subtotal by price * quantity
    total_price_raw = models.FloatField(default=0.0)  # subtotal from raw data

    original_price = models.FloatField(default=0.0)  # 原價
    cost = models.FloatField(default=0.0)   # 成本
    gross_margin = models.FloatField(default=0.0)   # 毛利
    shipping_cost = models.FloatField(default=0)  # 運費

    refound = models.BooleanField(default=False)
    append = models.BooleanField(default=False)

    objects = models.Manager()

    product_relativity_calculated = models.BooleanField(default=False)

    MANUAL_FIELDS = [
        'manual_external_id', 'manual_name', 'manual_spec', 'manual_price', 'manual_quantity',
        'manual_total_price', 'manual_cost', 'manual_shipping_cost',
        'manual_original_price',
    ]
    # if the OrderProduct has been updated manually, ORDERLY won't update it anymore
    manual_updated = models.BooleanField(default=False)
    manual_external_id = models.CharField(max_length=256, blank=True, null=True, default=None)
    manual_name = models.CharField(max_length=512, blank=True, null=True, default=None)
    manual_spec = models.CharField(max_length=128, blank=True, null=True, default=None)
    manual_price = models.FloatField(null=True, blank=True, default=None)
    manual_quantity = models.FloatField(null=True, blank=True, default=None)
    manual_total_price = models.FloatField(null=True, blank=True, default=None)

    manual_original_price = models.FloatField(null=True, blank=True, default=None)
    manual_cost = models.FloatField(null=True, blank=True, default=None)
    manual_shipping_cost = models.FloatField(null=True, blank=True, default=None)
    # manual_updated_by = models.ManyToManyField(User, blank=True)
    # *********

    def get_original_price(self, check_manual=True):
        original = self.original_price
        manual = self.manual_original_price

        if check_manual is False:
            return original

        if original == manual:
            return original

        if manual is None:
            return original

        return manual

    def get_price(self, check_manual=True):
        original = self.price
        manual = self.manual_price

        if check_manual is False:
            return original

        if original == manual:
            return original

        if manual is None:
            return original

        return manual

    def get_quantity(self, check_manual=True):
        original = self.quantity
        manual = self.manual_quantity

        if check_manual is False:
            return original

        if original == manual:
            return original

        if manual is None:
            return original

        return manual

    def get_cost(self, check_manual=True):
        original = self.cost
        manual = self.manual_cost

        if check_manual is False:
            return original

        if original == manual:
            return original

        if manual is None:
            return original

        return manual

    def get_total_price(self, check_manual=True):
        original = self.total_price
        manual = self.manual_total_price

        if check_manual is False:
            return original

        if original == manual:
            return original

        if manual is None:
            return original

        return manual

    def get_display_with_id(self):

        display = ''

        if self.name != 'UNKNOWN' and self.name != '' and self.name != 'None':
            display = self.name

        if self.spec != '' and self.spec is not None and self.spec != 'None':
            display = f'{display}-{self.spec}'

        if self.productbase.unit != '' and self.productbase.unit is not None and self.productbase.unit != 'None':
            display = f'{display}({self.productbase.unit})'

        if len(self.productbase.external_id) > 0:
            display = f'[{self.productbase.external_id}] {display}'

        return display

    # ref: https://app.asana.com/0/1125673157918636/1137444066434769
    @staticmethod
    def set_price_equal_to_new_price(team_slug, old_price, new_price):

        # to run
        # from team.models import OrderProduct
        # OrderProduct.set_price_equal_to_new_price('newwis', -411, -1)

        team = Team.objects.filter(slug=team_slug).first()

        if team is None:
            # print('Team slug: {} is not found.'.format(team_slug))
            return False

        if team.cleanable is False:
            # print('Cleanable is False.')
            return False

        if None in [old_price, new_price]:
            # print('old_price or new_price is None.')
            return False

        # build qs
        qs = team.orderproduct_set.filter(price=old_price, total_price_raw=new_price, original_price=new_price)

        # print data which will be updated
        # print('total: {}'.format(qs.count()))
        # print(qs.values_list('id', flat=True)[::1])

        for item in qs:

            # print('update {}'.format(item.id))

            item.price = new_price
            item.total_price = item.price * item.quantity

            item.save()

        # print('Done')

        return True

