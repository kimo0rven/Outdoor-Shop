from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(label='Email address')
    first_name = forms.CharField(max_length=150, label='First name')
    last_name = forms.CharField(max_length=150, label='Last name')
    date_of_birth = forms.DateField(
        label='Date of birth',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'auth-input'}),
    )
    gender = forms.ChoiceField(
        label='Gender',
        choices=[
            ('', 'Select your gender'),
            ('male', 'Male'),
            ('female', 'Female'),
            ('non_binary', 'Non-binary'),
            ('prefer_not', 'Prefer not to say'),
        ],
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.HiddenInput()
        self.fields['username'].required = False
        self.fields['password1'].help_text = None
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm password'
        self.fields['password1'].widget.attrs.update(
            {'class': 'auth-input auth-password', 'autocomplete': 'new-password'}
        )
        self.fields['password2'].widget.attrs.update(
            {'class': 'auth-input auth-password', 'autocomplete': 'new-password'}
        )
        for name in ('first_name', 'last_name', 'email'):
            self.fields[name].widget.attrs.update({'class': 'auth-input'})
        self.fields['gender'].widget.attrs.update({'class': 'auth-select'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.strip().lower()
        return ''

    def clean(self):
        return super().clean()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.gender = self.cleaned_data['gender']
        user.is_customer = True
        user.is_staff = False
        if commit:
            user.save()
        return user


class CustomerLoginForm(forms.Form):
    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(
            attrs={
                'class': 'auth-input',
                'autocomplete': 'email',
                'placeholder': '',
            }
        ),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'auth-input',
                'autocomplete': 'current-password',
                'placeholder': '',
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get('email') or '').strip()
        password = cleaned.get('password')
        if not email or not password:
            return cleaned

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ValidationError('Invalid email or password.')
        except User.MultipleObjectsReturned:
            user_obj = User.objects.filter(email__iexact=email).first()

        user = authenticate(username=user_obj.username, password=password)
        if user is None:
            raise ValidationError('Invalid email or password.')
        self.user_cache = user
        return cleaned

    def get_user(self):
        return self.user_cache
