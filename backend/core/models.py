from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")

    class Meta:
        unique_together = ("name", "user")

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TYPE_CHOICES = [("income", "Income"), ("expense", "Expense")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    is_anomaly = models.BooleanField(default=False)
    anomaly_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
        ]
        ordering = ["-date"]


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="budgets")
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()  # store as first day of the month, e.g. 2026-09-01

    class Meta:
        unique_together = ("user", "category", "month")
