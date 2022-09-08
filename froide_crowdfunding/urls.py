from django.urls import path

from .views import (
    CrowdfundingDetailView,
    CrowdfundingListView,
    request_crowdfunding,
    start_contribution,
    start_contribution_donation,
)

urlpatterns = [
    path("edit/", CrowdfundingListView.as_view(), name="crowdfunding-edit"),
    path(
        "contribute/<int:pk>/",
        start_contribution,
        name="crowdfunding-start_contribution",
    ),
    path(
        "contribute/<int:pk>/donate/",
        start_contribution_donation,
        name="crowdfunding-start_contribution_donation",
    ),
    path("request/<int:pk>/", request_crowdfunding, name="crowdfunding-request"),
    path(
        "campaign/<slug:slug>/",
        CrowdfundingDetailView.as_view(),
        name="crowdfunding-detail",
    ),
]
