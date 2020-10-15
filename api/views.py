import datetime
import random
from json import loads

from api import admin
from api.models import User, Group, Food, FoodSize, Token, Favorite, Order, Option, Address, \
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

            user = User(
                phone=info['phone'],
                email=info['email'],
                name=info['name'],
                password=info['password'],
                profile_image=info['profileImage']
            )
            user.save(force_insert=True)
            tok = get_random_string(length=32)
            tok = Token(user=user, token=tok)
            tok.save(force_insert=True)

            return my_response(True, 'user registered', tok.to_json())
        except Exception as e:
            e = str(e)
            if e.__contains__('UNIQUE constraint'):
                return my_response(False, 'user exist! please sign in', {})
            else:
                return my_response(False, 'error in register, check body send, ' + e, {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def login(request):
    if request.method == "POST":
        info = loads(request.body.decode('utf-8'))
        try:
            phone = info['phone']
            user = User.objects.filter(phone=phone)

            if user.exists():
                password = info['password']
                if user[0].password == password:
                    user.update(status=True)

                    tok = get_random_string(length=32)
                    tok = Token(user=user[0], token=tok)
                    tok.save(force_insert=True)

                    return my_response(True, 'success', tok.to_json())
                else:
                    return my_response(False, 'invalid information', {})
            else:
                return my_response(False, 'user not found', {})
        except Exception as e:
            e = str(e)
            if e.__contains__('UNIQUE constraint'):
                Token.objects.filter(user__phone=info['phone']).delete()
                return login(request)
            else:
                return my_response(False, 'error in login, check login body, ' + e, {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def get_user_info(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists():
                user = token[0].user
                return my_response(True, 'success', user.to_json())
            else:
                return my_response(False, 'token not exist', {})
        except Exception as e:
            return my_response(False, 'error in getUserInfo, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def logout(request):
    if request.method == 'GET':
        try:
            token = request.headers.get('token')
            if token == admin.admin_token:
                admin.admin_token = ''
            token = Token.objects.filter(token=token)
            if token.exists():
                user = token[0].user
                User.objects.filter(phone=user.phone).update(status=False)
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
                User.objects.filter(phone=user.phone).delete()
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

                user = User.objects.filter(phone=user.phone)
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
            user = request.headers.get('token')
            if user is not None:
                user = Token.objects.filter(token=user).first().user
            group_with_children = []
            groups = Group.objects.all()
            fav_option = []
            fav_food = []
            for g in groups:
                if g.is_food_g:
                    children = Food.objects.filter(group__group_id=g.group_id)
                else:
                    children = Option.objects.filter(group__group_id=g.group_id)
                child_list = []
                for c in children:
                    if g.is_food_g:
                        fav = Favorite.objects.filter(
                            user=user,
                            food=c,
                            option=None,
                        )
                        if fav.exists():
                            fav_food.append(fav[0].food_id)
                            child_list.append(c.to_json(fav=True))
                        else:
                            child_list.append(c.to_json())
                    else:
                        fav = Favorite.objects.filter(
                            user=user,
                            food=None,
                            option=c,
                        )
                        if fav.exists():
                            fav_option.append(fav[0].option_id)
                            child_list.append(c.to_json(fav=True))
                        else:
                            child_list.append(c.to_json())

                group_with_children.append(g.to_json(child_list))

            options = list(Option.objects.filter(rank__gt=4).order_by('rank'))
            foods = list(Food.objects.filter(rank__gt=4).order_by('rank'))
            popular_list = merge(foods, options, fav_option, fav_food)

            context = {
                'childrenWithGroup': group_with_children,
                'popularFoods': popular_list,
            }
            return my_response(True, 'success', context)
        except Exception as e:
            return my_response(False, 'error in home info, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def get_food_detail(request):
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
def user_favorite_foods(request):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists():
        try:
            user = token[0].user
            if request.method == 'GET':
                favs = Favorite.objects.filter(user=user)
                favs_list = []
                for f in favs:
                    favs_list.append(f.to_json())

                return my_response(True, 'success', favs_list)

            elif request.method == 'POST':
                is_food = request.GET.get('isFood')
                _id = request.GET.get('id')
                fav = request.GET.get('fav')
                fav = int(fav)
                is_food = int(is_food)
                if fav == 1:
                    if is_food == 1:
                        f = Favorite(user=user, food_id=_id)
                        f.save()
                    else:
                        f = Favorite(user=user, option_id=_id)
                        f.save()
                    return my_response(True, 'success', f.to_json())
                else:
                    if is_food == 1:
                        Favorite.objects.filter(user=user, food_id=_id).delete()
                    else:
                        Favorite.objects.filter(user=user, option_id=_id).delete()
                    return my_response(True, 'success', {})

            else:
                return my_response(False, 'invalid method', {})
        except Exception as e:
            return my_response(False, 'error in favorite, ' + str(e), {})

    else:
        return my_response(False, 'token not exist', {})


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
                del_time = info['deliveryTime']
                order_type = info['orderType']
                tr_id = random.randint(100000, 1000000000)
                if address is not None:
                    address = Address.objects.get(address_id=address)
                order = Order(
                    user=user,
                    track_id=tr_id,
                    datetime=time,
                    total_price=total_price,
                    description=description,
                    address=address,
                    delivery_time=del_time,
                    order_type=order_type,
                )
                order.save()

                foods = info['foods']
                for f in foods:
                    size = FoodSize.objects.get(food_size_id=f['foodSizeId'])
                    _type = FoodType.objects.get(food_type_id=f['foodTypeId'])
                    of = OrderFood(food_size=size, food_type=_type, order=order, number=f['number'])
                    of.save()
                    order_options = info['options']
                    for op_id in order_options:
                        o = Option.objects.get(option_id=op_id)
                        OrderOption(order=order, order_food=of, option=o).save()
                options = info['options']
                for o in options:
                    op_id = o['optionId']
                    option = Option.objects.filter(option_id=op_id)
                    rate = o['rate']
                    op_rate = option.first().rate
                    op_rate = (rate + op_rate) / 2
                    option.update(rate=op_rate)
                    OrderOption(order=order, option=option.first()).save()

                return my_response(True, 'success', order.to_json())
            else:
                return my_response(False, 'invalid token', {})
        except Exception as e:
            return my_response(False, 'error in insert order, check body send, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def set_rate(request):
    if request.method == 'POST':
        try:
            info = loads(request.body.decode('utf-8'))
            for i in info:
                is_food = i['isFood']
                _id = i['id']
                user_rate = i['rate']
                if is_food:
                    c = Food.objects.filter(food_id=_id)
                    rate = c[0].rank
                    rate = (user_rate + rate) / 2
                    c.update(rank=rate)
                else:
                    c = Option.objects.filter(option_id=_id)
                    rate = c[0].rank
                    rate = (user_rate + rate) / 2
                    c.update(rank=rate)
            return my_response(True, 'success', {})
        except Exception as e:
            return my_response(False, 'error in set rate, check body send, ' + str(e), {})
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

            paginator = Paginator(orders, 25)
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
def search_food(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        _list = []
        foods = Food.objects.filter(name__contains=name)
        for f in foods:
            _list.append(f.to_json())

        options = Option.objects.filter(name__contains=name)
        for o in options:
            _list.append(o.to_json())
        return my_response(True, 'success', _list)
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def filter_food(request):
    if request.method == 'POST':
        try:
            info = loads(request.body.decode('utf-8'))
            food_list = []
            min_p = info['minPrice']
            max_p = info['maxPrice']
            group_name = info['groupName']
            size_name = info['sizeName']
            min_r = info['minRate']
            max_r = info['maxRate']

            groups = Group.objects.filter(name=group_name)
            for g in groups:
                foods = Food.objects.filter(group=g, price__range=(min_p, max_p), rank__range=(min_r, max_r))
                for f in foods:
                    size = FoodSize.objects.filter(food=f, size=size_name)
                    if size.exists():
                        food_list.append(f.to_json())

                options = Option.objects.filter(group=g, price__range=(min_p, max_p), rank__range=(min_r, max_r))
                for o in options:
                    food_list.append(o.to_json())

            return my_response(True, 'success', food_list)
        except Exception as e:
            return my_response(False, 'error in filter food, check body send, ' + str(e), {})
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

    elif request.method == 'POST' or request.method == 'PUT':
        return admin.res_info(request)
    else:
        return my_response(False, 'invalid method', {})


def image_name():
    name = datetime.datetime.now()
    name = str(name).replace(' ', '_')
    name = name.split('.')[0].replace(':', '-')

    return name


def merge(foods, options, fav_op, fav_fo):
    result = []
    i = j = 0
    total = len(foods) + len(options)
    while len(result) != total:
        if len(foods) == i:
            while j < len(options):
                if options[j].option_id in fav_op:
                    result.append(options[j].to_json(fav=True, with_group=True))
                else:
                    result.append(options[j].to_json(with_group=True))
                j += 1
            # result += options[j:]
            break
        elif len(options) == j:
            while i < len(foods):
                if foods[i].food_id in fav_fo:
                    result.append(foods[i].to_json(fav=True, with_group=True))
                else:
                    result.append(foods[i].to_json(with_group=True))
                i += 1
            # result += foods[i:]
            break
        elif foods[i].rank > options[j].rank:
            if foods[i].food_id in fav_fo:
                result.append(foods[i].to_json(fav=True, with_group=True))
            else:
                result.append(foods[i].to_json(with_group=True))
            i += 1
        else:
            if options[j].option_id in fav_op:
                result.append(options[j].to_json(fav=True, with_group=True))
            else:
                result.append(options[j].to_json(with_group=True))
            j += 1
    return result
