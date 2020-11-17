from django.db import models


class User(models.Model):
    phone = models.CharField(max_length=11, primary_key=True)
    email = models.EmailField()
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)

    def to_json(self):
        return {
            'phone': self.phone,
            'email': self.email,
            'name': self.name,
            'profileImage': self.profile_image,
            'status': self.status,
        }

    def __str__(self):
        return self.name + ' ' + self.phone


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=32)
    is_admin = models.BooleanField(default=False)
    expiry_date = models.DateTimeField()

    def to_json(self):
        return {
            'token': self.token,
            'user': self.user.to_json()
        }

    def __str__(self):
        return self.user.name + ' token'


class Otp(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=10)
    expiry = models.CharField(max_length=5)


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    building_number = models.CharField(max_length=50, blank=True, null=True)
    post_code = models.CharField(max_length=25, default='')
    lat = models.FloatField()
    long = models.FloatField()

    def to_json(self):
        return {
            'addressId': self.address_id,
            'address': self.address,
            'buildingNumber': self.building_number,
            'lat': self.lat,
            'long': self.long,
            'postCode': self.post_code,
        }

    def __str__(self):
        return self.user.name + ' ' + self.address


class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    image = models.CharField(max_length=100)
    is_food_g = models.BooleanField(default=True)
    status = models.BooleanField(default=True)

    def to_json(self, children):
        context = {
            'groupId': self.group_id,
            'name': self.name,
            'image': self.image,
            'isFoodGroup': self.is_food_g,
            'status': self.status,
            'children': children,
        }
        if children is None:
            del (context['name'])
            del (context['children'])
            context.update({'groupName': self.name})
        return context

    def __str__(self):
        return self.name


class Food(models.Model):
    food_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    price = models.FloatField(null=True, blank=True)
    final_price = models.FloatField(null=True, blank=True)
    status = models.BooleanField(default=True)
    rank = models.FloatField(default=1.0)
    image = models.CharField(max_length=100)

    def to_json(self, fav=None, with_group=False):
        context = {
            'foodId': self.food_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'finalPrice': self.final_price,
            'rank': self.rank,
            'image': self.image,
            'status': self.status,
        }
        if fav is not None:
            context.update({'favorite': fav})

        if with_group:
            context.update(self.group.to_json(None))
        return context

    def __str__(self):
        return self.group.name + ' ' + self.name


class Option(models.Model):
    option_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.FloatField()
    rank = models.FloatField(default=1.0)
    status = models.BooleanField(default=True)
    image = models.CharField(max_length=100)

    def to_json(self, fav=None, with_group=False, with_sizes=True):
        context = {
            'optionId': self.option_id,
            'name': self.name,
            'price': self.price,
            'rank': self.rank,
            'status': self.status,
            'image': self.image,
        }

        if with_sizes:
            size_list = []
            sizes = FoodSize.objects.filter(option__option_id=self.option_id)
            for s in sizes:
                size_list.append(s.to_json())
            context.update({'sizes': size_list})

        if fav is not None:
            context.update({'favorite': fav})
        if with_group:
            context.update(self.group.to_json(None))
        return context

    def __str__(self):
        return self.name + '({})'.format(str(self.option_id))


class FoodOption(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)


class FoodSize(models.Model):
    food_size_id = models.AutoField(primary_key=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True, blank=True)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)
    size = models.CharField(max_length=50)
    price = models.FloatField()

    def to_json(self, with_option_name=False):
        context = {
            'sizeId': self.food_size_id,
            'size': self.size,
            'price': self.price,
        }
        if with_option_name:
            context.update({'name': self.option.name})
        return context


class FoodType(models.Model):
    food_type_id = models.AutoField(primary_key=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    price = models.FloatField()

    def to_json(self):
        return {
            'foodTypeId': self.food_type_id,
            'type': self.type,
            'price': self.price,
        }


class Favorite(models.Model):
    fav_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True, blank=True)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)

    def to_json(self):
        if self.food is None:
            var = self.option.to_json(with_group=True)
        else:
            var = self.food.to_json(with_group=True)

        context = {
            'favId': self.fav_id,
        }
        context.update(var)
        return context


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track_id = models.CharField(max_length=10)
    datetime = models.DateTimeField()
    total_price = models.FloatField()
    completed = models.BooleanField(default=False)  # for payment
    status = models.BooleanField(default=False)  # for accept reject admin
    payment_type = models.BooleanField(default=True)  # if with card is True else False
    order_type = models.BooleanField()  # if delivery is False else True
    delivery_cost = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    delivery_time = models.CharField(max_length=10)
    service_charge = models.FloatField(default=1.0)

    def to_json(self, with_detail=True, with_customer=False):
        context = {
            'orderId': self.order_id,
            'trackId': self.track_id,
            'datetime': self.datetime,
            'totalPrice': self.total_price,
            'description': self.description,
            'status': self.status,
            'completed': self.completed,
            'paymentType': self.payment_type,
            'orderType': self.order_type,
            'deliveryCost': self.delivery_cost,
            'deliveryTime': self.delivery_time,
        }

        if with_customer:
            context.update(
                {'customer': self.user.to_json()}
            )

        if with_detail:
            foods = OrderFood.objects.filter(order__order_id=self.order_id)
            foods_list = []
            for f in foods:
                foods_list.append(f.to_json())

            address = None
            if self.address is not None:
                address = self.address.to_json()

            context.update({
                'address': address,
                'foods': foods_list,
            })

        return context


class OrderFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food_size = models.ForeignKey(FoodSize, on_delete=models.CASCADE)
    food_type = models.ForeignKey(FoodType, on_delete=models.CASCADE, blank=True, null=True)
    number = models.IntegerField()
    is_rated = models.BooleanField(default=False)

    def to_json(self):
        context = {
            'orderFoodId': self.id,
            'size': self.food_size.to_json(),
            'number': self.number,
            'isRated': self.is_rated,
        }
        if self.food_size.food is not None:
            food = Food.objects.get(food_id=self.food_size.food_id)
            context.update({'food': food.to_json(with_group=True)})
        else:
            food = Option.objects.get(option_id=self.food_size.option_id)
            context.update({'food': food.to_json(with_group=True, with_sizes=False)})

        if self.food_type is not None:
            context.update({'type': self.food_type.to_json()})

        ops = OrderOption.objects.filter(order_food=self)
        if ops.exists():
            op_list = []
            for o in ops:
                op_list.append(o.to_json())

            context.update({'options': op_list})
        return context


class OrderOption(models.Model):
    order_food = models.ForeignKey(OrderFood, on_delete=models.CASCADE)
    option_size = models.ForeignKey(FoodSize, on_delete=models.CASCADE, default=None)

    def to_json(self):
        return self.option_size.to_json(with_option_name=True)


class RestaurantInfo(models.Model):
    res_info_id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=50)
    open = models.BooleanField()
    time_slot = models.IntegerField(null=True, blank=True)
    max_order_per_time_slot = models.IntegerField(null=True, blank=True)
    order_fulfilment = models.IntegerField()  # example collection=0, delivery=1, both=2
    # todo table service options
    collection_time = models.CharField(max_length=10, null=True, blank=True)
    delivery_time = models.CharField(max_length=10, null=True, blank=True)
    collection_discount_amount = models.FloatField(default=0.0)
    cost = models.FloatField(default=0.0)
    free_delivery = models.FloatField(default=0.0)
    min_order_val = models.FloatField(default=0.0)
    sales_tax = models.FloatField(default=0.0)
    paypal_payment_fee = models.FloatField(default=0.0)

    show_item_category_or_sub = models.BooleanField(default=True)  # if cat is True else False

    enable_accept_reject = models.BooleanField(default=True)
    accept_message = models.CharField(max_length=200, default="")
    reject_message = models.CharField(max_length=200, default="")
    time_auto_reject = models.IntegerField(default=1)

    role = models.TextField(default="")

    def to_json(self, times, address):
        return {
            'ResInfoId': self.res_info_id,
            'open': self.open,
            'timeSlot': self.time_slot,
            'maxOrderPerSlot': self.max_order_per_time_slot,
            'orderFulfilment': self.order_fulfilment,
            'collectionTime': self.collection_time,
            'deliveryTime': self.delivery_time,
            'collectionDiscountAmount': self.collection_discount_amount,
            'deliveryCost': self.cost,
            'freeDelivery': self.free_delivery,
            'minOrderValue': self.min_order_val,
            'salesTax': self.sales_tax,
            'paypalPaymentFee': self.paypal_payment_fee,
            'showItemCategory': self.show_item_category_or_sub,
            'enableAcceptReject': self.enable_accept_reject,
            'acceptMessage': self.accept_message,
            'rejectMessage': self.reject_message,
            'timeAutoReject': self.time_auto_reject,
            'role': self.role,
            'times': times,
            'address': address,
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
            'address': self.address,
            'telephone': self.telephone,
            'orderAlert': self.order_alert,
            'email': self.email,
        }


class RestaurantTime(models.Model):
    res_time_id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(RestaurantInfo, on_delete=models.CASCADE)
    start = models.TimeField()
    end = models.TimeField()
    status = models.BooleanField(default=True)

    def to_json(self):
        return {
            'resTimeId': self.res_time_id,
            'start': self.start,
            'end': self.end,
            'status': self.status,
        }


class PostCode(models.Model):
    post_code_id = models.AutoField(primary_key=True)
    post_code = models.CharField(max_length=25)
    delivery_cost = models.FloatField()
    free_delivery = models.FloatField()
    is_over_ride = models.BooleanField(default=False)

    def to_json(self):
        return {
            'postCodeId': self.post_code_id,
            'postCode': self.post_code,
            'deliveryCost': self.delivery_cost,
            'freeDelivery': self.free_delivery,
            'isOverriding': self.is_over_ride,
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


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    trans_id = models.CharField(max_length=25)
    status = models.CharField(max_length=10)
    amount = models.FloatField()
    trans_time = models.DateTimeField()

    def to_json(self):
        return {
            'paymentId': self.id,
            'user': self.user.to_json(),
            'transactionId': self.trans_id,
            'status': self.status,
            'amount': self.amount,
            'transactionTime': self.trans_time,
        }


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    rate = models.FloatField(default=1.0)

    def to_json(self):
        return {
            'ticketId': self.ticket_id,
            'message': self.message,
            'rate': self.rate,
        }
