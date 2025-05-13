# views.py
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Ticket, TicketAssignment, User
from .serializers import TicketSerializer, TicketAssignmentSerializer , TicketStatusUpdateSerializer
from .permissions import IsAdminOrReadOnly, IsAgent
#import asyncio
from django.core.cache import cache
#from rest_framework.views import APIView

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TicketAssignmentViewSet(viewsets.ViewSet):
#class TicketAssignmentViewSet(APIView):

    permission_classes = [IsAuthenticated, IsAgent]
    
    @action(detail=False, methods=['get'])
    def get_assigned_tickets(self, request):
        
        agent = request.user
        MAX_TICKETS = 15

        while True:  # Retry loop for optimistic concurrency
            try:
                
                with transaction.atomic():
                    # Get currently active assignments
                    active_assignments =  TicketAssignment.objects.filter(
                        agent=agent,
                        is_active=True
                    ).select_related('ticket').order_by('assigned_at')
                    
                    active_count = active_assignments.count()
                    
                    if active_count >= MAX_TICKETS:
                        serializer = TicketAssignmentSerializer(active_assignments[:MAX_TICKETS], many=True)
                        #cache.set(cache_key, serializer.data, timeout=300)
                        return Response(serializer.data)
                    
                    # Calculate how many more tickets we need
                    needed = MAX_TICKETS - active_count
                    
                    if needed > 0:
                        # Find unassigned tickets
                        unassigned_tickets =  Ticket.objects.filter(
                            status='open'
                        ).exclude(
                            assignments__is_active=True
                        ).order_by('created_at')[:needed]
                        
                        # Create new assignments
                        new_assignments = []
                        for ticket in unassigned_tickets:
                            assignment = TicketAssignment(
                                ticket=ticket,
                                agent=agent,
                                is_active=True
                            )
                            new_assignments.append(assignment)
                            ticket.status = 'assigned'
                            ticket.save()
                        
                        TicketAssignment.objects.bulk_create(new_assignments)
                        
                        # Refresh the queryset to include new assignments
                        active_assignments =  TicketAssignment.objects.filter(
                            agent=agent,
                            is_active=True
                        ).select_related('ticket').order_by('assigned_at')[:MAX_TICKETS]
                    
                    serializer = TicketAssignmentSerializer(active_assignments, many=True)
                    #cache.set(cache_key, serializer.data, timeout=300)
                    #print("hi we are in the view get method")
                    return Response(serializer.data)
            except DatabaseError:
                continue  # Retry on conflict
        

    @action(detail=False, methods=['post'])
    def update_status(self, request):
        serializer = TicketStatusUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        ticket_id = serializer.validated_data['ticket_id']
        new_status = serializer.validated_data['status']
        
        with transaction.atomic():
            ticket =  Ticket.objects.get(id=ticket_id)
            ticket.status = new_status
            ticket.save()
            
            # If ticket is resolved or closed, mark assignment as inactive
            if new_status in ['resolved', 'closed']:
                TicketAssignment.objects.filter(
                    ticket_id=ticket_id,
                    agent=request.user
                ).update(is_active=False)
        
        return Response({'status': 'success'})