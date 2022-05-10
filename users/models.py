import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone




def upload_to(instance, file_name):
    return f'media/{uuid.uuid4()}{file_name}'
    
license_type = (
    ("ANNUAL", "ANNUAL"),
    ("MONTHLY", "MONTHLY"),
    ("NUMBER", "REQUEST_NUMBER")
)
    
class License(models.Model):
    type = models.CharField(max_length=255, blank=False, null=False, choices=license_type)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    request_number = models.IntegerField(blank=True, null=True)
    token = models.CharField(max_length=1024)
    
    def is_expired(self):
        if self.type == license_type[2][0]:
            return self.request_number == 0
        else:
            pass_time = timezone.now() - self.start_date
            if self.type == license_type[1][0]: 
                return pass_time.day() > 30
            else:
                return pass_time.year() > 1
    
    def rest(self)->str:
        if self.type == license_type[2][0]:
            return f'{self.request_number} requête(s)'
        else:
            pass_time = self.end_date - self.start_date
            if self.type == license_type[1][0]: 
                return f'{pass_time.day()} jours'
            else:
                return f'{pass_time.month()} mois: {pass_time.day()} jour: {pass_time.hour()} heures'
    

class MyUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    license = models.ForeignKey(License, on_delete=models.CASCADE, null=True, blank=True)
    profile_image = models.ImageField(upload_to=upload_to, null=True, blank=True, default="media/default.png")
    