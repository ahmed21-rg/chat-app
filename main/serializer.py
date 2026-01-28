from .models import ChatRoom, Message, User, Profile
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['id','username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, data):
        
        if data['password'] != data['password2']:
            raise serializers.ValidationError('password do not match')    
        
        validate_password(data['password'])
        
        return data
    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=100)
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'user', 'bio', 'image']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'group_name', 'is_group', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(
    source="sender.username",
    read_only=True
    )
    room_id = serializers.IntegerField(source="room.id", read_only=True)
    message = serializers.CharField(required=False, allow_blank=True)

    other_user = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    document_url = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = [
            'id',
            'room',
            'room_id',
            'sender',
            'other_user',
            'image',
            'document',
            'image_url',
            'document_url',
            'sender_username',
            'message',
            'read_by',
            'created_at',
            'unread_count'
        ]
        read_only_fields = [
            'room',
            'sender',
            'created_at',
            'room_id',
            'sender_username',
            'other_user'
        ]
        extra_kwargs = {
            "image": {"required": False, "allow_null": True},
            "document": {"required": False, "allow_null": True},
        }
       

    def get_other_user(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        
        current_user = request.user
        room = obj.room   # Get the chat room of the message

        if room.is_group:
            return None
        
        member = room.members.exclude(user=current_user).select_related('user').first()   # get the other member of the room 

        if member:
            return {
                'id': member.user.id,
                'username': member.user.username
            }
        return None
    

    def get_unread_count(self, obj):
        request = self.context.get('request')
        
        user = request.user
        if not request or not user.is_authenticated:
            return 0
        
        return (Message.objects.filter(
            room=obj.room,
        ).exclude(sender=user
        ).exclude(read_by__contains=[user.id]
        ).count()
        )     # count of unread messages for the user in the room

    def get_image_url(self, obj):
        
        request = self.context.get('request')
        
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        
        return None

    def get_document_url(self, obj):
        request = self.context.get('request')
        if obj.document and request:
            return request.build_absolute_uri(obj.document.url)
        return None
        
    def validate(self, attrs):
        message = attrs.get('message', '').strip()
        image = attrs.get('image')
        document = attrs.get('document')

        if not message and not image and not document:
            raise serializers.ValidationError("Message cannot be empty if no image or document is provided.")
        attrs["message"] = message
        return attrs

    
class GroupAddMemberSerializer(serializers.ModelSerializer):
    is_creator = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'group_name', 'is_group', 'created_by', 'is_creator', 'created_at']

    def get_is_creator(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.created_by == request.user
    
