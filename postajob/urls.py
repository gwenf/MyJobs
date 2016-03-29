from django.conf.urls import patterns, url
from django.http import Http404

from postajob import models, views


def raise_404(*args, **kwargs):
    # TODO: Fix FormViewBase so I don't have to do this
    raise Http404("postajob.urls: Can't delete products")


urlpatterns = patterns(
    '',

    # Views for job and admin
    url(r'^order/',
        views.order_postajob,
        name="order_postajob"),
    url(r'list/$', views.product_listing, name='product_listing'),

    # Posted job management
    url(r'^all/$',
        views.jobs_overview,
        name='jobs_overview'),

    # Purchased job management
    url(r'^purchased-jobs/$', views.purchasedproducts_overview,
        name='purchasedproducts_overview'),
    url(r'purchased-jobs/product/(?P<purchased_product>\d+)/view/(?P<pk>\d+)$',
        views.view_job, {'admin': False}, name='view_job'),
    url(r'^purchased-jobs/product/(?P<purchased_product>\d+)/',
        views.purchasedjobs_overview, {'admin': False},
        name='purchasedjobs_overview'),

    # Purchased microsite management
    url(r'^admin/$', views.purchasedmicrosite_admin_overview,
        name='purchasedmicrosite_admin_overview'),

    # Invoices
    url(r'^admin/invoice/(?P<pk>\d+)/$', views.resend_invoice,
        name='resend_invoice'),

    # Requests
    url(r'^admin/request/$', views.admin_request, name='request'),
    url(r'^admin/request/view/(?P<pk>\d+)/$', views.view_request,
        name='view_request'),
    url(r'^admin/request/approve/(?P<pk>\d+)/$', views.process_admin_request,
        {'approve': True, 'block': False}, name='approve_admin_request'),
    url(r'^admin/request/deny/(?P<pk>\d+)/$', views.process_admin_request,
        {'approve': False, 'block': False}, name='deny_admin_request'),
    url(r'^admin/request/block/(?P<pk>\d+)/$', views.process_admin_request,
        {'approve': False, 'block': True}, name='block_admin_request'),

    # Job
    url(r'^job/add/',
        views.JobFormView.as_view(),
        name='job_add'),
    url(r'^job/delete/(?P<pk>\d+)/',
        views.JobFormView.as_view(),
        name='job_delete'),
    url(r'^job/update/(?P<pk>\d+)/',
        views.JobFormView.as_view(),
        name='job_update'),

    # PurchasedJob
    url(r'^job/purchase/add/(?P<product>\d+)/',
        views.PurchasedJobFormView.as_view(),
        name='purchasedjob_add'),
    url(r'^job/purchase/update/(?P<pk>\d+)/',
        views.PurchasedJobFormView.as_view(),
        name='purchasedjob_update'),
    url(r'^job/purchase/delete/(?P<pk>\d+)/',
        views.PurchasedJobFormView.as_view(),
        name='purchasedjob_delete'),

    # Product management
    url(r'^admin/product/$',  views.admin_products, name='product'),
    url(r'^admin/product/add/', views.ProductFormView.as_view(),
        name='product_add'),
    url(r'^admin/product/delete/(?P<pk>\d+)/', raise_404,
        name='product_delete'),
    url(r'^admin/product/update/(?P<pk>\d+)/', views.ProductFormView.as_view(),
        name='product_update'),

    # ProductGrouping
    url(r'^admin/product/group/$', views.admin_groupings,
        name='productgrouping'),
    url(r'^admin/product/group/add/', views.ProductGroupingFormView.as_view(),
        name='productgrouping_add'),
    url(r'^admin/product/group/delete/(?P<pk>\d+)/',
        views.ProductGroupingFormView.as_view(),
        name='productgrouping_delete'),
    url(r'^admin/product/group/update/(?P<pk>\d+)/',
        views.ProductGroupingFormView.as_view(),
        name='productgrouping_update'),

    # Offline Purchases
    url(r'^admin/purchase/offline/$', views.admin_offlinepurchase,
        name='offlinepurchase'),
    url(r'^admin/purchase/offline/add/',
        views.OfflinePurchaseFormView.as_view(), name='offlinepurchase_add'),
    url(r'^admin/purchase/offline/delete/(?P<pk>\d+)/',
        views.OfflinePurchaseFormView.as_view(),
        name='offlinepurchase_delete'),
    url(r'^admin/purchase/offline/update/(?P<pk>\d+)/',
        views.OfflinePurchaseFormView.as_view(),
        name='offlinepurchase_update'),

    url(r'^purchase/redeem/$',
        views.OfflinePurchaseRedemptionFormView.as_view(),
        name='offlinepurchase_redeem'),
    url(r'^admin/purchase/offline/success/(?P<pk>\d+)/$', views.view_request,
        {'model': models.OfflinePurchase}, name='offline_purchase_success'),

    # PurchasedProduct
    url(r'^product/purchase/add/(?P<product>\d+)/',
        views.PurchasedProductFormView.as_view(),
        name='purchasedproduct_add'),
    url(r'^product/purchase/delete/(?P<pk>\d+)/',
        views.PurchasedProductFormView.as_view(),
        name='purchasedproduct_delete'),
    url(r'^product/purchase/update/(?P<pk>\d+)/',
        views.PurchasedProductFormView.as_view(),
        name='purchasedproduct_update'),

    url(r'^admin/purchased/product$', views.admin_purchasedproduct,
        name='purchasedproduct'),
    url(r'^admin/purchased/product/(?P<purchased_product>\d+)/view/(?P<pk>\d+)$',
        views.view_job, {'admin': True}, name="admin_view_job"),
    url(r'^admin/purchased/product/(?P<purchased_product>\d+)/view-invoice',
        views.view_invoice, name="admin_view_invoice"),
    url(r'^admin/purchased/product/(?P<purchased_product>\d+)/',
        views.purchasedjobs_overview, {'admin': True}, name="purchasedjobs"),

    # CompanyProfile
    url(r'^admin/profile/',
        views.CompanyProfileFormView.as_view(),
        name='companyprofile_add'),
    url(r'^admin/profile/delete/(?P<pk>\d+)/',
        views.CompanyProfileFormView.as_view(),
        name='companyprofile_delete'),
    url(r'^admin/profile/update/(?P<pk>\d+)/',
        views.CompanyProfileFormView.as_view(),
        name='companyprofile_update'),

    # User management
    url(r'^admin/blocked-users/$', views.blocked_user_management,
        name='blocked_user_management'),
    url(r'^admin/blocked-users/unblock/(?P<pk>\d+)/$', views.unblock_user,
        name='unblock_user'),

    url(r'^sites/$',
        views.SitePackageFilter.as_view(),
        name='site_fsm'),
)
