from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
import requests
from fastapi.background import BackgroundTasks
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8000'],
    allow_methods=['*'],
    allow_headers=['*'],
)

redis = get_redis_connection(
    host='redis-18875.c300.eu-central-1-1.ec2.cloud.redislabs.com',
    port=18875,
    password='eETVHCysRSElIMItOM4qNR92vXPf7B0m',
    decode_responses=True
)


class ProductOrder(HashModel):
    product_id: str
    quantity: int

    class Meta:
        database = redis


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis


@app.post('/orders')
def create_order(product_order: ProductOrder, backgroundtasks: BackgroundTasks):
    req = requests.get(f'http://localhost:81/product/{product_order.product_id}')
    product = req.json()
    fee = product['price'] * 0.2

    order = Order(
        product_id=product_order.product_id,
        price=product['price'],
        fee=fee,
        quantity=product_order.quantity,
        total=product['price'] + fee,
        status='pending'
    )
    order.save()
    backgroundtasks.add_task(order_complete, order)
    return order


@app.get('/order/{pk}')
def get_order(pk: str):
    return format(pk)


def format(pk: str):
    order = Order.get(pk)
    return {
        'id': order.pk,
        'quantity': order.quantity,
        'fee': order.fee,
        'price': order.price,
        'total': order.total,
        'status': order.status
    }


@app.get('/orders')
def get_all_orders():
    return [format(pk) for pk in Order.all_pks()]


def order_complete(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd(name='order-completed', fields=order.dict())
