from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserRegisterForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from django.http import Http404
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import random
# Create your views here.
@login_required
def home(request):
    if request.method == "POST":
        u_form = UserProfileForm(request.POST, request.FILES)
        print(request.FILES)
        if request.FILES:
            files = request.FILES.getlist('food_picture')
            for file in files:
                image_path = file.temporary_file_path()
                print(image_path)

                model = load_model('keras_model.h5')
                data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
                image = Image.open(image_path).convert('RGB')
                size = (224, 224)
                image = ImageOps.fit(image, size, Image.ANTIALIAS)
                image_array = np.asarray(image)
                normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
                data[0] = normalized_image_array
                prediction = model.predict(data)
                with open("labels.txt", "r") as txt_file:
                    data = txt_file.readlines()
                class_names = []
                for dat in data:
                    name = dat.strip().split()[1]
                    class_names.append(name)
                index = np.argmax(prediction)
                result_set = {}
                for i, v in enumerate(prediction[0]):
                    if v > 0.07:
                        result_set[i] = v
                print(result_set)
                result_list = []
                for index, value in result_set.items():
                    class_name = class_names[index]
                    confidence_score = prediction[0][index]
                    result_list.append(class_name)
                    print("Class: ", class_name)
                    print("Confidence Score: ", confidence_score)

        calories_list = random.sample(range(20, 80), len(result_list))
        total = sum(calories_list)
        ingredients = ""
        for item, calorie in zip(result_list, calories_list):
            print(item)
            ingredients += item + ": " + str(calorie) + "cals,"
        ingredients = ingredients[:len(ingredients)-1]
        if u_form.is_valid():
            u_form1 = u_form.save(commit=False)
            u_form1.user = request.user
            u_form1.ingredients = ingredients
            u_form1.estimated_calories = total
            u_form1.save()
            latest_id = Food.objects.last().id
            return redirect(f"history_detail/{latest_id}")
        else:
            print("NOT VALID")
            print(u_form)
            ingredients = "tomato: 100 cals, onions: 200 cals"
        return render(request, 'user/result.html', { 'image':"image_path", 'ingredients': ingredients, 'total':total })

    else:
        u_form = UserProfileForm()
    return render(request, 'user/home.html')

# def image_upload(request):
#     context = dict()
#     if request.method == 'POST':
#         username = request.POST["username"]
#         image_path = request.POST["src"]  # src is the name of input attribute in your html file, this src value is set in javascript code
#         image = NamedTemporaryFile()
#         image.write(urlopen(path).read())
#         image.flush()
#         image = File(image)
#         name = str(image.name).split('\\')[-1]
#         name += '.jpg'  # store image in jpeg format
#         image.name = name
#         if image is not None:
#             obj = Image.objects.create(username=username, image=image)  # create a object of Image type defined in your model
#             obj.save()
#             context["path"] = obj.image.url  #url to image stored in my server/local device
#             context["username"] = obj.username
#         else :
#             return redirect('/')
#         return redirect('any_url')
#     return render(request, 'index.html', context=context)  # context is like respose data we are sending back to user, that will be rendered with specified 'html file'.         

@login_required
def history(request):
    user_id = request.user.id
    foods = Food.objects.filter(user_id=user_id).order_by('-uploaded_date')
        # food.estimated_calories
        # food.ingredients.split(',')
        # food.food_picture.url
    return render(request, 'user/history.html', {"foods":foods})

@login_required
def history_detail(request, pk=None):
    # try:
        food = Food.objects.get(id=pk, user=request.user)
        ingredients_list = []
        for ingredients in food.ingredients.split(','):
            ingredient = ingredients.split(':')
            ingredients_list.append((ingredient[0], ingredient[1]))
        context = {
            'estimated_calories': food.estimated_calories,
            'uploaded_date': food.uploaded_date,
            'ingredients': ingredients_list,
            'food_picture': food.food_picture.url,
        }
        return render(request, 'user/history_detail.html', context)
    # except:
    #     raise Http404("You are not authorised")

def register(request):
    if request.method == "POST":
        u_form = UserRegisterForm(request.POST)
        if u_form.is_valid():
            u_form.save()
            return redirect('user-home')
    else:
        u_form = UserRegisterForm()

    return render(request, 'user/register.html', {"u_form": u_form})
