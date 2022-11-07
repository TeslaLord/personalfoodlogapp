from django.db import models
from django.contrib.auth.models import User

 
class Food(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estimated_calories = models.IntegerField(default=0)
    ingredients = models.CharField(max_length=10000, null=True, blank=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    food_picture = models.ImageField(
        null=False, blank=False, upload_to='food_images')

# class UserProfile(models.Model):
#     food = models.ManyToManyField(Food)

#     def __str__(self):
#         return self.user.username