import datetime
import random
from json import loads

from api import admin
from api.models import User, FoodGroup, Food, FoodSize, Token, Favorite, Order, Option, Address, \
    OrderOption, RestaurantInfo, RestaurantTime, OrderFood, FoodOption, FoodType, RestaurantAddress
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.core.paginator import Paginator

otp = None


def my_response(status, message, data):
    return JsonResponse({
        'status': status,
        'message': message,
        'data': data,
    })


@csrf_exempt
def base(request):
    return HttpResponse(content='<p1>this is server api for pizza project</p1>')


@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            info = loads(request.body.decode('utf-8'))
            user = User()
            for k in info.keys():
                setattr(user, k, info[k])

            user.save(force_insert=True)
            tok = get_random_string(length=32)
            tok = Token(user=user, token=tok).save(force_insert=True)

            return my_response(True, 'user registered', tok.to_json())
        except Exception as e:
            return my_response(False, 'user exist! please sign in, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            info = loads(request.body.decode('utf-8'))
            phone = info['phone']
            user = User.objects.filter(phone=phone)

            if user.exists():
                password = info['password']
                if user[0].password == password:
                    user.update(status=True)

                    tok = get_random_string(length=32)
                    tok = Token(user=user, token=tok).save(force_insert=True)

                    return my_response(True, 'success', tok.to_json())
                else:
                    return my_response(False, 'invalid information', {})
            else:
                return my_response(False, 'user not found', {})
        except Exception as e:
            return my_response(False, 'error in login, check login body, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def logout(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists():
                user = token[0].user
                User.objects.filter(user_id=user.user_id).update(status=False)
                token.delete()
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'token not exist', {})
        except Exception as e:
            return my_response(False, 'error in logout, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def delete_account(request):
    if request.method == 'DELETE':
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists():
                user = token[0].user
                User.objects.filter(user_id=user.user_id).delete()
                token.delete()
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'token not exist', {})
        except Exception as e:
            return my_response(False, 'error in logout, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def password_reminder(request):
    if request.method == 'GET':
        phone = request.GET.get('phone')
        user = User.objects.filter(phone=phone)
        if user.exists():
            password = random.randint(100, 99999)
            password = str(password)
            # pass_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
            user.update(password=password)
        else:
            return my_response(False, 'user not found', {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def my_send_mail(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists():
                global otp
                otp = random.randint(10000, 99999)
                send_mail(
                    'pizza app',
                    'confirmation code ' + str(otp) + 'for change password in pizza app',
                    'from@example.com',
                    ['to@example.com'],
                    fail_silently=False,
                )

                return my_response(True, 'success', {})
            else:
                return my_response(False, 'token not exist', {})
        except Exception as e:
            return my_response(False, 'error in send mail, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def change_pass(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists():
                user = token[0].user
                info = loads(request.body.decode('utf-8'))

                this_otp = info['otp']
                old = info['old']
                new = info['new']

                global otp
                if this_otp != otp:
                    return my_response(False, 'confirmation code invalid', None)

                if user.password != old:
                    return my_response(False, 'old password invalid', None)

                user = User.objects.filter(user_id=user.user_id)
                user.update(password=new)
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'token not exist', {})
        except Exception as e:
            return my_response(False, 'error in all changePass, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def get_home_info(request):
    if request.method == 'GET':
        try:
            all_foods_group = []
            popular_foods = []
            groups = FoodGroup.objects.all()
            for g in groups:
                foods = Food.objects.filter(group__group_id=g.group_id)
                foods_list = []
                for f in foods:
                    foods_list.append(f.to_json())
                    if f.rank > 4:
                        popular_foods.append(f.to_json())
                all_foods_group.append(g.to_json(foods_list))

            context = {
                'foodsWithGroup': all_foods_group,
                'popularFoods': popular_foods,
            }
            return my_response(True, 'success', context)
        except Exception as e:
            return my_response(False, 'error in all foods, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def get_food(request):
    if request.method == 'GET':
        food_id = request.GET.get('foodId')
        option_list = []
        food_sizes_list = []
        food_types_list = []

        sizes = FoodSize.objects.filter(food__food_id=food_id)
        for s in sizes:
            food_sizes_list.append(s.to_json())

        types = FoodType.objects.filter(food__food_id=food_id)
        for t in types:
            food_types_list.append(t.to_json())

        fo_options = FoodOption.objects.filter(food__food_id=food_id)
        for fo in fo_options:
            o = Option.objects.get(option_id=fo.option.option_id)
            option_list.append(o.to_json())

        context = {
            'options': option_list,
            'foodSizes': food_sizes_list,
            'foodTypes': food_types_list,
        }

        return my_response(True, 'success', context)
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def get_fav_foods(request):
    if request.method == 'GET':
        token = request.headers.get('token')
        token = Token.objects.filter(token=token)
        if token.exists():
            user = token[0].user
            favs = Favorite.objects.filter(user=user)
            favs_list = []
            for f in favs:
                favs_list.append(f.to_json())

            return my_response(True, 'success', favs_list)
        else:
            return my_response(False, 'token not exist', {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def get_user_address(request):
    if request.method == 'GET':
        token = request.headers.get('token')
        token = Token.objects.filter(token=token)
        if token.exists():
            user = token[0].user
            ads = Address.objects.filter(user=user)
            ads_list = []
            for a in ads:
                ads_list.append(a.to_json())
            return my_response(True, 'success', ads_list)
        else:
            return my_response(False, 'token not exist', {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def insert_user_address(request):
    if request.method == 'POST' or request.method == 'PUT':
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists():
                user = token[0].user
                info = loads(request.body.decode('utf-8'))

                a = Address(
                    user=user,
                    address=info['address'],
                    building_number=info['buildingNumber'],
                    lat=info['lat'],
                    long=info['long']
                )
                if request.method == 'POST':
                    a.save()
                else:
                    a.save(force_update=True)
                return my_response(True, 'success', a.to_json())

            else:
                return my_response(False, 'invalid token', {})
        except Exception as e:
            return my_response(False, 'error in insert Address, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def insert_user_order(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists():
                user = token[0].user
                info = loads(request.body.decode('utf-8'))
                time = info['datetime']
                total_price = info['totalPrice']
                description = info['description']
                address = info['addressId']
                if address is not None:
                    address = Address.objects.get(address_id=address)
                order = Order(
                    user=user,
                    datetime=time,
                    total_price=total_price,
                    description=description,
                    address=address
                )
                order.save()

                foods = info['foods']
                for f in foods:
                    size = FoodSize.objects.get(food_size_id=f['foodSizeId'])
                    _type = FoodType.objects.get(food_type_id=f['foodTypeId'])
                    OrderFood(food_size=size, food_type=_type, order=order, number=f['number']).save()

                order_options = info['optionsId']
                for op in order_options:
                    o = Option.objects.get(option_id=op)
                    OrderOption(order=order, option=o).save()

                return my_response(True, 'success', order.to_json())
            else:
                return my_response(False, 'invalid token', {})
        except Exception as e:
            return my_response(False, 'error in insert order, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def get_orders(request):
    if request.method == 'GET':
        token = request.headers.get('token')
        token = Token.objects.filter(token=token)
        if token.exists():
            if token[0] == admin.admin_token:
                orders = Order.objects.all()
            else:
                user = token[0].user
                orders = Order.objects.filter(user=user)

            paginator = Paginator(orders, 15)
            try:
                page = int(request.GET.get('page', '1'))
            except:
                page = 1

            try:
                orders = paginator.page(page)
            except:
                orders = paginator.page(paginator.num_pages)
            orders_list = []
            for o in orders.object_list:
                orders_list.append(o.to_json())

            return my_response(True, 'success', orders_list)
        else:
            return my_response(False, 'token not exist', {})
    else:
        return my_response(False, 'invalid method', {})

@csrf_exempt
def get_res_info(request):
    if request.method == 'GET':
        ress = RestaurantInfo.objects.all()
        for r in ress:
            times_list = []
            times = RestaurantTime.objects.filter(restaurant__res_info_id=r.res_info_id)
            for t in times:
                times_list.append(t.to_json())
            address_list = []
            address = RestaurantAddress.objects.filter(restaurant__res_info_id=r.res_info_id)
            for a in address:
                address_list.append(a.to_json())
            data = r.to_json(times_list, address_list)

            return my_response(True, 'success', data)

        return my_response(False, 'not exist any restaurant', {})

    else:
        return my_response(False, 'invalid method', {})


def image_name():
    name = datetime.datetime.now()
    name = str(name).replace(' ', '_')
    name = name.split('.')[0].replace(':', '-')

    return name
