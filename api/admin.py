import base64
import datetime
from json import loads

from api.views import my_response, image_name
from django.contrib import admin
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from fcm.models import Device

from .models import User, Group, Food, FoodSize, FoodType, Option, Token, Order, RestaurantInfo, RestaurantAddress, \
    PostCode, Offer, RestaurantTime, OrderFood, OrderOption, Favorite, FoodOption, Ticket, Address, Otp
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
admin.site.register(Favorite)
admin.site.register(FoodOption)
admin.site.register(Ticket)
admin.site.register(Address)
admin.site.register(RestaurantTime)
admin.site.register(Otp)


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
                    Token(user=user[0], token=tok, is_admin=True).save()
                    Device(reg_id=info['deviceToken'], dev_id=info['deviceId'], name='appAdmin', is_active=True).save()
                    return my_response(True, 'success', {'token': tok})
                else:
                    return my_response(False, 'invalid information', {})
            else:
                return my_response(False, 'user not found', {})
        except Exception as e:
            e = str(e)
            if e.__contains__('UNIQUE constraint'):
                Device.objects.filter(dev_id=info['deviceId']).delete()
                return admin_login(request)
            else:
                return my_response(False, 'error in login, check login body, ' + e, {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def res_info(request, res_id=None):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
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
                        cost=info['cost'],
                        free_delivery=info['freeDelivery'],
                        min_order_val=info['minOrderValue'],
                        sales_tax=info['salesTax'],
                        paypal_payment_fee=info['paypalPaymentFee'],
                        # show_item_category_or_sub=info['showItemCategory'],
                        # enable_accept_reject=info['enableAcceptReject'],
                        # message_show=info['message'],
                        # time_auto_reject=info['timeAutoReject'],
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
                        cost=info['cost'],
                        free_delivery=info['freeDelivery'],
                        min_order_val=info['minOrderValue'],
                        sales_tax=info['salesTax'],
                        paypal_payment_fee=info['paypalPaymentFee'],
                        # show_item_category_or_sub=info['showItemCategory'],
                        # enable_accept_reject=info['enableAcceptReject'],
                        # message_show=info['message'],
                        # time_auto_reject=info['timeAutoReject'],
                    )
                    ri = ri.first()

                return my_response(True, 'success', ri.to_json(None, None))

            except Exception as e:
                return my_response(False, 'error in res info, check send body, ' + str(e), {})
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def res_role(request):
    if request.method == "PUT":
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists() and token[0].is_admin:
                info = loads(request.body.decode('utf-8'))

                if 'resId' in info:
                    res_id = info['resId']
                else:
                    res_id = RestaurantInfo.objects.first().res_info_id

                RestaurantInfo.objects.filter(res_info_id=res_id).update(role=info['role'])

                return my_response(True, 'success', {'role': info['role']})
            else:
                return my_response(False, 'token invalid', {})

        except Exception as e:
            return my_response(False, 'error in res role code, check send body, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def post_code(request):
    if request.method == "POST":
        try:
            token = request.headers.get('token')
            token = Token.objects.filter(token=token)
            if token.exists() and token[0].is_admin:
                info = loads(request.body.decode('utf-8'))
                pc = PostCode(
                    post_code=info['postCode'],
                    delivery_cost=info['deliveryCost'],
                    free_delivery=info['freeDelivery'],
                )

                pc.save()
                return my_response(True, 'success', pc.to_json())
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
            token = Token.objects.filter(token=token)
            if token.exists() and token[0].is_admin:
                info = loads(request.body.decode('utf-8'))
                o = Offer(
                    percent=info['percent'],
                    amount=info['amount'],
                    type=info['type']
                )

                o.save()
                return my_response(True, 'success', o.to_json())
            else:
                return my_response(False, 'token invalid', {})

        except Exception as e:
            return my_response(False, 'error in offer, check send body, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def res_location(request, address_id=None):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == "POST" or request.method == 'PUT':
            try:
                info = loads(request.body.decode('utf-8'))
                res = RestaurantInfo.objects.first().res_info_id

                if request.method == 'POST':
                    a = RestaurantAddress(
                        restaurant_id=res,
                        address=info['address'],
                        telephone=info['telephone'],
                        order_alert=info['orderAlert'],
                        email=info['email'],
                    )
                    a.save()
                else:
                    a = RestaurantAddress.objects.filter(res_address_id=address_id)
                    a.update(
                        address=info['address'],
                        telephone=info['telephone'],
                        order_alert=info['orderAlert'],
                        email=info['email'],
                    )
                    a = a.first()
                return my_response(True, 'success', a.to_json())

            except Exception as e:
                return my_response(False, 'error in post res location, check send body, ' + str(e), {})
        elif request.method == 'DELETE':
            var = RestaurantAddress.objects.filter(res_address_id=address_id).delete()
            if var[0] != 0:
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
def res_times(request, time_id=None):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'PUT':
            try:

                info = loads(request.body.decode('utf-8'))
                time = RestaurantTime.objects.filter(res_time_id=time_id)
                time.update(
                    res_time_id=time_id,
                    start=info['start'],
                    end=info['end'],
                    status=info['status'],
                )
                time = time.first()
                return my_response(True, 'success', time.to_json())

            except Exception as e:
                return my_response(False, 'error in times, check send body, ' + str(e), {})

        elif request.method == 'DELETE':
            var = RestaurantTime.objects.filter(time_id=time_id).delete()
            if var[0] != 0:
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
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
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
                    fg.update(name=name, image=img_name, is_food_g=is_food_g, status=info['status'])
                    fg = fg.first()
                return my_response(True, 'success', fg.to_json(None))

            except Exception as e:
                return my_response(False, 'error in group check body send, ' + str(e), {})
        elif request.method == 'DELETE':
            var = Group.objects.filter(group_id=group_id).delete()
            if var[0] != 0:
                return my_response(True, 'success', {})
            else:
                return my_response(False, 'foodGroupId not exist!', {})
        elif request.method == 'GET':
            g_list = []
            gs = Group.objects.all()
            for g in gs:
                if g.is_food_g:
                    foods = Food.objects.filter(group=g)
                else:
                    foods = Option.objects.filter(group=g)
                _list = []
                for f in foods:
                    _list.append(f.to_json())
                g_list.append(g.to_json(_list))
            return my_response(True, 'success', g_list)

        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def food(request, food_id=None):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'POST' or request.method == 'PUT':
            try:
                info = loads(request.body.decode('utf-8'))
                name = info['name']
                describ = info['description']
                price = info['price']
                final_price = info['finalPrice']
                image = info['image']
                status = info['status']
                sizes = info['sizes']
                types = info['types']
                ops = info['options']
                try:
                    img_name = image_name() + '.png'
                    path = 'media/Images/' + img_name
                    img_data = base64.b64decode(image)
                    with open(path, 'wb') as f:
                        f.write(img_data)
                except:
                    img_name = image

                if request.method == 'POST':
                    group_id = info['groupId']
                    f = Food(
                        group_id=group_id,
                        name=name,
                        description=describ,
                        price=price,
                        final_price=final_price,
                        image=img_name,
                        status=status,
                    )
                    f.save()
                    for o in ops:
                        FoodOption(food=f, option_id=o).save()
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
                        final_price=final_price,
                        image=img_name,
                        status=status,
                    )
                    f = f.first()
                    FoodSize.objects.filter(food=f).delete()
                    for s in sizes:
                        size = s['size']
                        s_price = s['price']
                        FoodSize(food=f, size=size, price=s_price).save()
                    FoodType.objects.filter(food=f).delete()
                    for t in types:
                        _type = t['type']
                        t_price = t['price']
                        FoodType(food=f, type=_type, price=t_price).save()
                    FoodOption.objects.filter(food=f).delete()
                    for o in ops:
                        FoodOption(food=f, option_id=o).save()

                return my_response(True, 'success', f.to_json())
            except Exception as e:
                return my_response(False, 'error in food, check send body, ' + str(e), {})
        elif request.method == 'DELETE':
            var = Food.objects.filter(food_id=food_id).delete()
            if var[0] != 0:
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
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'POST' or request.method == 'PUT':
            try:
                info = loads(request.body.decode('utf-8'))
                name = info['name']
                price = info['price']
                image = info['image']
                st = info['status']
                sizes = info['sizes']
                try:
                    img_name = image_name() + '.png'
                    path = 'media/Images/' + img_name
                    img_data = base64.b64decode(image)
                    with open(path, 'wb') as f:
                        f.write(img_data)
                except:
                    img_name = image

                if request.method == 'POST':
                    g_id = info['groupId']
                    o = Option(group_id=g_id, name=name, price=price, image=img_name)
                    o.save()
                    for s in sizes:
                        FoodSize(option=o, size=s['size'], price=s['price']).save()
                else:
                    o = Option.objects.filter(option_id=option_id)
                    o.update(name=name, price=price, image=img_name, status=st)
                    o = o.first()
                    FoodSize.objects.filter(option=o).delete()
                    for s in sizes:
                        FoodSize(option=o, size=s['size'], price=s['price']).save()

                return my_response(True, 'success', o.to_json())

            except Exception as e:
                return my_response(False, 'error in option, check send body, ' + str(e), {})
        elif request.method == 'DELETE':
            var = Option.objects.filter(option_id=option_id).delete()
            if var[0] != 0:
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


@csrf_exempt
def order_with_detail(request):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'GET':
            o = Order.objects.get(order_id=request.GET.get('orderId'))
            return my_response(True, 'success', o.to_json())
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def filter_order(request):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'GET':
            try:
                orders = Order.objects.all()
                tr_id = request.GET.get('trackId')
                if tr_id is not None:
                    orders = orders.filter(track_id__contains=tr_id)
                date = request.GET.get('date')
                if date is not None:
                    orders = orders.filter(datetime__date=date)

                delivery = request.GET.get('delivery')
                if delivery is not None:
                    if delivery == '0':
                        delivery = False
                    else:
                        delivery = True
                    orders = orders.filter(order_type=delivery)
                st = request.GET.get('status')
                if st is not None:
                    if st == '0':
                        st = False
                    else:
                        st = True
                    orders = orders.filter(completed=st)
                p_type = request.GET.get('paymentType')
                if p_type is not None:
                    if p_type == '0':
                        p_type = False
                    else:
                        p_type = True
                    orders = orders.filter(payment_type=p_type)
                _list = []
                for o in orders:
                    _list.append(o.to_json())
                return my_response(True, 'success', _list)
            except Exception as e:
                return my_response(False, 'error in filter order, check send query params, '+ str(e), {})
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def orders_today(request):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'GET':
            orders = Order.objects.filter(datetime__day=datetime.datetime.now().day)
            _list = []
            for o in orders:
                _list.append(o.to_json())
            return my_response(True, 'success', _list)
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def invoice(request):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'GET':
            orders = Order.objects.extra(select={'day': 'date(datetime)'}).values('day').distinct()
            _list = []
            for o in orders:
                _list.append(o['day'])
            _list.reverse()
            return my_response(True, 'success', _list)
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def order_of_day(request):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'GET':
            orders = Order.objects.filter(datetime__date=request.GET.get('day'))
            _list = []
            for o in orders:
                _list.append(o.to_json(with_detail=False))

            return my_response(True, 'success', _list)
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})


@csrf_exempt
def accept_reject_order(request):
    token = request.headers.get('token')
    token = Token.objects.filter(token=token)
    if token.exists() and token[0].is_admin:
        if request.method == 'POST':
            try:
                info = loads(request.body.decode('utf-8'))
                acc_rej = info['acceptOrReject']
                o_id = info['orderId']
                mess = info['message']
                order = Order.objects.filter(order_id=o_id)
                if acc_rej:
                    order.update(status=True)

                order = order.first()
                p = order.user.phone
                users_notif = Device.objects.filter(name=p)
                for un in users_notif:
                    un.send_message(
                        {
                            'orderId': order.order_id,
                            'state': acc_rej,
                            'orderType': order.order_type,
                            'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                        },
                        notification={
                            'title': 'order',
                            'body': mess,
                            'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                            "sound": "default",
                        }
                    )

                return my_response(True, 'success', {})

            except Exception as e:
                return my_response(False, 'error in acceptRejectOrder, check send body, ' + str(e), {})
        else:
            return my_response(False, 'invalid method', {})
    else:
        return my_response(False, 'token invalid', {})
