from .models import OrderProduct, OrderBase

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):

    readonly_fields = (
        'uploadedfile_id', 'productbase', 'orderbase', 'clientbase', 'orderlist_id',
        'quantity', 'total_price_raw', 'original_price', 'cost', 'gross_margin', 'shipping_cost',
        'c_at',
    )

    list_display = (
        'id',
        'c_at',
        'u_at',
        'datetime',
        'team',
        'orderbase',
        'external_id',
        'refound',
        'append',
        'name',
        'spec',
        'price',
        'quantity',
        'total_price',
        'total_price_raw',
        'original_price',
        'cost',
        'gross_margin',
        'shipping_cost',

        # 'orderlist_id',
        # 'uploadedfile_id',
        'productbase',
        'clientbase',

    )

    list_editable = ('refound', 'append')

    list_filter = ('team', 'refound', 'append')

    search_fields = ('orderlist_id', 'orderbase__external_id', 'id')



@admin.register(OrderBase)
class OrderBaseAdmin(admin.ModelAdmin):

    readonly_fields = (
        'u_at', 'orderlist_id', 'orderlist_ids', 'orderrow_ids', 'order_ids', 'client_ids',
        'product_ids', 'tags', 'tag_ids', 'clientbase',
    )

    list_display = (
        'id',
        'team',
        'has_product_refound',
        'has_product_append',
        'get_datasource',
        'orderlist_id',
        'external_id',
        'get_clientbase_id',
        'datetime',
        'delivery_datetime',
        'shipping_cost',
        'status',
        'total_price',
        'total_paid',
        'shipping_cost',
        'shipping_cost',
    )

    list_editable = ('has_product_refound', 'has_product_append')

    list_filter = ('team',)

    search_fields = ('team__slug', 'team__name', 'external_id', 'id', 'clientbase__id')

