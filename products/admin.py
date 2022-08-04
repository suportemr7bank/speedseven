"""
Admin site
"""

from django.contrib import admin

from .models import ProfileProduct, AgreementTemplate, ProductPurchase, Product, ProductCategory


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product admin model
    """


@admin.register(ProfileProduct)
class ProfileProductAdmin(admin.ModelAdmin):
    """
    Profile product admin model
    """


@admin.register(AgreementTemplate)
class AgreementTemplateAdmin(admin.ModelAdmin):
    """
    Agreement template admin model
    """


@admin.register(ProductPurchase)
class ProductPurchaseAdmin(admin.ModelAdmin):
    """
    Product purchase admin model
    """

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """
    Product category admin model
    """
