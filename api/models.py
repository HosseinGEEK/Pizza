from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11)
    email = models.EmailField()
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)

    def to_json(self):
        return {
            'userId': self.user_id,
            'phone': self.phone,
            'email': self.email,
            'name': self.name,
            'profileImage': self.profile_image,
            'status': self.status,
        }

    def __str__(self):
        return self.name + ' ' + self.phone


class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=32)

    def to_json(self):
        return {
            'token': self.token,
            'user': self.user.to_json()
        }

    def __str__(self):
        return self.user.name + ' token'


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    building_number = models.CharField(max_length=50, blank=True, null=True)
    lat = models.FloatField()
    long = models.FloatField()

    def to_json(self):
        return {
            'addressId': self.address_id,
            'address': self.address,
            'buildingNumber': self.building_number,
            'lat': self.lat,
            'long': self.long,
        }

    def __str__(self):
        return self.user.name + ' ' + self.address


class FoodGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    image = models.CharField(max_length=100)

    def to_json(self, foods):
        return {
            'groupId': self.group_id,
            'name': self.name,
            'image': self.image,
            'foods': foods,
        }

    def __str__(self):
        return self.name


class Food(models.Model):
    food_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(FoodGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    price = models.FloatField(null=True, blank=True)
    final_price = models.FloatField(null=True, blank=True)
    status = models.BooleanField(default=True)
    rank = models.FloatField(default=1.0)
    image = models.CharField(max_length=100)

    def to_json(self):
        return {
            'foodId': self.food_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'finalPrice': self.final_price,
            'rank': self.rank,
            'image': self.image,
        }

    def __str__(self):
        return self.group.name + ' ' + self.name


class FoodSize(models.Model):
    food_size_id = models.AutoField(primary_key=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    size = models.CharField(max_length=50)
    price = models.FloatField()

    def to_json(self):
        return {
            'foodTypeId': self.food_size_id,
            'size': self.size,
            'price': self.price,
        }

    def __str__(self):
        return self.food.name + ' ' + self.size


class FoodType(models.Model):
    food_type_id = models.AutoField(primary_key=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    price = models.FloatField()

    def to_json(self):
        return {
            'foodTypeId': self.food_type_id,
            'size': self.type,
            'price': self.price,
        }

    def __str__(self):
        return self.food.name + ' ' + self.type


class Option(models.Model):
    option_id = models.AutoField(primary_key=True)
    # option_group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.FloatField()

    def to_json(self):
        return {
            'optionId': self.option_id,
            'name': self.name,
            'price': self.price,
        }

    def __str__(self):
        return self.name


# todo option reference
class FoodOption(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)


class Favorite(models.Model):
    fav_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    def to_json(self):
        return {
            'favId': self.fav_id,
            'food': self.food.to_json()
        }


class Order(models.Model):
    order_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    total_price = models.FloatField()
    status = models.BooleanField()
    payment_type = models.BooleanField()  # if with card is True else False
    order_type = models.BooleanField()  # if delivery is True else False
    description = models.CharField(max_length=200, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)

    def to_json(self):
        foods = OrderFood.objects.filter(order__order_id=self.order_id)
        foods_list = []
        for f in foods:
            foods_list.append(f.to_json())

        ops = OrderOption.objects.filter(order__order_id=self.order_id)
        options_list = []
        for o in ops:
            options_list.append(o.to_json())
        return {
            'orderId': self.order_id,
            'datetime': self.datetime,
            'totalPrice': self.total_price,
            'description': self.description,
            'address': self.address.to_json(),
            'foods': foods_list,
            'options': options_list,
        }

    def __str__(self):
        return self.user.name + ' ' + str(self.datetime)


class OrderFood(models.Model):
    food_size = models.ForeignKey(FoodSize, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    number = models.IntegerField()

    def to_json(self):
        food = Food.objects.get(food_id=self.food_size.food_id)
        sizes = [self.food_size.to_json()]
        return {
            'food': food.to_json(sizes),
            'number': self.number,
        }

    def __str__(self):
        return str(self.order.order_id) + ' ' + self.food_size.size


class OrderOption(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)

    def to_json(self):
        return self.option.to_json()

    def __str__(self):
        return str(self.order.order_id) + ' ' + self.option.name


class RestaurantInfo(models.Model):
    res_info_id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=50)
    open = models.BooleanField()
    time_slot = models.CharField(max_length=50)
    max_order_per_time_slot = models.CharField(max_length=25)
    order_fulfilment = models.CharField(max_length=50)  # example collection, delivery
    # todo table service options
    collection_time = models.CharField(max_length=25)
    delivery_time = models.CharField(max_length=25)
    delivery_post_codes = models.TextField(null=True, blank=True)
    collection_discount_amount = models.FloatField(default=0.0)
    delivery_cost = models.FloatField(default=0.0)
    free_delivery = models.FloatField(default=0.0)
    min_order_val = models.FloatField(default=0.0)
    sales_tax = models.FloatField(default=0.0)
    paypal_payment_fee = models.FloatField(default=0.0)

    show_item_category_or_sub = models.BooleanField()  # if cat is True else False

    enable_accept_reject = models.BooleanField()
    message_show = models.CharField(max_length=500)
    time_auto_reject = models.IntegerField()

    def to_json(self, *args, **kwargs):
        return {
            'ResInfoId': self.res_info_id,
            'open': self.open,
            'timeSlot': self.time_slot,
            'maxOrderPerSlot': self.max_order_per_time_slot,
            'orderFulfilment': self.order_fulfilment,
            'collectionTime': self.collection_time,
            'deliveryTime': self.delivery_time,
            'deliveryPostCodes': self.delivery_post_codes,
            'collectionDiscountAmount': self.collection_discount_amount,
            'deliveryCost': self.delivery_cost,
            'freeDelivery': self.free_delivery,
            'minOrderValue': self.min_order_val,
            'salesTax': self.sales_tax,
            'paypalPaymentFee': self.paypal_payment_fee,
            'showItemCategory': self.show_item_category_or_sub,
            'enableAcceptReject': self.enable_accept_reject,
            'message': self.message_show,
            'timeAutoReject': self.time_auto_reject,
            'times': args,
            'address': kwargs,
        }


class RestaurantAddress(models.Model):
    res_address_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(RestaurantInfo, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20)
    order_alert = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

    def to_json(self):
        return {
            'ResAddressId': self.res_address_id,
            'name': self.restaurant.res_info_id,
            'address': self.address,
            'telephone': self.telephone,
            'orderAlert': self.order_alert,
            'email': self.email,
        }

    def __str__(self):
        return str(self.restaurant.res_info_id) + ' ' + self.address


class RestaurantTime(models.Model):
    res_time_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(RestaurantInfo, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    start = models.TimeField()
    end = models.TimeField()

    def to_json(self):
        return {
            'resTimeId': self.res_time_id,
            'day': self.day,
            'start': self.start,
            'end': self.end,
        }

    def __str__(self):
        return self.day


class PostCode(models.Model):
    post_code_id = models.AutoField(primary_key=True)
    post_code = models.CharField(max_length=25)
    delivery_cost = models.FloatField(default=7.0)
    free_delivery = models.FloatField(default=40.0)

    def to_json(self):
        return {
            'post_code_id': self.post_code_id,
            'post_code': self.post_code,
            'delivery_cost': self.delivery_cost,
            'free_delivery': self.free_delivery,
        }


class Offer(models.Model):
    offer_id = models.AutoField(primary_key=True)
    percent = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    type = models.CharField(max_length=50)

    def to_json(self):
        return {
            'offer_id': self.offer_id,
            'percent': self.percent,
            'amount': self.amount,
            'type': self.type,
        }


class PaymentGateway(models.Model):
    payment_gateway_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    # todo pay code


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)

    def to_json(self):
        return {
            'messageId': self.message_id,
            'user': self.user.to_json(),
            'message': self.message,
        }

    def __str__(self):
        return self.user.name