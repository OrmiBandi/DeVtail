from django.urls import path
from .views import (
    DevMateListView,
    DevMateReceivedListView,
    DevMateCreateView,
    DevMateUpdateView,
    DevMateDeleteView,
)

app_name = "devmates"

urlpatterns = [
    path("list/", DevMateListView.as_view(), name="devmate_list"),
    path(
        "received-list/",
        DevMateReceivedListView.as_view(),
        name="devmate_received_list",
    ),
    path("apply/<int:pk>/", DevMateCreateView.as_view(), name="devmate_create"),
    path("accept/<int:pk>/", DevMateUpdateView.as_view(), name="devmate_update"),
    path("reject/<int:pk>/", DevMateDeleteView.as_view(), name="devmate_delete"),
]
