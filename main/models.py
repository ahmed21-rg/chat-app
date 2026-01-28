from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
# Create your models here.

class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, password2=None):

        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email,
        and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class User(AbstractUser):
    username = models.CharField(max_length=100, null=False, unique=True)
    email= models.EmailField(unique=True)
   
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS= ["username"]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=300, blank=True)
    image= models.ImageField(upload_to='user_images', default='default.jpg')
    verified= models.BooleanField(default=False)

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
    
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    post_save.connect(create_user_profile, sender=User)
    post_save.connect(save_user_profile, sender=User)



class ChatRoom(models.Model):
    group_name = models.CharField(max_length=100, blank=False) # name of group or "Private Room" for private chats
    is_group = models.BooleanField(default=False) 
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_rooms', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    private_key = models.CharField(max_length=255, blank=True, null=True)  # For private rooms, can be used for encryption keys

    def __str__(self):
        return self.group_name if self.is_group else f"Private Room {self.id}"
    


class ChatRoomMember(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='members')   # which room the user belongs to
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'user')


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')  # which room the message belongs to
    sender = models.ForeignKey(User, on_delete=models.CASCADE)      # who sent the message 
    message = models.TextField()
    image = models.FileField(upload_to='images/', null=True, blank=True)
    document = models.FileField(upload_to='documents/', null=True, blank=True)
    read_by = models.JSONField(default=list)  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.room.group_name}"     # show sender and room info