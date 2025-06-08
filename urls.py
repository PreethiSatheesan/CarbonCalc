
from django.urls import path
from .views import calculate_footprint, home, history_view, monthly_history_data,logout_view,login_view, register

urlpatterns = [
    path('', home, name='home'),
    #path('cacc/',calculate, name='calculate'),
    path('calculate/', calculate_footprint, name='calculate_footprint'),
    path('history/', history_view, name='history_view'),  # 👈 New route for the history page
    path('login/', login_view, name='login'),
    path('register/',register, name='register'),
    path('monthly-history-data/', monthly_history_data, name='monthly-history-data'),  # 👈 JSON data endpoint
    path('logout/', logout_view, name='logout'), # 👈 Add this line
    #path('generate-pdf/', generate_pdf, name='generate_pdf'),

    
]
