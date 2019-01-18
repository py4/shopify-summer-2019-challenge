# shopify-summer-2019-challenge

### Running the code:

First build the docker image:
```
docker build -t marketplace .
```

And then run the container:
```
docker run -d -p 8000:8000 --name marketplace marketplace
```

### Usage:

First create a superuser so the admin can add products to the website through admin panel:
```
docker exec -it marketplace python shopify_challenge/manage.py createsuperuser
```
Then go to `localhost:8000/admin` and login, and then you can add products (It's also possible by population script)

First the client has to register in the website to get an auth token
```
curl -X POST \
  http://localhost:8000/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "test", "password": "test"}'

Result:
{
    "user": {
        "id": 8,
        "username": "test"
    },
    "token": "2980a86ae9627382fe9cf3de49c0997cedc80555"
}
```

Now in the case that the client has not the token, it can login with username and password to get the auth token:

```
curl -X POST \
  http://localhost:8000/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "test", "password": "test"}'
  
Result:

{
    "token": "2980a86ae9627382fe9cf3de49c0997cedc80555"
}
```

Now to get the list of available products:
```
curl -X GET http://localhost:8000/products/
  
Result:
[
    {
        "id": 1,
        "title": "product1",
        "price": 1,
        "inventory_count": 1
    },
    {
        "id": 2,
        "title": "product2",
        "price": 2,
        "inventory_count": 2
    },
    {
        "id": 3,
        "title": "product3",
        "price": 3,
        "inventory_count": 3
    }
]
```

To get a single product:
```
curl -X GET http://localhost:8000/products/1/

Result:
{
  "id": 1,
  "title": "product1",
  "price": 1,
  "inventory_count": 1
}
```

Now to create a shopping cart:
```
curl -X POST \
  http://localhost:8000/carts/ \
  -H 'Authorization: Token 2980a86ae9627382fe9cf3de49c0997cedc80555' \
  -H 'Content-Type: application/json'

Result:
{
    "cart": {
        "id": 11,
        "items": [],
        "complete": false,
        "total_price": 0
    }
}
```

Now to purchase a item:
```
curl -X POST \
  http://localhost:8000/carts/11/purchase/ \
  -H 'Authorization: Token 2980a86ae9627382fe9cf3de49c0997cedc80555' \
  -H 'Content-Type: application/json' \
  -d '{
	"product_id": 2,
	"quantity": 1
}'

Result:
{
    "id": 11,
    "items": [
        {
            "product": {
                "id": 2,
                "title": "product2",
                "price": 2,
                "inventory_count": 2
            },
            "quantity": 1
        }
    ],
    "complete": false,
    "total_price": 2
}
```

Now to checkout:
```
curl -X POST \
  http://localhost:8000/carts/11/checkout/ \
  -H 'Authorization: Token 2980a86ae9627382fe9cf3de49c0997cedc80555' \
  -H 'Content-Type: application/json'
  
Result:
{
    "message": "success"
}
```

Now if we view the cart, we see that it is completed:
```
curl -X GET \
  http://localhost:8000/carts/12/ \
  -H 'Authorization: Token 2980a86ae9627382fe9cf3de49c0997cedc80555' \
  -H 'Content-Type: application/json' \

Result:
{
    "id": 11,
    "items": [
        {
            "product": {
                "id": 2,
                "title": "product2",
                "price": 2,
                "inventory_count": 1
            },
            "quantity": 1
        }
    ],
    "complete": true,
    "total_price": 2
}
```

# Improvements for future
* Different error codes for different errors (Conditioning on the returned message in the client is wrong!)
* Handling duplicate items in cart
* Writing unit/functional tests
* lock mechanism for handling `inventory_count`
* db population script
