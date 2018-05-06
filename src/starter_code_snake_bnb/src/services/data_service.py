import datetime

from data.cages import Cage
from data.owners import Owner
from data.bookings import Booking
from data.snakes import Snake
from typing import List


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email
    owner.save()
    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def register_cage(active_account: Owner,
                  name, allow_dangerous, has_toys,
                  carpeted, meters, price) -> Cage:
    cage = Cage()
    cage.name = name
    cage.square_meters = meters
    cage.is_carpeted = carpeted
    cage.has_toys = has_toys
    cage.allow_dangerous_snakes = allow_dangerous
    cage.price = price
    cage.save()

    account = find_account_by_email(active_account.email)
    account.cage_ids.append(cage.id)
    account.save()

    return cage


def find_cages_for_user(account: Owner) -> List[Cage]:
    query = Cage.objects(id__in=account.cage_ids)
    cages = list(query)
    return cages


def add_available_date(cage: Cage,
                       startdate: datetime.datetime, days: int) -> Cage:
    booking = Booking()
    booking.check_in_date = startdate
    booking.check_out_date = startdate + datetime.timedelta(days=days)
    cage = Cage.objects(id=cage.id).first()
    cage.bookings.append(booking)
    cage.save()
    return cage


def add_snake(account: Owner, name: str, length: float, species: str,
              is_venomous: bool) -> Snake:
    snake = Snake()
    snake.name = name
    snake.length = length
    snake.species = species
    snake.is_venomous = is_venomous
    snake.save()

    owner = find_account_by_email(account.email)
    owner.snake_ids.append(snake.id)
    owner.save()

    return snake


def get_snakes_for_user(account: Owner) -> List[Snake]:
    snakes = Snake.objects(id__in=account.snake_ids).all()
    return list(snakes)


def get_available_cages(checkin: datetime.datetime,
                        checkout: datetime.datetime,
                        snake: Snake) -> List[Cage]:
    min_size = snake.length / 4

    query = Cage.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    if snake.is_venomous:
        query = query.filter(allow_dangerous_snakes=True)

    cages = query.order_by('price', '-square_meters')

    final_cages = []
    for c in cages:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout \
                    and b.guest_snake_id is None:
                final_cages.append(c)
    return final_cages


def book_cage(account: Owner, snake: Snake, cage: Cage,
              checkin: datetime.datetime,
              checkout: datetime.datetime):
    booking = None
    for b in cage.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout \
                and b.guest_snake_id is None:
            booking = b
            break
    booking.guest_owner_id = account.id
    booking.guest_snake_id = snake.id
    booking.booked_date = datetime.datetime.now()

    cage.save()
