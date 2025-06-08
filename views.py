
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth, User

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.db.models import Sum
import json
from .models import CarbonFootprint, UserReward
from django.contrib.auth import logout


from django.contrib.auth import authenticate, login





from django.http import JsonResponse
from django.shortcuts import render
from .models import CarbonFootprint, UserReward
from django.db import models
from django.utils.timezone import now, timedelta



from django.db.models import Avg
import json


"""@login_required
def history_view(request):
    footprints = CarbonFootprint.objects.filter(user=request.user).order_by('created_at')

    # Group by month and calculate totals
    monthly_data = (
        footprints
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Avg('footprint_total'))  # Using Avg to handle multiple entries per month
        .order_by('month')
    )

    # Prepare labels and data for chart
    labels = [entry['month'].strftime('%b %Y') for entry in monthly_data]
    user_data = [round(entry['total'], 2) for entry in monthly_data]
    average_data = [800 for _ in labels]  # Replace 800 with actual national avg if needed

    return render(request, 'history.html', {
        'footprints': footprints,
        'labels': json.dumps(labels),
        'user_data': json.dumps(user_data),
        'average_data': json.dumps(average_data),
    })"""

def login_view(request):
    if request.method=="POST":
        uname=request.POST['username']
        pname=request.POST['password']
        user=auth.authenticate(username=uname,password=pname) #username password in the table 
        if user is not None:
            auth.login(request,user)        #permission giving process
            respose=redirect("/")
            return respose
        else:
            message="*invalid username and password"

        return render(request,"login.html",{'msg':message})        #here request has url    
    else:
        return render(request,'login.html')


def register(request):
    if request.method=="POST":
        uname=request.POST['username']
        Email=request.POST['email']
        password=request.POST['password1']
        repassword=request.POST['password2']
        if password==repassword:
            if User.objects.filter(username=uname).exists():
                msg="the user name is already taken"
            elif User.objects.filter(email=Email).exists(): 
                msg="the email already exsist"
            else:
                user=User.objects.create_user(username=uname,email=Email,password=repassword)
                user.save()
                auth.login(request,user)  #automatically login after the registration.
                msg="Registration successfull"
                return redirect("/")
        else:
            msg="*password not same"
        return render(request,"register.html",{"msge":msg})
    else:
        return render(request,'register.html')
    
def logout_view(request):
    auth.logout(request)
    response=redirect('/')
    response.delete_cookie("usernam")
    return response

def home(request):
    return render(request, 'home.html')


"""def calculate(request):
    if not request.user.is_authenticated:
        msg = 'Please login'
        return render(request, 'home.html', {'msg': msg})

    if request.method == 'GET':
        return render(request, 'calculate.html')
    else:
        # handle POST or other logic here if needed
        return render(request, 'calculate.html')"""



