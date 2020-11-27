from api.models import *

def update_option_size(option, sizes):
    fo_sizes = list(FoodSize.objects.filter(option=option))
    if len(fo_sizes) == 0 and len(sizes) != 0:
        for s in sizes:
            FoodSize(
                option=option,
                size=s['size'],
                price=s['price'],
            ).save()
        return

    if len(sizes) > len(fo_sizes):
        index = 0
        while index < len(sizes):
            temp = sizes[index]
            if temp['id'] is None:
                FoodSize(
                    option=option,
                    size=temp['size'],
                    price=temp['price'],
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
                )
                fo_sizes.remove(temp)
                temp = None
        if temp is not None:
            FoodSize.objects.filter(food_size_id=temp.food_size_id).delete()
            fo_sizes.remove(temp)
