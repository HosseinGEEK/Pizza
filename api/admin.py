import base64
from json import loads

from api.views import my_response, image_name
from django.contrib import admin
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from .models import User, Group, Food, FoodSize, FoodType, Option, Token, Order, RestaurantInfo, RestaurantAddress, \
    PostCode, Offer, RestaurantTime, OrderFood, OrderOption
from django.core.paginator import Paginator

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Food)
admin.site.register(FoodSize)
admin.site.register(FoodType)
admin.site.register(Option)
admin.site.register(Order)
admin.site.register(Token)
admin.site.register(RestaurantInfo)
admin.site.register(OrderFood)
admin.site.register(OrderOption)

admin_token = ''


@csrf_exempt
def admin_login(request):
    if request.method == "POST":
        info = loads(request.body.decode('utf-8'))
        try:
            phone = info['phone']
            user = User.objects.filter(phone=phone)

            if user.exists():
                password = info['password']
                if user.first().password == password:
                    user.update(status=True)

                    tok = get_random_string(length=32)
                    global admin_token
                    admin_token = tok
                    tok = Token(user=user.first(), token=tok)
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
                return admin_login(request)
            else:
                return my_response(False, 'error in login, check login body, ' + e, {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def res_info(request, res_id=None):
    token = request.headers.get('token')
    if token == admin_token:
        if request.method == "POST" or request.method == "PUT":
            try:
                info = loads(request.body.decode('utf-8'))
                if request.method == "POST":
                    ri = RestaurantInfo(
                        open=info['open'],
                        time_slot=info['timeSlot'],
                        max_order_per_time_slot=info['maxOrderPerSlot'],
                        order_fulfilment=info['orderFulfilment'],
                        collection_time=info['collectionTime'],
                        delivery_time=info['deliveryTime'],
                        delivery_post_codes=info['deliveryPostCodes'],
                        collection_discount_amount=info['collectionDiscountAmount'],
                        delivery_cost=info['deliveryCost'],
                        free_delivery=info['freeDelivery'],
                        min_order_val=info['minOrderValue'],
                        sales_tax=info['salesTax'],
                        paypal_payment_fee=info['paypalPaymentFee'],
                        show_item_category_or_sub=info['showItemCategory'],
                        enable_accept_reject=info['enableAcceptReject'],
                        message_show=info['message'],
                        time_auto_reject=info['timeAutoReject'],
                    )
                    ri.save()
                else:
                    ri = RestaurantInfo.objects.filter(res_info_id=res_id)
                    ri.update(
                        open=info['open'],
                        time_slot=info['timeSlot'],
                        max_order_per_time_slot=info['maxOrderPerSlot'],
                        order_fulfilment=info['orderFulfilment'],
                        collection_time=info['collectionTime'],
                        delivery_time=info['deliveryTime'],
                        delivery_post_codes=info['deliveryPostCodes'],
                        collection_discount_amount=info['collectionDiscountAmount'],
                        delivery_cost=info['deliveryCost'],
                        free_delivery=info['freeDelivery'],
                        min_order_val=info['minOrderValue'],
                        sales_tax=info['salesTax'],
                        paypal_payment_fee=info['paypalPaymentFee'],
                        show_item_category_or_sub=info['showItemCategory'],
                        enable_accept_reject=info['enableAcceptReject'],
                        message_show=info['message'],
                        time_auto_reject=info['timeAutoReject'],
                    )
                    ri = ri.first()

                my_response(True, 'success', ri.to_json(None, None))

            except Exception as e:
                return my_response(False, 'error in res info, check send body, ' + str(e), {})
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def post_code(request):
    if request.method == "POST":
        try:
            token = request.headers.get('token')
            if token == admin_token:
                info = loads(request.body.decode('utf-8'))
                pc = PostCode(
                    post_code=info['postCode'],
                    delivery_cost=info['deliveryCost'],
                    free_delivery=info['freeDelivery'],
                )

                pc.save()
                my_response(True, 'success', pc.to_json())
            else:
                return my_response(False, 'token invalid', {})

        except Exception as e:
            return my_response(False, 'error in post code, check send body, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def offer(request):
    if request.method == "POST":
        try:
            token = request.headers.get('token')
            if token == admin_token:
                info = loads(request.body.decode('utf-8'))
                o = Offer(
                    percent=info['percent'],
                    amount=info['amount'],
                    type=info['type']
                )

                o.save()
                my_response(True, 'success', o.to_json())
            else:
                return my_response(False, 'token invalid', {})

        except Exception as e:
            return my_response(False, 'error in offer, check send body, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def res_location(request, address_id):
    token = request.headers.get('token')
    if token == admin_token:
        if request.method == "POST" or request.method == 'PUT':
            try:
                info = loads(request.body.decode('utf-8'))

                if request.method == 'POST':
                    a = RestaurantAddress(
                        restaurant__res_info_id=info['resId'],
                        address=info['address'],
                        telephone=info['telephone'],
                        order_alert=info['orderAlert'],
                        email=info['email'],
                    )
                    a.save(force_update=True)
                else:
                    a = RestaurantAddress.objects.filter(res_address_id=address_id)
                    a.update(
                        restaurant__res_info_id=info['resId'],
                        address=info['address'],
                        telephone=info['telephone'],
                        order_alert=info['orderAlert'],
                        email=info['email'],
                    )
                    a = a.first()
                my_response(True, 'success', a.to_json())

            except Exception as e:
                return my_response(False, 'error in post res location, check send body, ' + str(e), {})
        elif request.method == 'DELETE':
            var = RestaurantAddress.objects.filter(res_address_id=address_id)
            if var[0] == 1:
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'location id not exist', {})
        elif request.method == 'GET':
            _list = []
            los = RestaurantAddress.objects.all()
            for l in los:
                _list.append(l.to_json())

            return my_response(True, 'success', _list)
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def res_times(request, time_id):
    token = request.headers.get('token')
    if token == admin_token:
        if request.method == 'POST' or request.method == 'PUT':
            try:

                info = loads(request.body.decode('utf-8'))

                if request.method == 'POST':
                    time = RestaurantTime(
                        restaurant__res_info_i=info['resId'],
                        day=info['day'],
                        start=info['start'],
                        end=info['end'],
                        status=info['status'],
                    )
                    time.save()
                else:
                    time = RestaurantTime.objects.filter(res_time_id=time_id)
                    time.update(
                        restaurant__res_info_i=info['resId'],
                        day=info['day'],
                        start=info['start'],
                        end=info['end'],
                        status=info['status'],
                    )
                    time = time.first()

                return my_response(True, 'success', time.to_json())

            except Exception as e:
                return my_response(False, 'error in times, check send body, ' + str(e), {})

        elif request.method == 'DELETE':
            var = RestaurantTime.objects.filter(time_id=time_id)
            if var[0] == 1:
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'time id not exist', {})
        elif request.method == 'GET':
            _list = []
            tis = RestaurantTime.objects.all()
            for t in tis:
                _list.append(t.to_json())

            return my_response(True, 'success', _list)
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def group(request, group_id=None):
    token = request.headers.get('token')
    if token == admin_token:
        if request.method == 'POST' or request.method == 'PUT':
            try:
                info = loads(request.body.decode('utf-8'))
                name = info['name']
                image = info['image']
                is_food_g = info['isFoodGroup']
                try:
                    img_name = image_name() + '.png'
                    path = 'media/Images/' + img_name
                    img_data = base64.b64decode(image)
                    with open(path, 'wb') as g:
                        g.write(img_data)
                except Exception as e:
                    img_name = image

                if request.method == 'POST':
                    fg = Group(name=name, image=img_name, is_food_g=is_food_g)
                    fg.save()
                else:
                    fg = Group.objects.filter(group_id=group_id)
                    fg.update(name=name, image=img_name, is_food_g=is_food_g)
                    fg = fg.first()
                return my_response(True, 'success', fg.to_json(None))

            except Exception as e:
                return my_response(False, 'error in group check body send, ' + str(e), {})
        elif request.method == 'DELETE':
            var = Group.objects.filter(group_id=group_id).delete()
            if var[0] == 1:
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'foodGroupId not exist!', {})
        elif request.method == 'GET':
            g_list = []
            gs = Group.objects.all()
            for g in gs:
                g_list.append(g.to_json(None))
            return my_response(True, 'success', g_list)

        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def food(request, food_id=None):
    token = request.headers.get('token')
    if token == admin_token:
        if request.method == 'POST' or request.method == 'PUT':
            try:
                info = loads(request.body.decode('utf-8'))
                group_id = info['groupId']
                name = info['name']
                describ = info['description']
                price = info['price']
                image = info['image']
                status = info['status']
                sizes = info['sizes']
                types = info['types']
                try:
                    img_name = image_name() + '.png'
                    path = 'media/Images/' + img_name
                    img_data = base64.b64decode(image)
                    with open(path, 'wb') as f:
                        f.write(img_data)
                except:
                    img_name = image

                if request.method == 'POST':
                    f = Food(
                        group__group_id=group_id,
                        name=name,
                        description=describ,
                        price=price,
                        image=img_name,
                        status=status,
                    )
                    f.save()
                    for s in sizes:
                        size = s['size']
                        s_price = s['price']
                        FoodSize(food=f, size=size, price=s_price).save()

                    for t in types:
                        _type = t['type']
                        t_price = t['price']
                        FoodType(food=f, type=_type, price=t_price).save()
                else:
                    f = Food.objects.filter(food_id=food_id)
                    f.update(
                        name=name,
                        description=describ,
                        price=price,
                        image=img_name,
                        status=status,
                    )
                    for s in sizes:
                        size = s['size']
                        s_price = s['price']
                        FoodSize.objects.filter(food_size_id=s['id']).update(size=size, price=s_price)

                    for t in types:
                        _type = t['type']
                        t_price = t['price']
                        FoodType.objects.filter(t['id']).update(type=_type, price=t_price)
                    f = f.first()

                return my_response(True, 'success', f.to_json())

            except Exception as e:
                return my_response(False, 'error in food, check send body, ' + str(e), {})
        elif request.method == 'DELETE':
            var = Food.objects.filter(food_id=food_id).delete()
            if var[0] == 1:
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'foodId not exist!', {})
        elif request.method == 'GET':
            fo_list = []
            fos = Food.objects.all()
            for f in fos:
                fo_list.append(f.to_json())
            return my_response(True, 'success', fo_list)
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def option(request, option_id=None):
    token = request.headers.get('token')
    if token == admin_token:
        if request.method == 'POST' or request.method == 'PUT':
            try:
                info = loads(request.body.decode('utf-8'))
                name = info['name']
                price = info['price']
                o = Option(name=name, price=price)

                if request.method == 'PUT':
                    o.save(force_update=True)
                else:
                    o.save()

                return my_response(True, 'success', o.to_json())

            except Exception as e:
                return my_response(False, 'error in option, check send body, ' + str(e), {})
        elif request.method == 'DELETE':
            var = Option.objects.filter(option_id=option_id).delete()
            if var[0] == 1:
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'optionId not exist!', {})
        elif request.method == 'GET':
            op_list = []
            ops = Option.objects.all()
            for o in ops:
                op_list.append(o.to_json())
            return my_response(True, 'success', op_list)
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})