def calculate_footprint(request):
    if not request.user.is_authenticated:
        msg = 'Please login'
        return render(request, 'home.html', {'msg': msg})
    
    if request.method == 'POST':
        try:
            data = request.POST
            electricity = float(data.get('electricity_usage', 0))
            gas = float(data.get('gas_usage', 0))
            fuel = float(data.get('vehicle_fuel_usage', 0))
            waste = float(data.get('waste_quantity', 0))
            water = float(data.get('water_use', 0))
            diet = data.get('diet_type', 'non_vegetarian')

            # Save the footprint object first
            footprint = CarbonFootprint(
                user=request.user,
                electricity_usage=electricity,
                gas_usage=gas,
                vehicle_fuel_usage=fuel,
                waste_quantity=waste,
                water_use=water,
                diet_type=diet
            )
            footprint.calculate_footprint()  # This saves the object and computes total

            reward_points = 0
            reward_messages = []

            # Compare only after the footprint is safely saved
            previous = CarbonFootprint.objects.filter(
                user=request.user
            ).exclude(id=footprint.id).order_by('-created_at').first()

            if previous:
                if footprint.footprint_total < previous.footprint_total:
                    diff = previous.footprint_total - footprint.footprint_total
                    reward_points += int(diff)  # Reduction earns points
                    reward_messages.append("🎉 You've reduced your carbon footprint since last time!")
                else:
                    reward_messages.append("⚠️ Your carbon footprint increased. Try following the tips above.")
            else:
                reward_points += 10  # First entry bonus
                reward_messages.append("🌱 First footprint entry! You've earned 10 bonus points.")

            # National average comparison (skip None values)
            all_others = CarbonFootprint.objects.exclude(user=request.user).exclude(footprint_total=None)
            if all_others.exists():
                total_sum = sum(fp.footprint_total for fp in all_others if fp.footprint_total is not None)
                count = all_others.count()
                if count > 0:
                    average_footprint = total_sum / count
                    if round(footprint.footprint_total, 2) < average_footprint:
                        reward_points += 5
                        reward_messages.append("🌍 You're doing better than the national average! Extra 5 points!")

            # Save points to user reward model
            user_reward, created = UserReward.objects.get_or_create(user=request.user)
            if reward_points > 0:
                user_reward.add_points(reward_points)  # Add reward points to the user

            # Generate tips & appreciations
            tips = []
            appreciations = []

            if electricity > 200:
                tips.append("🔌 Use energy-efficient appliances to lower electricity usage.")
            else:
                appreciations.append("💡 Electricity usage is within a good range!")

            if gas > 30:
                tips.append("🔥 Consider improving gas appliance efficiency.")
            else:
                appreciations.append("✅ Great job keeping gas usage low.")

            if fuel > 50:
                tips.append("🚗 Try carpooling or using public transport.")
            else:
                appreciations.append("🚙 Efficient travel habits!")

            if water > 10000:
                tips.append("🚿 Fix leaks and use low-flow taps to reduce water usage.")
            else:
                appreciations.append("💧 Water usage is sustainable!")

            if waste > 20:
                tips.append("🗑️ Recycle more and reduce single-use plastics.")
            else:
                appreciations.append("♻️ Waste generation is minimal!")

            if diet == 'non_vegetarian':
                tips.append("🥗 Try incorporating more plant-based meals.")
            else:
                appreciations.append("🌱 Your diet is eco-friendly!")

            reward_messages += appreciations

            # Fetch history for graphs
            user_history = CarbonFootprint.objects.filter(user=request.user).order_by('created_at')
            graph_values = [round(entry.footprint_total, 2) for entry in user_history if entry.footprint_total is not None]
            graph_dates = [entry.created_at.strftime("%Y-%m-%d") for entry in user_history if entry.footprint_total is not None]

            # Send the reward messages, points, and the history data to the template
            return render(request, 'calculate.html', {
                'carbon_footprint': round(footprint.footprint_total, 2),
                'category_emissions': {
                    'electricity': electricity * 0.233,
                    'gas': gas * 2.0,
                    'fuel': fuel * 2.31,
                    'waste': waste * 0.5,
                    'water': water * 0.03,
                    'diet': {'vegan': 1.5, 'vegetarian': 2.5, 'non_vegetarian': 3.5}.get(diet, 3.5)
                },
                'tips': tips,
                'points_earned': reward_points,
                'total_points': user_reward.points,
                'reward_messages': reward_messages,
                'graph_dates': graph_dates,
                'graph_values': graph_values,
            })

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in calculate_footprint: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

    else:
        history = CarbonFootprint.objects.filter(user=request.user).order_by('-created_at') if request.user.is_authenticated else []
        msg="please login"
        return render(request, 'calculate.html', {'msg':msg,'history_view': history})


@login_required
def monthly_history_data(request):
    user = request.user
    data = (
        CarbonFootprint.objects.filter(user=user)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('footprint_total'))
        .order_by('month')
    )

    response_data = {
        'labels': [d['month'].strftime('%B %Y') for d in data],
        'data': [round(d['total'], 2) for d in data]
    }
    return JsonResponse(response_data)




@login_required
def monthly_history(request):
    footprints = CarbonFootprint.objects.filter(user=request.user).order_by('created_at')
    labels = [fp.created_at.strftime('%B %Y') for fp in footprints]
    values = [fp.footprint_total for fp in footprints]
    return JsonResponse({'labels': labels, 'values': values})

from django.utils.timezone import now, timedelta
from django.db.models import Avg

@login_required
def history_view(request):
    user = request.user
    footprints = CarbonFootprint.objects.filter(user=user).order_by('created_at')

    # Prepare graph data
    dates = [fp.created_at.strftime("%Y-%m-%d") for fp in footprints]
    user_footprints = [fp.footprint_total for fp in footprints]

    # Calculate average footprint (can be based on all users or a fixed national avg)
    avg_footprint_value = 526.5  # Example: 20 kg CO₂
    avg_footprints = [avg_footprint_value for _ in footprints]

    return render(request, 'history.html', {
        'footprints': footprints,
        'dates': json.dumps(dates),
        'user_footprints': json.dumps(user_footprints),
        'avg_footprints': json.dumps(avg_footprints),
    })
