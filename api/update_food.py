from api.models import *


def food_type(f, types):
    fo_types = list(FoodType.objects.filter(food=f, option_type=None))
    if len(fo_types) == 0 and len(types) != 0:
        for t in types:
            FoodType(food=f, type=t['type'], price=t['price']).save()
        return

    if len(types) > len(fo_types):
        index = 0
        while index < len(types):
            temp = types[index]
            if temp['id'] is None:
                FoodType(food=f, type=temp['type'], price=temp['price']).save()
                types.remove(temp)
            else:
                index += 1
                continue

    while len(fo_types) != 0:
        temp = fo_types[0]
        for t in types:
            if t['id'] == temp.food_type_id:
                FoodType.objects.filter(food_type_id=t['id']).update(type=t['type'], price=t['price'])
                fo_types.remove(temp)
                temp = None
        if temp is not None:
            FoodType.objects.filter(food_type_id=temp.food_type_id).delete()
            fo_types.remove(temp)


def food_size(f, sizes):
    fo_sizes = list(FoodSize.objects.filter(food=f))
    if len(fo_sizes) == 0 and len(sizes) != 0:
        for s in sizes:
            FoodSize(
                food=f,
                size=s['size'],
                price=s['price'],
                extra_type_price=s['extraTypePrice'],
                extra_option_price=s['extraOptionPrice'],
            ).save()
        return

    if len(sizes) > len(fo_sizes):
        index = 0
        while index < len(sizes):
            temp = sizes[index]
            if temp['id'] is None:
                FoodSize(
                    food=f,
                    size=temp['size'],
                    price=temp['price'],
                    extra_type_price=temp['extraTypePrice'],
                    extra_option_price=temp['extraOptionPrice'],
                ).save()
                sizes.remove(temp)
            else:
                index += 1
                continue

    while len(fo_sizes) != 0:
        temp = fo_sizes[0]
        for s in sizes:
            if s['id'] == temp.food_size_id:
                FoodSize.objects.filter(food_size_id=s['id']).update(
                    size=s['size'],
                    price=s['price'],
                    extra_type_price=s['extraTypePrice'],
                    extra_option_price=s['extraOptionPrice'],
                )
                fo_sizes.remove(temp)
                temp = None
        if temp is not None:
            FoodSize.objects.filter(food_size_id=temp.food_size_id).delete()
            fo_sizes.remove(temp)


def food_option_type(f, o_types):
    op_tys = list(OptionType.objects.filter(food=f))

    if len(op_tys) == 0 and len(o_types) != 0:
        for ot in o_types:
            op_t = OptionType(food=f, name=ot['name'], option_type=ot['optionType'])
            op_t.save()
            for c in ot['children']:
                FoodType(food=f, type=c['type'], price=c['price'], option_type=op_t).save()
        return

    if len(o_types) > len(op_tys):
        index = 0
        while index < len(o_types):
            temp = o_types[index]
            if temp['id'] is None:
                op_t = OptionType(food=f, name=temp['name'], option_type=temp['optionType'])
                op_t.save()
                for c in temp['children']:
                    FoodType(food=f, type=c['type'], price=c['price'], option_type=op_t).save()
                o_types.remove(temp)
            else:
                index += 1
                continue

    while len(op_tys) != 0:
        temp2 = op_tys[0]
        for ot in o_types:
            if ot['id'] == temp2.id:
                OptionType.objects.filter(id=ot['id']) \
                    .update(name=ot['name'], option_type=ot['optionType'])
                types = ot['children']
                option_type(f, temp2, types)
                op_tys.remove(temp2)
                temp2 = None
        if temp2 is not None:
            OptionType.objects.filter(id=temp2.id).delete()
            op_tys.remove(temp2)


def option_type(f, option_t, types):
    fo_types = list(FoodType.objects.filter(option_type=option_t))
    if len(fo_types) == 0 and len(types) != 0:
        for t in types:
            FoodType(food=f, option_type=option_t, type=t['type'], price=t['price']).save()
        return

    if len(types) > len(fo_types):
        index = 0
        while index < len(types):
            temp = types[index]
            if temp['id'] is None:
                FoodType(food=f, option_type=option_t, type=temp['type'], price=temp['price']).save()
                types.remove(temp)
            else:
                index += 1
                continue

    while len(fo_types) != 0:
        temp = fo_types[0]
        for t in types:
            if t['id'] == temp.food_type_id:
                FoodType.objects.filter(food_type_id=t['id']).update(type=t['type'], price=t['price'])
                fo_types.remove(temp)
                temp = None
        if temp is not None:
            FoodType.objects.filter(food_type_id=temp.food_type_id).delete()
            fo_types.remove(temp)


def update_food(f, info):
    sizes = info['sizes']
    types = info['types']
    o_types = info['optionTypes']

    food_type(f, types)

    food_size(f, sizes)

    food_option_type(f, o_types)
