from rest_framework import serializers
from .models import Ticket, TicketAssignment

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

class TicketAssignmentSerializer(serializers.ModelSerializer):
    ticket = TicketSerializer(read_only=True)
    
    class Meta:
        model = TicketAssignment
        fields = '__all__'
        read_only_fields = ('assigned_at',)


class TicketStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES)
    ticket_id = serializers.IntegerField()

    def validate(self, data ):
        ticket = Ticket.objects.get(id=data['ticket_id'])
        current_status = ticket.status
        new_status = data['status']
        
        valid_transitions = {
            'assigned': ['resolved'],
            'resolved': ['closed'],
            'closed': []
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {new_status}"
            )
        
        request = self.context['request']
        TickAssign=TicketAssignment.objects.filter(
                    ticket_id=data['ticket_id'],
                    agent=request.user)
        if not TickAssign :
            raise serializers.ValidationError(
                f"The user Cannot change this Ticket , It is not assigned to him"
            )
        
        return data      