from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from rest_framework.test import APIClient
from .models import Category, Transaction, Budget
from .services import check_anomaly, predict_next_month, suggest_budget

class FinanceTrackerTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.category1 = Category.objects.create(name='Food', user=self.user1)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_no_anomaly_for_normal_transaction(self):
        amounts = [500, 600, 700, 800, 900]
        for amount in amounts:
            Transaction.objects.create(
                user=self.user1, category=self.category1, amount=amount, type='expense', date=timezone.now().date()
            )
        
        t = Transaction(user=self.user1, category=self.category1, amount=750, type='expense', date=timezone.now().date())
        is_anomaly, reason = check_anomaly(t)
        self.assertFalse(is_anomaly)

    def test_anomaly_flagged_for_high_amount_with_history(self):
        for i in range(5):
            Transaction.objects.create(
                user=self.user1, category=self.category1, amount=100, type='expense', date=timezone.now().date()
            )
        
        t = Transaction(user=self.user1, category=self.category1, amount=1000, type='expense', date=timezone.now().date())
        is_anomaly, reason = check_anomaly(t)
        self.assertTrue(is_anomaly)
        self.assertIn("exceeds 2 std deviations", reason)

    def test_anomaly_flagged_cold_start_rule(self):
        t = Transaction(user=self.user1, category=self.category1, amount=6000, type='expense', date=timezone.now().date())
        is_anomaly, reason = check_anomaly(t)
        self.assertTrue(is_anomaly)
        self.assertIn("cold start rule", reason)

    def test_predict_uses_linear_regression_with_enough_data(self):
        # Create data for 4 different months
        for i in range(4):
            date = timezone.now().date().replace(day=1) - relativedelta(months=i)
            Transaction.objects.create(
                user=self.user1, category=self.category1, amount=100, type='expense', date=date
            )
        
        result = predict_next_month(self.user1, self.category1)
        self.assertEqual(result['method'], 'linear_regression')

    def test_predict_uses_moving_average_with_insufficient_data(self):
        # Create data for 2 different months
        for i in range(2):
            date = timezone.now().date().replace(day=1) - relativedelta(months=i)
            Transaction.objects.create(
                user=self.user1, category=self.category1, amount=100, type='expense', date=date
            )
        
        result = predict_next_month(self.user1, self.category1)
        self.assertEqual(result['method'], 'moving_average')

    def test_suggest_budget_returns_warning_when_over_80_percent(self):
        current_month = timezone.now().date().replace(day=1)
        Budget.objects.create(user=self.user1, category=self.category1, monthly_limit=1000, month=current_month)
        
        # Spend 850 (85%)
        Transaction.objects.create(
            user=self.user1, category=self.category1, amount=850, type='expense', date=current_month
        )
        
        result = suggest_budget(self.user1, self.category1)
        self.assertEqual(result['warning'], 'approaching_limit')

    def test_user_cannot_access_another_users_transactions(self):
        cat2 = Category.objects.create(name='Travel', user=self.user2)
        t2 = Transaction.objects.create(
            user=self.user2, category=cat2, amount=500, type='expense', date=timezone.now().date()
        )
        
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
