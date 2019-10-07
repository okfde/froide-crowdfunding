from django.conf.urls import url

from .views import (
    request_crowdfunding, start_contribution,
    start_contribution_donation,
    CrowdfundingListView, CrowdfundingDetailView
)

urlpatterns = [
    url(r'^$', CrowdfundingListView.as_view(), name='crowdfunding-index'),
    url(r'^edit/$', CrowdfundingListView.as_view(), name='crowdfunding-edit'),
    url(r'^contribute/(?P<pk>\d+)/$', start_contribution,
        name='crowdfunding-start_contribution'),
    url(r'^contribute/(?P<pk>\d+)/donate/$', start_contribution_donation,
        name='crowdfunding-start_contribution_donation'),
    url(r'^request/(?P<pk>\d+)/$', request_crowdfunding,
        name='crowdfunding-request'),
    url(r'^campaign/(?P<slug>[\w-]+)/$', CrowdfundingDetailView.as_view(),
        name='crowdfunding-detail'),
]
