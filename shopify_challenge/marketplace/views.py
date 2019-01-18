from rest_framework import viewsets, permissions, generics
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from marketplace.models import Product, Cart, CartItem
from marketplace.serializers import ProductSerializer, UserSerializer, CreateUserSerializer, CartSerializer


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        """ Registers user in the website via POST method

        Arguments that should be in the body of POST request:
            username: username of the user
            password: plain text password of the user

        Returns:
            user: Serialized user
            token: Auth token to be used for future uses
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        })


class ProductViewSet(viewsets.ViewSet):
    def list(self, request):
        """ Returns list of products in the website

        Optional arguments:
            in_stock: if set to true, only product with inventory_count > 0 will be returned

        Returns:
            Array of serialized products
            404 if not exists
        """

        queryset = Product.objects.all()
        if request.GET.get('in_stock', None) == 'true':
            queryset = queryset.filter(inventory_count__gt=0)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """ Returns a single product in the website

        Arguments:
            pk: primary key of the specific product (usually id)

        Returns:
            Serialization of the specific product
            404 if not exists
        """

        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class CartViewSet(viewsets.ViewSet):
    """ Handles API related to shopping cart

    Authentication classes:
        Token Authentication

    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        """ Create a shopping cart

        Returns:
            serialization of the shopping cart
        """

        cart = Cart.objects.create(user=request.user)
        return Response({'cart': CartSerializer(cart).data})

    def retrieve(self, request, pk=None):
        """ Returns a shopping cart

        Returns:
            serialization of the shopping cart
            404 if not exists
        """

        cart = get_object_or_404(Cart, pk=pk)
        return Response(CartSerializer(cart).data)

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """ Used to add a product to shopping cart

        Note that currently we don't handle the problem of duplicate item in shopping cart

        Arguments in request body:
            product_id: id of the corresponding product
            quantity: quantity of the product that user wants to add to cart

        Returns:
            Serialization of the shopping cart

        Errors:
            - Empty product id
            - Empty quantity
            - Already completed cart
            - Not existing product
            - Out of stock items
        """

        try:
            product_id = request.data['product_id']
        except:
            return Response({'error': 'product_id cannot be empty'})

        try:
            quantity = int(request.data['quantity'])
        except:
            return Response({'error': 'quantity cannot be empty'})

        cart = get_object_or_404(Cart.objects.filter(user=request.user), pk=pk)

        if cart.complete:
            return Response({'message': 'Cart is already completed'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, pk=product_id)

        if(product.inventory_count >= quantity):  # Potential threading problem in future
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Item is out of stock'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """ Used to finalize a shopping cart

        Returns:
            success message

        Errors:
            * Out of stock products
            * Already completed cart
            * Empty cart
        """

        cart = get_object_or_404(Cart.objects.filter(user=request.user), pk=pk)
        if cart.complete:
            return Response({'message': 'Already completed'}, status=status.HTTP_400_BAD_REQUEST)

        out_of_stock = []

        # Potential threading problem. requires lock

        items = cart.cartitem_set.prefetch_related('product').all()

        if not items:
            return Response({'message': 'Empty cart'}, status=status.HTTP_400_BAD_REQUEST)

        for item in items:
            if item.product.inventory_count < item.quantity:
                out_of_stock.append(item.product.id)

        if out_of_stock:
            return Response({'message': 'Some products are of stock', 'detail': {'products': out_of_stock}}, status=status.HTTP_400_BAD_REQUEST)

        for item in items:
            product = item.product
            product.inventory_count -= item.quantity
            product.save()

        cart.complete = True
        cart.save()

        return Response({'message': 'success'})
