from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'designer_status')
        read_only_fields = fields   # role and status must never be writable by the client


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate_password(self, value):
        validate_password(value)   # uses the validators in settings.py
        return value

    def create(self, validated_data):
        first, _, last = validated_data['name'].strip().partition(' ')
        email = validated_data['email']
        return User.objects.create_user(
            username=email, email=email, password=validated_data['password'],
            first_name=first, last_name=last,
        )


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Log in with email + password instead of username."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(self.username_field, None)
        self.fields['email'] = serializers.EmailField()

    def validate(self, attrs):
        account = User.objects.filter(email__iexact=attrs['email']).first()
        user = None
        if account:
            user = authenticate(self.context.get('request'),
                                username=account.username, password=attrs['password'])

        # One generic message, so it never reveals which credential was wrong (FR-CUS-11).
        if user is None:
            raise AuthenticationFailed('Invalid email or password.')
        if user.status == User.Status.SUSPENDED:
            raise AuthenticationFailed('This account is suspended. Please contact support.')

        refresh = self.get_token(user)
        return {'access': str(refresh.access_token), 'refresh': str(refresh),
                'user': UserSerializer(user).data}