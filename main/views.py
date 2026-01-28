from django.db.models import Subquery, OuterRef, Q, Max, F
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import APIView, permission_classes
from rest_framework import status
from rest_framework import generics
from .models import *
from .serializer import *
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination 
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@method_decorator(csrf_exempt, name='dispatch')   
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = get_tokens_for_user(user)
        return Response({'token': token, 'msg': 'Login successful'})


def login_page(request):
    return render(request, "login.html")


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username
        })

class LogoutView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]          

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChatPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page_size'
    max_page_size = 50

class MyInboxView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ChatPagination


    def get_serializer_context(self):
        return {'request': self.request}  # to access request in serializer


    def get_queryset(self):

        user = self.request.user
        user_id = self.kwargs['user_id']

        if self.request.user.id != int(user_id):
            return Message.objects.none()
        

        rooms = ChatRoom.objects.filter(members__user=user).distinct() # get all rooms of the user 

        # Get the last message for each room
        last_message_ids = (
            Message.objects.filter(room=OuterRef("pk"))
            .order_by("-created_at")
            .values("id")[:1] 
        )    

        rooms = rooms.annotate(last_message_ids=Subquery(last_message_ids)).exclude(last_message_ids=None)

        message = (Message.objects.filter(id__in=rooms.values("last_message_ids"))
        .select_related('sender', 'room')
        .order_by("-created_at")
        )

        return message
    

class GetOrCreatePrivateRoomView(generics.CreateAPIView):    # get or create private chat room between two users

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        other_user = request.data.get('user_id')  #id of other user to chat with

        if other_user is None:  
            return Response({"detail":"user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if int(other_user) == request.user.id:
            return Response({"detail":"Cannot create private room with yourself"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            other_user = User.objects.get(id=other_user)   #get other user object
        
        except User.DoesNotExist:
            return Response({"detail":"User not found"}, status=status.HTTP_404_NOT_FOUND)

        user_ids = sorted([request.user.id, other_user.id])
        private_key = f"private_{user_ids[0]}_{user_ids[1]}"


        with transaction.atomic():
                
            room, created = ChatRoom.objects.get_or_create(
                private_key=private_key,
                defaults={'is_group': False}
            )

            ChatRoomMember.objects.get_or_create(
                room=room,
                user=request.user
            )
            ChatRoomMember.objects.get_or_create(
                room=room,
                user=other_user
            )

            #check if private room already exists
            #room = (
             #   ChatRoom.objects
              #  .filter(is_group=False, members__user=request.user)
               #.annotate(member_count=Count('members'))
                #.filter(member_count=2)
                #.distinct().first())
                        #if not room:
                # Create a new private roomroom = ChatRoom.objects.create(is_group=False)ChatRoomMember.objects.bulk_create([ChatRoomMember(room=room, user=request.user),ChatRoomMember(room=room, user=other_user)])
        
        
        return Response({"room_id": room.id,
                            "is_group": room.is_group
                            }
                            , status=status.HTTP_201_CREATED)



class GetMessageView(generics.ListAPIView): 
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ChatPagination
    
    def get_queryset(self):
        user = self.request.user
        room_id = self.kwargs['room_id']

        room = ChatRoom.objects.filter(id=room_id, members__user=user).exists()

        if not room:
            return Message.objects.none()
        
        unread_messages = Message.objects.filter(
            room__id=room_id).exclude(
                sender=user
            )

        for message in unread_messages:
            if user.id not in message.read_by:
                message.read_by.append(user.id)
                message.save(update_fields=['read_by'])    #mark messages as read by adding user id to read_by list

        return Message.objects.filter(room_id=room_id).select_related('sender').order_by('created_at')



class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        
        if not ChatRoomMember.objects.filter(
            room__id=room_id,
            user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this chat room.")
    
        serializer.save(room_id=room_id, sender=self.request.user)


class FileUploadView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer): #override post method to add room and sender before saving
        print("FILES:", self.request.FILES)
        print("DATA:", self.request.data)
        room_id = self.kwargs['room_id']
        
        room = get_object_or_404(ChatRoom, id=room_id)

        if not ChatRoomMember.objects.filter(
            room__id=room_id,
            user=self.request.user).exists():

            raise PermissionDenied("You are not a member of this chat room.")
        
        serializer.save(room=room, sender=self.request.user)
        
    


class UpdateProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
    

class CreateGroupView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupAddMemberSerializer

    def get_serializer_context(self):
        return {'request': self.request}  # gets the request object in serializer

    def perform_create(self, serializer):
        room = serializer.save(is_group=True, 
                               created_by=self.request.user
                               )  # Create the group chat room
        ChatRoomMember.objects.create(room=room, user=self.request.user)


class GroupListView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(is_group=True, members__user=self.request.user)  


class AddGroupMemberView(generics.CreateAPIView):   
    permission_classes = [IsAuthenticated]
    serializer_class = GroupAddMemberSerializer

    def post(self, request, room_id):
               
        room = ChatRoom.objects.filter(id=room_id, is_group=True).first()

        if room.created_by != request.user: # only group creator can add members
            return Response({"detail":"Only group creator can add members"}, status=status.HTTP_403_FORBIDDEN)
 

        if not room:
            return Response({"detail":"Group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Only group creator can add members
        if room.created_by != request.user:
            return Response({"detail":"Only group creator can add members"}, status=status.HTTP_403_FORBIDDEN)

        # Get user_id from request data
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"detail":"user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)  #get user object to be added

        except User.DoesNotExist:
            return Response({"detail":"User not found"}, status=status.HTTP_404_NOT_FOUND)

        if ChatRoomMember.objects.filter(room=room, user=user).exists():
            return Response({"detail":"User is already a member of the group"}, status=status.HTTP_400_BAD_REQUEST)
        
        ChatRoomMember.objects.create(room=room, user=user)
        return Response({"detail":"User added to group successfully"}, status=status.HTTP_201_CREATED)
    


class RemoveGroupMemberView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id, user_id):
        room = ChatRoom.objects.filter(id=room_id, is_group=True).first()

        if not room:
            return Response({"detail":"Group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Only group creator can remove members
        if room.created_by != request.user:
            return Response({"detail":"Only group creator can remove members"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)  #get user object to be removed

        except User.DoesNotExist:
            return Response({"detail":"User not found"}, status=status.HTTP_404_NOT_FOUND)

        membership = ChatRoomMember.objects.filter(room=room, user=user).first()

        if not membership:
            return Response({"detail":"User is not a member of the group"}, status=status.HTTP_400_BAD_REQUEST)
        
        membership.delete()
        return Response({"detail":"User removed from group successfully"}, status=status.HTTP_200_OK)


class SearchUserView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    #queryset = Profile.objects.all()

    def get_queryset(self):

        username = self.kwargs.get('username')
        logged_in_user = self.request.user

        users = Profile.objects.filter(
            (Q(user__username__icontains=username) |
            Q(full_name__icontains=username) |
            Q(user__email__icontains=username))
            &
            ~Q(user=logged_in_user)#not logged in user/except logged in user
        )
        return users


def chat_test(request):
    return render(request, "chat_test.html")
