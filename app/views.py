from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render
from .models import Item, OrderItem, Order, Payment, Experience
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import CustomUser
from django.conf import settings
from .forms import ItemForm, ExperienceForm
from django.views.generic.edit import CreateView
from django.db.models import Sum, Q


class IndexView(View):
    def get(self, request, *args, **kwargs):
        item_data = Item.objects.all()
        item_data = item_data[:4]
        return render(request, 'app/index.html', {
            'item_data': item_data
        })
    

class ProductListView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()
        if q:
            item_data = Item.objects.filter(Q(title__icontains=q) | Q(description__icontains=q))
        else:
            item_data = Item.objects.all()
        return render(request, 'app/product_list.html', {
            'item_data': item_data,
            'q': q,
        })

    def post(self, request, *args, **kwargs):
        q = request.POST.get('q', '').strip()
        if q:
            item_data = Item.objects.filter(Q(title__icontains=q) | Q(description__icontains=q))
        else:
            item_data = Item.objects.all()
        return render(request, 'app/product_list.html', {
            'item_data': item_data,
            'q': q,
        })


class ItemDetailView(View):
    def get(self, request, *args, **kwargs):
        item_data = Item.objects.get(slug=self.kwargs['slug'])
        return render(request, 'app/product.html', {
            'item_data': item_data
        })


@login_required
def addItem(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order = Order.objects.filter(user=request.user, ordered=False)

    if order.exists():
        order = order[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        order.items.add(order_item)

    return redirect('order')


@login_required
def removeItem(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order.exists():
        order = order[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            return redirect("order")

    return redirect("product", slug=slug)


@login_required
def removeSingleItem(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order.exists():
        order = order[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            return redirect("order")

    return redirect("product", slug=slug)


class OrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            context = {'order': order}
            return render(request, 'app/order.html', context)
        except ObjectDoesNotExist:
            return render(request, 'app/order.html', {'order': None})
        
    
class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=request.user, ordered=False)
        user_data = CustomUser.objects.get(id=request.user.id)
        context = {
            'order': order,
            'user_data': user_data
        }
        return render(request, 'app/payment.html', context)

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=request.user, ordered=False)
        order_items = order.items.all()
        amount = order.get_total()

        payment = Payment(user=request.user)
        payment.stripe_charge_id = 'test_stripe_charge_id'
        payment.amount = amount
        payment.save()

        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        order.payment = payment
        order.save()
        return redirect('thanks')
    
    
class ThanksView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app/thanks.html')
    

class HistoryView(LoginRequiredMixin, ListView):
    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
        return render(request, 'app/history.html', {'orders': orders})


class ExperienceListView(View):
    def get(self, request, *args, **kwargs):
        from .models import Experience
        experiences = Experience.objects.filter(active=True)
        return render(request, 'app/experience_list.html', {'experiences': experiences})


class ExperienceDetailView(View):
    def get(self, request, *args, **kwargs):
        from .models import Experience
        experience = Experience.objects.get(slug=self.kwargs['slug'])
        capacity_range = range(1, experience.capacity + 1)
        return render(request, 'app/experience_detail.html', {
            'experience': experience,
            'capacity_range': capacity_range,
        })


@login_required
def reserve_experience(request, slug):
    from .models import Experience, Reservation
    experience = get_object_or_404(Experience, slug=slug)
    if request.method == 'POST':
        date = request.POST.get('date')
        people = int(request.POST.get('people', 1))
        # シンプルなバリデーション（本番では詳細に実装）
        reservation = Reservation.objects.create(
            user=request.user,
            experience=experience,
            reserved_date=date,
            people=people,
            status='pending'
        )
        return redirect('experience_thanks')

    capacity_range = range(1, experience.capacity + 1)
    return render(request, 'app/experience_detail.html', {
        'experience': experience,
        'capacity_range': capacity_range,
    })


class ExperienceThanksView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app/experience_thanks.html')


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'app/item_create.html'

    def form_valid(self, form):
        # 新規作成時に owner をログインユーザーに設定して保存する
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        from django.urls import reverse
        return reverse('product_list')


class ExperienceCreateView(LoginRequiredMixin, CreateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'app/experience_create.html'

    def form_valid(self, form):
        # 必要なら追加処理をここに
        return super().form_valid(form)

    def get_success_url(self):
        from django.urls import reverse
        return reverse('experience_list')


class SellerDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # 出品者のアイテム一覧
        items = Item.objects.filter(owner=request.user)
        # 各アイテムごとの売れた合計数量と売上高を計算
        sales = []
        total_revenue = 0
        for item in items:
            total_sold = OrderItem.objects.filter(item=item, ordered=True).aggregate(total=Sum('quantity'))['total'] or 0
            revenue = total_sold * (item.price or 0)
            sales.append({'item': item, 'sold': total_sold, 'revenue': revenue})
            total_revenue += revenue
        return render(request, 'app/seller_dashboard.html', {'sales': sales, 'total_revenue': total_revenue})


class UserReservationsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from .models import Reservation
        reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'app/user_reservations.html', {'reservations': reservations})

