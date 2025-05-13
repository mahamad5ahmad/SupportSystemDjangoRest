

# tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Ticket
import threading
from rest_framework.test import APIRequestFactory
from django.test import TransactionTestCase  # Changed from TestCase
from django.test import AsyncClient, TestCase
import asyncio

User = get_user_model()

class TicketAssignmentTests(TransactionTestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        self.agent1 = User.objects.create_user(
            username='agent1',
            email='agent1@example.com',
            password='password',
            is_agent=True
        )
        self.agent2 = User.objects.create_user(
            username='agent2',
            email='agent2@example.com',
            password='password',
            is_agent=True
        )
        
        # Create some tickets
        for i in range(75):
            Ticket.objects.create(
                title=f'Ticket {i}',
                description=f'Description {i}',
                created_by=self.admin
            )
        
        self.client1 = APIClient()
        self.client2=APIClient()
        self.client1.force_authenticate(user=self.agent1)
        self.client2.force_authenticate(user=self.agent2)




    def test_agent_ticket_assignment(self):
        # Agent1 login
        self.client1.force_authenticate(user=self.agent1)
        
        # First request - should get 15 tickets
        response =  self.client1.get('/api/agent/tickets/')
        #print(response.data )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 15)
        
        # Second request - should get same 15 tickets
        response =  self.client1.get('/api/agent/tickets/')
        #print(response.data )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 15)
        
        # Agent2 login - should get different 15 tickets
        self.client2.force_authenticate(user=self.agent2)
        response =  self.client2.get('/api/agent/tickets/')
        #print(response.data )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 15)
        
        # Check that agents got different tickets
        agent1_tickets = set(ta['ticket']['id'] for ta in 
                             self.client1.get('/api/agent/tickets/').data)
        agent2_tickets = set(ta['ticket']['id'] for ta in 
                             self.client2.get('/api/agent/tickets/').data)
        self.assertTrue(agent1_tickets.isdisjoint(agent2_tickets))


    # tests.py (additional tests)
    def test_agent_can_update_status(self):
        self.client1.force_authenticate(user=self.agent1)
        
        # First get some tickets
        response = self.client1.get('/api/agent/tickets/')
        #print(response.data )
        ticket_id = response.data[0]['ticket']['id']
        
        # Update status to in_progress
        response = self.client1.post('/api/agent/tickets/', {
            'ticket_id': ticket_id,
            'status': 'resolved'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        
        # Verify status changed
        ticket = Ticket.objects.get(id=ticket_id)
        self.assertEqual(ticket.status, 'resolved')
        
        # Try invalid transition
        response = self.client1.post('/api/agent/tickets/', {
            'ticket_id': ticket_id,
            'status': 'assigned'
        }, format='json')
        self.assertEqual(response.status_code, 400)  



    def test_concurrent_ticket_assignment(self):
        
        #self.client1.force_authenticate(user=self.agent1)
        #self.client2.force_authenticate(user=self.agent2)
        # Verify no overlapping tickets
        response1 = self.client1.get('/api/agent/tickets/')
        response2 = self.client2.get('/api/agent/tickets/')
        results1 = [t['ticket']['id'] for t in response1.data]
        results2 = [t['ticket']['id'] for t in response2.data]
        agent1_tickets = set(results1)
        agent2_tickets = set(results2)
        self.assertTrue(
            agent1_tickets.isdisjoint(agent2_tickets),
            f"Overlapping tickets found: {agent1_tickets & agent2_tickets}"
        )

        results = {'agent1': [], 'agent2': []}
        errors = []
        
        def fetch_tickets(client, agent_name):  
             
            while(True):     
                try:
                    response = client.get('/api/agent/tickets/')
                    #print("the response")
                    #print(response.data)
                    results[agent_name] = [t['ticket']['id'] for t in response.data]
                    return
                except Exception as e:
                    errors.append(str(e))
                    
        
        # Create threads
        thread1 = threading.Thread(
            target=fetch_tickets,
            args=(self.client1, 'agent1')
        )
        thread2 = threading.Thread(
            target=fetch_tickets,
            args=(self.client2, 'agent2')
        )
        
        # Start threads
        thread1.start()
        thread2.start()
        
        # Wait for completion
        thread1.join()
        thread2.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        
        # Verify no overlapping tickets
        agent1_tickets = set(results['agent1'])
        agent2_tickets = set(results['agent2'])
        self.assertTrue(
            agent1_tickets.isdisjoint(agent2_tickets),
            f"Overlapping tickets found: {agent1_tickets & agent2_tickets}"
        )
        
        # Verify correct number of tickets
        self.assertEqual(len(agent2_tickets), 15)
        self.assertEqual(len(agent1_tickets), 15)

   