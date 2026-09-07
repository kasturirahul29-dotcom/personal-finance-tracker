from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Category, Transaction, Budget
from .serializers import CategorySerializer, TransactionSerializer, BudgetSerializer
from .permissions import IsOwner
from .services import check_anomaly, predict_next_month, suggest_budget
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    
    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
        
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }, status=status.HTTP_201_CREATED)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        month = self.request.query_params.get('month')
        if month:
            # Assumes YYYY-MM
            queryset = queryset.filter(date__startswith=month)
            
        type_param = self.request.query_params.get('type')
        if type_param:
            queryset = queryset.filter(type=type_param)
            
        return queryset

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        # Check for anomaly
        is_anomaly, reason = check_anomaly(transaction)
        if is_anomaly:
            transaction.is_anomaly = True
            transaction.anomaly_reason = reason
            transaction.save()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_anomalies(request):
    transactions = Transaction.objects.filter(user=request.user, is_anomaly=True)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        queryset = Budget.objects.filter(user=self.request.user)
        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(month=month)
        return queryset
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_budget_suggestions(request):
    category_id = request.query_params.get('category')
    if not category_id:
        return Response({"error": "Category required"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        category = Category.objects.get(id=category_id, user=request.user)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
    result = suggest_budget(request.user, category)
    return Response(result)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_dashboard_summary(request):
    month = request.query_params.get('month')
    if not month:
        return Response({"error": "Month (YYYY-MM-01) required"}, status=status.HTTP_400_BAD_REQUEST)
        
    year, mon, _ = month.split('-')
    
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=year,
        date__month=mon
    )
    
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    
    by_category_data = transactions.filter(type='expense').values('category__name').annotate(total=Sum('amount'))
    by_category = [{"category": item['category__name'], "total": float(item['total'])} for item in by_category_data]
    
    budgets = Budget.objects.filter(user=request.user, month=month)
    budget_serializer = BudgetSerializer(budgets, many=True)
    
    return Response({
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "by_category": by_category,
        "budgets": budget_serializer.data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_predictions(request):
    category_id = request.query_params.get('category')
    if not category_id:
        return Response({"error": "Category required"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        category = Category.objects.get(id=category_id, user=request.user)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        
    result = predict_next_month(request.user, category)
    return Response(result)
