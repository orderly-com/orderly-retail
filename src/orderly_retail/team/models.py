from team.models import OrderBase, ProductBase


class PurchaseBase(OrderBase):
    class Meta:
        proxy = True


class SkuBase(ProductBase):
    class Meta:
        proxy = True

