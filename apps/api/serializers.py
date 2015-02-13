from rest_framework import serializers, exceptions

from apps.api import fields
from apps.mainapp.models import Report, Ward, ReportCategory, City
from django.contrib.auth import authenticate
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportCategory
        fields = ('id', 'name')

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'name')

class WardSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = Ward
        fields = ('id', 'name', 'city')


class ReportSerializer(serializers.ModelSerializer):
    longitude = serializers.FloatField(source='point.x')
    latitude = serializers.FloatField(source='point.y')
    photo = fields.StdImageField(required=False, allow_null=True)

    class Meta:
        model = Report
        fields = ('id', 'title', 'category', 'ward', 'photo', 'created_at', 'updated_at', 'status', 'street', 'fixed_at',
                  'sent_at', 'email_sent_to', 'longitude', 'latitude', 'desc',
        )
        read_only_fields = ('id', 'status', 'sent_at', 'ward', 'created_at', 'updated_at', 'fixed_at', 'email_sent_to',)

    def generate_point(self, x, y):
        return Point(x, y, srid=4326)

    def create(self, validated_attrs):
        point = self.generate_point(validated_attrs['point']['x'], validated_attrs['point']['y'])
        validated_attrs['point'] = point
        try:
            ward = Ward.objects.get(geom__contains=point)
        except Ward.DoesNotExist:
            raise exceptions.ValidationError(_("Provided location doesn't belong to any of the available cities"))
        user = self.context['request'].user
        return Report.objects.create(user=user, ward=ward, **validated_attrs)

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password"')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs