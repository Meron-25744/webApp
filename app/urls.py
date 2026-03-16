from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('experiences/', views.ExperienceListView.as_view(), name='experience_list'),
    path('experience/<slug>', views.ExperienceDetailView.as_view(), name='experience_detail'),
    path('experience/<slug>/reserve', views.reserve_experience, name='experience_reserve'),
    path('experience/thanks/', views.ExperienceThanksView.as_view(), name='experience_thanks'),
    path('product/<slug>', views.ItemDetailView.as_view(), name='product'),
    path('additem/<slug>', views.addItem, name='additem'),
    path('order/', views.OrderView.as_view(), name='order'),
    path('removeitem/<slug>', views.removeItem, name='removeitem'),
    path('removesingleitem/<slug>', views.removeSingleItem, name='removesingleitem'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('thanks/', views.ThanksView.as_view(), name='thanks'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('add/', views.ItemCreateView.as_view(), name='product_add'),
    path('add_experience/', views.ExperienceCreateView.as_view(), name='experience_add'),
    path('seller/dashboard/', views.SellerDashboardView.as_view(), name='seller_dashboard'),
    path('my/reservations/', views.UserReservationsView.as_view(), name='user_reservations'),
]