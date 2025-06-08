

"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now



class CarbonFootprint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    electricity_usage = models.FloatField(help_text="Electricity usage in kWh")
    gas_usage = models.FloatField(help_text="Gas usage in cubic meters")
    vehicle_fuel_usage = models.FloatField(help_text="Fuel usage in liters")
    waste_quantity = models.FloatField(help_text="Non-recyclable waste in kg")
    water_use = models.FloatField(help_text="water usage in liters", default=0.0)
    diet_type = models.CharField(max_length=20, choices=[
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vegetarian'),
        ('non_vegetarian', 'Non-Vegetarian')
    ])
    footprint_total = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_footprint(self):
        # Emission factors (kg CO2 per unit)
        electricity_factor = 0.233
        gas_factor = 2.0
        fuel_factor = 2.31
        waste_factor = 0.5
        water_factor = 0.03
        diet_factors = {
            'vegan': 1.5,
            'vegetarian': 2.5,
            'non_vegetarian': 3.5
        }

        self.footprint_total = (
            self.electricity_usage * electricity_factor +
            self.gas_usage * gas_factor +
            self.vehicle_fuel_usage * fuel_factor +
            self.waste_quantity * waste_factor +
            self.water_use * water_factor +
            diet_factors.get(self.diet_type, 0)
        )
        self.save()

class UserReward(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def add_points(self, pts):
        self.points += pts
        self.save()
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class CarbonFootprint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    electricity_usage = models.FloatField(help_text="Electricity usage in kWh")
    gas_usage = models.FloatField(help_text="Gas usage in cubic meters")
    vehicle_fuel_usage = models.FloatField(help_text="Fuel usage in liters")
    waste_quantity = models.FloatField(help_text="Non-recyclable waste in kg")
    water_use = models.FloatField(help_text="Water usage in liters", default=0.0)
    
    DIET_CHOICES = [
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vegetarian'),
        ('non_vegetarian', 'Non-Vegetarian'),
    ]
    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES)
    
    footprint_total = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_footprint(self):
        # Emission factors (kg CO2 per unit)
        electricity_factor = 0.233   # per kWh
        gas_factor = 2.0             # per m³
        fuel_factor = 2.31           # per liter
        waste_factor = 0.5           # per kg
        water_factor = 0.03          # per liter
        diet_factors = {
            'vegan': 1.5,
            'vegetarian': 2.5,
            'non_vegetarian': 3.5
        }

        self.footprint_total = (
            self.electricity_usage * electricity_factor +
            self.gas_usage * gas_factor +
            self.vehicle_fuel_usage * fuel_factor +
            self.waste_quantity * waste_factor +
            self.water_use * water_factor +
            diet_factors.get(self.diet_type, 0)
        )
        self.save()

    def calculate_rewards(self):
        # Get the user's reward object
        reward = self.user.userreward

        # Define a baseline for rewards (e.g., national average footprint)
        national_average = 526.5  # Example value in kg CO2e

        # Determine reward points
        points_earned = 0

        if self.footprint_total < national_average:
            # Reward for being below average
            points_earned = 100  # Example reward points
        elif self.footprint_total < national_average * 1.5:
            # Smaller reward if the footprint is below 1.5x the average
            points_earned = 50

        # If the user's footprint has decreased from their last entry, they get bonus points
        last_footprint = CarbonFootprint.objects.filter(user=self.user).order_by('-created_at').first()
        if last_footprint and self.footprint_total < last_footprint.footprint_total:
            points_earned += 20  # Reward for improvement

        # Add the points to the user's reward account
        reward.add_points(points_earned)


    def __str__(self):
        return f"{self.user.username}'s footprint - {self.created_at.strftime('%B %Y')}"


class UserReward(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def add_points(self, pts):
        self.points += pts
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.points} pts"
