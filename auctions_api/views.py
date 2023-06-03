import decimal

from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action,authentication_classes,permission_classes
from django.db.models import Max
from rest_framework.views import APIView

from auctions.models import *
from rest_framework import viewsets, status,views,mixins,decorators
from .serializers import *
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly

from rest_framework.viewsets import generics, ModelViewSet
from .permissions import IsAuthorOrReadOnly
# Create your views here.


# A view set to register new users

class ListUsers(mixins.ListModelMixin,generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self,request):
        return self.list(request)

class RegisterUser(mixins.CreateModelMixin,generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    def post(self,request):
        return self.create(request)


    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        token,created = Token.objects.get_or_create(user = serializer.instance)

        response = {"user data": serializer.data,
                    "Token": token.key
                    }

        return Response(response, status=status.HTTP_201_CREATED, headers=headers)
#A view set for the creadtor of the listing in which he can modify the listing
#contains the put(update) and delete(destroy) view
#only listing creator can access and modify


class ownerview(generics.RetrieveUpdateDestroyAPIView):
    queryset = listings.objects.all()

    serializer_class = ListingsSerializer

    authentication_classes = [TokenAuthentication]

    permission_classes = [IsAuthorOrReadOnly]


# A viewset for the users to access all listings and details about it
# contains the listing(get) and get(with pk)
# All the users should be able to access this page
class listingdetailview(mixins.ListModelMixin,mixins.RetrieveModelMixin,generics.GenericAPIView):
    queryset = listings.objects.all()
    serializer_class = ListingsSerializer

    def get(self,request,pk = None):
        if pk :
            return self.retrieve(request)
        else:
            return self.list(request)



# A viewset for the authenticated users only in which they can create a listing

class ListingCreateView(mixins.CreateModelMixin,generics.GenericAPIView):

    queryset = listings.objects.all()

    serializer_class = ListingsSerializer

    authentication_classes = [TokenAuthentication,]

    permission_classes = [IsAuthenticated,]

# listing comments function for all users
class ListingComments(mixins.ListModelMixin,generics.GenericAPIView):
    serializer_class = CommentsSerializer

    def get_queryset(self):
        try:
            return comments.objects.filter(listing= listings.objects.get(id=self.kwargs['pk']))
        except:
            return Response({
                "warning": "invalid listing id"
            }, status= status.HTTP_400_BAD_REQUEST)
    def get(self,request,pk):
        return self.list(request)



#comment functions for the authenticated users
class placecomment(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = CommentsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        try:
            return comments.objects.filter(listing= listings.objects.get(id= self.kwargs['pk']))
        except:
            return Response({
                "warning": "invalid listing id"
            },status = status.HTTP_400_BAD_REQUEST)

    def post(self,request,pk):
            if request.POST.get("commenter") is not request.user.id:
                return self.create(request)
            elif self.kwargs["pk"] is not request.POST.get("listing"):
                return Response({
                    "warning": "invalid listing id"
                },status = status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "warning": "invalid user id"
                }, status = status.HTTP_400_BAD_REQUEST)

#bid placing function for the authenticated users
@decorators.api_view(['GET','POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def place_bid(request,pk = None):
    if request.method == "GET":
        listing_detail = listings.objects.get(id = pk)
        serializers = ListingsSerializer(listing_detail)
        return Response(serializers.data)
    else:
        if "bid_value" in request.data and pk != None:
            try:
                listing = listings.objects.get(id = pk)
                user =  User(id=request.user.id)
                bid_value = decimal.Decimal(request.POST.get('bid_value'))
            except:
                json = {
                    "warning": "couldn't preform the operation"
                }
                return Response(json,status=status.HTTP_400_BAD_REQUEST)
            else:
                highest_bid = listing.highest_bid()
                if highest_bid >= decimal.Decimal(bid_value) or listing.starting_bid >= decimal.Decimal(bid_value):
                    json = {'message': "bid value is lower than the starting bid or the current price",
                            'highest_bid': highest_bid}
                    return Response(json)
                else:
                    new_bid = bids.objects.create(listing=listing, bidder=user, bid_value=decimal.Decimal(bid_value))
                    new_bid.save()
                    serializer = BidsSerializer(new_bid, many=False)
                    json = {'message': 'bid is successfully placed',
                            'operation': serializer.data}
                    return Response(json, status=status.HTTP_201_CREATED)

#enhaceing the commenting process
