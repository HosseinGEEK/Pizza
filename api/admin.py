from json import loads

from api.views import my_response
from django.contrib import admin
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from .models import User, FoodGroup, Food, FoodSize, FoodType, Option, Token, Order, RestaurantInfo, RestaurantAddress, \
    PostCode, Offer, RestaurantTime

admin.site.register(User)
admin.site.register(FoodGroup)
admin.site.register(Food)
admin.site.register(FoodSize)
admin.site.register(FoodType)
admin.site.register(Option)

admin_token = ''


@csrf_exempt
def admin_login(request):
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
                    global admin_token
                    admin_token = tok
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
def res_info(request):
    if request.method == "POST" or request.method == "PUT":
        try:
            token = request.headers.get('token')
            if token == admin_token:
                info = loads(request.body.decode('utf-8'))
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
                if request.method == "PUT":
                    ri.save(force_update=True)
                else:
                    ri.save()

                my_response(True, 'success', ri.to_json())

        except Exception as e:
            return my_response(False, 'error in res info, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


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

        except Exception as e:
            return my_response(False, 'error in post code, ' + str(e), {})
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

        except Exception as e:
            return my_response(False, 'error in offer, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def res_location(request):
    if request.method == "POST":
        try:
            token = request.headers.get('token')
            if token == admin_token:
                info = loads(request.body.decode('utf-8'))
                a = RestaurantAddress(
                    restaurant__res_info_id=info['resId'],
                    address=info['address'],
                    telephone=info['tel'],
                    order_alert=info['orderAlert'],
                    email=info['email'],
                )
                a.save()
                my_response(True, 'success', a.to_json())

        except Exception as e:
            return my_response(False, 'error in post res location, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def get_location(request):
    if request.method == "GET":
        try:
            token = request.headers.get('token')
            if token == admin_token:
                info = loads(request.body.decode('utf-8'))
                res = info['resId']
                locs = RestaurantAddress.objects.filter(restaurant__res_info_id=res)
                locs_list = []

                for l in locs:
                    locs_list.append(l.to_json())

                my_response(True, 'success', locs_list)

        except Exception as e:
            return my_response(False, 'error in get res location, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def res_times(request):
    if request.method == 'POST' or request.method == 'PUT':
        try:
            token = request.headers.get('token')
            if token == admin_token:
                info = loads(request.body.decode('utf-8'))
                time = RestaurantTime(
                    restaurant__res_info_i=info['resId'],
                    day=info['day'],
                    start=info['start'],
                    end=info['end'],
                )
                if request.method == 'POST':
                    time.save()
                else:
                    time.save(force_update=True)
                return my_response(True, 'success', {})

        except Exception as e:
            return my_response(False, 'error in times, ' + str(e), {})

    else:
        return my_response(False, 'invalid method', {})

@csrf_exempt
def group(request):
    if request.method == 'POST' or request.method == 'PUT':
        try:
            token = request.headers.get('token')
            if token == admin_token:
                info = loads(request.body.decode('utf-8'))
                name = info['name']
                image = info['imageName']
                # todo handle image
                fg = FoodGroup(name=name, image=image)
                if request.method == 'POST':
                    fg.save()
                else:
                    fg.save(force_update=True)
                return my_response(True, 'success', {})

        except Exception as e:
            return my_response(False, 'error in group, ' + str(e), {})

    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def food(request):
    if request.method == 'POST' or request.method == 'PUT':
        try:
            token = request.headers.get('token')
            if token == admin_token:
                info = loads(request.body.decode('utf-8'))
                group_id = info['groupId']
                name = info['name']
                describ = info['description']
                price = info['price']
                image = info['imageName']
                # todo handle image
        except Exception as e:
            return my_response(False, 'error in food, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})


@csrf_exempt
def option(request):
    if request.method == 'POST' or request.method == 'PUT':
        try:
            token = request.headers.get('token')
            if token == admin_token:
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
            return my_response(False, 'error in option, ' + str(e), {})
    else:
        return my_response(False, 'invalid method', {})