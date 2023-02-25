import decimal

from django.shortcuts import render
from rest_framework.decorators import action
from django.db.models import Max
from auctions.models import *
from rest_framework import viewsets, status
from .serializers import *
from rest_framework.response import Response
# Create your views here.


class ListingsEndPoint(viewsets.ModelViewSet):
    queryset = listings.objects.all()
    serializer_class = ListingsSerializer

    @action(methods=["POST"],detail=True)
    def place_bid(self,request,pk = None):
        if "bid_value" in self.request.data and pk != None:
            listing = listings.objects.get(id = pk)
            user = User.objects.get(username= self.request.data['username'])
            bid = self.request.data['bid_value']

            highest_bid = listing.highest_bid()

            if highest_bid >= decimal.Decimal(bid) or listing.starting_bid >= decimal.Decimal(bid):
                json = {'message': "bid value is lower than the starting bid or the current price",
                        'highest_bid': highest_bid}
                return Response(json)
            else :
                new_bid = bids.objects.create(listing=listing,bidder=user,bid_value=decimal.Decimal(bid))
                new_bid.save()
                serializer = BidsSerializer(new_bid,many=False)
                json = {'message': 'bid is successfully placed',
                        'operation': serializer.data}
                return Response(json,status=status.HTTP_201_CREATED)
        else:
            json = {'message': 'missing bid value'}
            return Response(json, status=status.HTTP_400_BAD_REQUEST)

