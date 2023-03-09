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

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = comments
        fields = ['comment',"commenter","listing",'comment_date']

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            "password": {"write_only" : True , "required": True}
        }