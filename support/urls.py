# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, TicketAssignmentViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
    path('agent/tickets/', TicketAssignmentViewSet.as_view({
        'get': 'get_assigned_tickets',
        'post': 'update_status'
    }), name='agent-tickets'),
]