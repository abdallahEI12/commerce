from auctions.models import *
from rest_framework import serializers


class ListingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = listings
        fields = ['created_by','id','active','title','description',
                  'starting_bid','current_price','image','category']
class BidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = bids
        fields = ['bidder','bid_value','listing']