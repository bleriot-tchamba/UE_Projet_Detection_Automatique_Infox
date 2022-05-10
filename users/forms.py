from django import forms
from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model

from users.models import MyUser

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(max_length=255, required=True)
        
    def clean_username(self):
        username = self.data.get('username', None)
        if username:
            username = username.strip()
        if get_user_model().objects.filter(username__exact=username).count() != 1:
            raise forms.ValidationError('Aucun utilisateur avec ce username.')
        return get_user_model().objects.get(username=username)
    
    def clean_password(self):
        password = self.data.get('password', None)
        if not password:
            raise forms.ValidationError("Mots de passes vide")
        
        try:
            user = get_user_model().objects.get(username=self.data.get('username', None))
        
            if not self.cleaned_data['username'].check_password(password):
                raise forms.ValidationError("username et mot de passe ne correspondent pas.")
        except get_user_model().DoesNotExist:
            raise forms.ValidationError("Aucun utilisateur")
        return password
    

class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(required=True)
    
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email', 'confirm_password']
        
    def clean_username(self):
        username = self.data.get('username', None)
        print("hors")
        if get_user_model().objects.filter(username__exact=username).count() != 0:
            print('Dnas')
            raise forms.ValidationError('Un utilisateur avec ce username existe déjà.')
        return username
        
    def clean_password(self):
        password = self.data.get('password', None)
        if not password:
            raise forms.ValidationError("Mots de passes vide")
        if password != self.data['confirm_password']:
            raise forms.ValidationError("Les mots de passes ne sont pas identiques")
        return password
    
    def save(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        user = None

        with transaction.atomic():
            try:
                user = get_user_model().objects.create_user(
                    email=email, username=username, 
                    password=self.cleaned_data['password'],
                    is_active=True
                )
                user.save()
                my_user = MyUser(user=user)
                my_user.save()

            except IntegrityError as e:
                print(e)
        return user