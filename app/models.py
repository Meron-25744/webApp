from django.db import models
from django.conf import settings


class Item(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    price = models.IntegerField()
    category = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='images', blank=True, null=True, default='images/20200501_noimage.jpg')

    def __str__(self):
        return self.title
    

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"{self.item.title}：{self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total

    def __str__(self):
        return self.user.email
    

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=50)
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class Experience(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.IntegerField()
    duration_minutes = models.IntegerField(help_text='所要時間（分）', default=60)
    capacity = models.IntegerField(help_text='1回あたりの最大参加人数', default=10)
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='experience_images', blank=True, null=True, default='images/20200501_noimage.jpg')
    active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', '予約受付'),
        ('confirmed', '確定'),
        ('cancelled', 'キャンセル'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE)
    reserved_date = models.DateField()
    people = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.experience.title} - {self.user.email} ({self.reserved_date})"
