# views.py
from .utils import create_plot ,create_plot2
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import io
import base64
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import JsonResponse

# Create your views here.

@login_required
def generate_sales_report(request):
    # Fetch orders and their associated payments within the last 30 days
    sales_data = Payment.objects.filter(date_paid__gte=(timezone.now() - timedelta(days=30))) \
        .values('date_paid') \
        .annotate(total_sales=Sum('paid_amount')) \
        .order_by('date_paid')

    # Extract the dates and total sales for plotting
    dates = [sale['date_paid'].date() for sale in sales_data]
    total_sales = [sale['total_sales'] for sale in sales_data]

    # Plotting the sales report for the last 30 days
    plt.figure(figsize=(6, 3))
    plt.plot(dates, total_sales, marker='o', linestyle='-', color='b')
    plt.title("Sales Report (Last 30 Days)")
    plt.xlabel("Date")
    plt.ylabel("Total Sales (THB)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to an in-memory buffer for the first graph
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Encode the image to base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Fetch the top-selling products based on quantity sold
    product_sales_data = OrderDetail.objects.filter(order__status='completed', order__date_ordered__gte=timezone.now() - timedelta(days=30)) \
        .values('product__name') \
        .annotate(total_quantity_sold=Sum('quantity')) \
        .order_by('-total_quantity_sold')[:10]  # Get the top 10 products

    # Extract product names and sales data
    product_names = [entry['product__name'] for entry in product_sales_data]
    quantities_sold = [entry['total_quantity_sold'] for entry in product_sales_data]

    # Plotting the top-selling products
    plt.figure(figsize=(6, 3))
    plt.bar(product_names, quantities_sold, color='g')
    plt.title("Top-Selling Products (Last 30 Days)")
    plt.xlabel("Product Name")
    plt.ylabel("Quantity Sold")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the second plot to an in-memory buffer
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    plt.close()

    # Encode the second image to base64
    top_products_image_base64 = base64.b64encode(buf2.read()).decode('utf-8')
    buf2.close()

    # Render the sales report template with both images
    return render(request, 'sales_report.html', {
        'plot_image': image_base64,  # First graph (sales over time)
        'top_products_image': top_products_image_base64  # Second graph (top-selling products)
    })

# ฟังก์ชันสำหรับ Register
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()
            messages.success(request, 'บัญชีของคุณถูกสร้างขึ้นเรียบร้อยแล้ว!')
            return redirect('login')
        else:
            messages.error(request, 'โปรดแก้ไขข้อผิดพลาดด้านล่าง')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

# ฟังก์ชันสำหรับ Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # เปลี่ยนเป็น URL ที่ต้องการให้ไปหลังจาก login สำเร็จ
            else:
                messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# ฟังก์ชันสำหรับ Logout
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    # Get the current logged-in user's profile
    user_profile = request.user.member_profile

    # Display content based on user role
    if user_profile.role == 'customer':
        return render(request, 'home_customer.html', {
            'role': 'customer',
            'products': Product.objects.all().order_by('-id')[:5],  # Last 5 products
        })
    elif user_profile.role == 'staff':
        return render(request, 'home_staff.html', {
            'role': 'staff',
            'products': Product.objects.all().order_by('-id')[:5],  # Last 5 products
        })
    elif user_profile.role == 'owner':
        return render(request, 'home_owner.html', {
            'role': 'owner',
            'products': Product.objects.all().order_by('-id')[:5],  # Last 5 products
        })

    return redirect('login')  # If no role is found, redirect to login

def product_list_view(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


# views.py
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    # Check if the user has an order with a 'pending' status
    order = Order.objects.filter(customer=request.user, status='Preparation').first()

    # If no 'pending' order exists, create a new one
    if not order:
        order = Order.objects.create(customer=request.user, status='Preparation')

    # Add product to order details
    order_detail, created = OrderDetail.objects.get_or_create(order=order, product=product)

    if created:
        order_detail.quantity = 1  # Initialize quantity to 1 if a new OrderDetail was created
    else:
        order_detail.quantity += 1  # Increase quantity if the product is already in the cart

    order_detail.save()

    # Decrease stock for the product
    if product.stock > 0:
        product.stock -= 1
        product.save()

    messages.success(request, 'สินค้าถูกเพิ่มในตะกร้าแล้ว!')
    return redirect('product_list')

@login_required
def cart_view(request):
    # Get the current order for the user with 'pending' status
    order = Order.objects.filter(customer=request.user, status='Preparation').first()

    if order:
        order_details = order.order_details.all()
        total_price = order_details.aggregate(total_price=models.Sum(models.F('product__price') * models.F('quantity')))['total_price'] or 0
    else:
        order_details = []
        total_price = 0

    # Handle POST request for updating quantities
    if request.method == 'POST':
        for order_detail in order_details:
            quantity_key = f"quantity_{order_detail.id}"
            quantity = request.POST.get(quantity_key)
            if quantity:
                order_detail.quantity = int(quantity)
                order_detail.save()

        # After updating quantities, recalculate total price
        total_price = order_details.aggregate(total_price=models.Sum(models.F('product__price') * models.F('quantity')))['total_price'] or 0

        messages.success(request, 'ตะกร้าสินค้าของคุณได้รับการอัปเดตเรียบร้อยแล้ว!')
        return redirect('cart')

    return render(request, 'cart.html', {'order_details': order_details, 'order': order, 'total_price': total_price})


@login_required
def remove_from_cart(request, order_detail_id):
    order_detail = get_object_or_404(OrderDetail, id=order_detail_id)

    # Only allow removal if the user owns the order
    if order_detail.order.customer == request.user:
        order_detail.delete()
        messages.success(request, 'สินค้าถูกลบออกจากตะกร้าเรียบร้อยแล้ว!')

    return redirect('cart')



@login_required
def checkout_view(request):
    order = Order.objects.filter(customer=request.user, status='Preparation').first()

    if not order:
        messages.error(request, 'ไม่มีคำสั่งซื้อที่ยังไม่ได้ชำระ')
        return redirect('cart')

    # Calculate the total price by multiplying price and quantity
    total_price = order.order_details.aggregate(
        total_price=models.Sum(models.F('product__price') * models.F('quantity'))
    )['total_price'] or 0

    if request.method == 'POST':
        # Handle order payment
        payment_method = request.POST.get('payment_method')

        payment = Payment.objects.create(
            order=order,
            method=payment_method,
            paid_amount=total_price,  # Use the calculated total price
        )
        order.status = 'pending'
        order.save()

        messages.success(request, 'การชำระเงินสำเร็จ!')
        return redirect('home')

    return render(request, 'checkout.html', {'order': order, 'total_price': total_price})



# ฟังก์ชันสำหรับการแสดงสินค้าทั้งหมด
@login_required
def manage_product_view(request):
    # Only allow staff or owners to access this view
    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    products = Product.objects.all()
    return render(request, 'manage_product.html', {'products': products})

# ฟังก์ชันสำหรับการเพิ่มสินค้า
@login_required
def add_product_view(request):
    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'สินค้าถูกเพิ่มเรียบร้อยแล้ว!')
            return redirect('manage_product')
        else:
            messages.error(request, 'โปรดแก้ไขข้อผิดพลาดด้านล่าง')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

# ฟังก์ชันสำหรับการแก้ไขสินค้า
@login_required
def edit_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'สินค้าถูกแก้ไขเรียบร้อยแล้ว!')
            return redirect('manage_product')
        else:
            messages.error(request, 'โปรดแก้ไขข้อผิดพลาดด้านล่าง')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})

# ฟังก์ชันสำหรับการลบสินค้า
@login_required
def delete_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'สินค้าถูกลบเรียบร้อยแล้ว!')
        return redirect('manage_product')

    return render(request, 'delete_product.html', {'product': product})

@login_required
def manage_category_view(request):
    # Only allow staff or owners to access this view
    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    categories = Category.objects.all()
    return render(request, 'manage_category.html', {'categories': categories})

# ฟังก์ชันสำหรับการเพิ่มหมวดหมู่
@login_required
def add_category_view(request):
    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'หมวดหมู่ถูกเพิ่มเรียบร้อยแล้ว!')
            return redirect('manage_category')
        else:
            messages.error(request, 'โปรดแก้ไขข้อผิดพลาดด้านล่าง')
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form})

# ฟังก์ชันสำหรับการแก้ไขหมวดหมู่
@login_required
def edit_category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'หมวดหมู่ถูกแก้ไขเรียบร้อยแล้ว!')
            return redirect('manage_category')
        else:
            messages.error(request, 'โปรดแก้ไขข้อผิดพลาดด้านล่าง')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'edit_category.html', {'form': form, 'category': category})

# ฟังก์ชันสำหรับการลบหมวดหมู่
@login_required
def delete_category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'หมวดหมู่ถูกลบเรียบร้อยแล้ว!')
        return redirect('manage_category')

    return render(request, 'delete_category.html', {'category': category})

@login_required
def order_history_view(request):
    # Fetch all orders related to the logged-in user
    orders = Order.objects.filter(customer=request.user).order_by('-date_ordered')

    # Calculate the total price for each order
    for order in orders:
        order.total_price = order.order_details.aggregate(
            total_price=models.Sum(models.F('product__price') * models.F('quantity'))
        )['total_price'] or 0

    # Pass orders to the template
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def manage_product_stock_view(request):
    # Only allow staff or owners to access this view
    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    # Get all products from the database
    products = Product.objects.all()

    # Handle the update for stock changes
    if request.method == 'POST':
        for product in products:
            stock_key = f"stock_{product.id}"
            stock_quantity = request.POST.get(stock_key)
            if stock_quantity:
                product.stock = int(stock_quantity)
                product.save()
                messages.success(request, f"สต็อกของ {product.name} ถูกอัปเดตเรียบร้อยแล้ว!")

        return redirect('manage_product_stock')

    return render(request, 'manage_product_stock.html', {'products': products})

@login_required
def manage_product_stock_Staff_view(request):
    # Only allow staff or owners to access this view
    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    # Get all products from the database
    products = Product.objects.all()

    # Handle the update for stock changes
    if request.method == 'POST':
        for product in products:
            stock_key = f"stock_{product.id}"
            stock_quantity = request.POST.get(stock_key)
            if stock_quantity:
                product.stock = int(stock_quantity)
                product.save()
                messages.success(request, f"สต็อกของ {product.name} ถูกอัปเดตเรียบร้อยแล้ว!")

        return redirect('manage_product_stock_staff')

    return render(request, 'manage_product_stock_staff.html', {'products': products})


@login_required
def manage_orders_view(request):
    # Only allow staff or owners to access this view
    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    # Get all orders from the database but exclude those with 'completed' status
    orders = Order.objects.exclude(status__in=['completed', 'canceled']).order_by('-date_ordered')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)

    # Handle the update for order status changes
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.objects.get(id=order_id)

        if new_status in ['pending', 'completed', 'canceled']:
            order.status = new_status
            order.save()
            messages.success(request, f"สถานะของคำสั่งซื้อที่ #{order.id} ถูกอัปเดตเป็น {new_status}")

        return redirect('manage_orders')

    return render(request, 'manage_orders.html', {'page_obj': page_obj})
@login_required
def manage_orders_staff_view(request):
    # Only allow staff or owners to access this view
    if request.user.member_profile.role not in ['staff', 'owner']:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    # Get all orders from the database
    orders = Order.objects.exclude(status__in=['completed', 'canceled']).order_by('-date_ordered')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)
    # Handle the update for order status changes
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.objects.get(id=order_id)

        if new_status in ['pending', 'completed', 'canceled']:
            order.status = new_status
            order.save()
            messages.success(request, f"สถานะของคำสั่งซื้อที่ #{order.id} ถูกอัปเดตเป็น {new_status}")

        return redirect('manage_orders_staff')

    return render(request, 'manage_orders_staff.html', {'page_obj': page_obj})

@login_required
def manage_employees_view(request):
    # Only allow owners to access this view
    if request.user.member_profile.role != 'owner':
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    employees = Member.objects.all()  # Fetch all employees
    return render(request, 'manage_employees.html', {'employees': employees})


@login_required
def add_employee_view(request):
    # Only allow owners to access this view
    if request.user.member_profile.role != 'owner':
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()  # Save the employee instance
            messages.success(request, 'พนักงานถูกเพิ่มเรียบร้อยแล้ว!')
            return redirect('manage_employees')
        else:
            messages.error(request, 'โปรดแก้ไขข้อผิดพลาดด้านล่าง')
    else:
        form = MemberForm()

    return render(request, 'add_employee.html', {'form': form})


@login_required
def edit_employee_view(request, pk):
    # Only allow owners to access this view
    if request.user.member_profile.role != 'owner':
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    # Fetch the employee from the database
    employee = get_object_or_404(Member, pk=pk)

    if request.method == 'POST':
        form = MemberForm(request.POST, instance=employee)  # Important: Use instance to load existing employee data
        if form.is_valid():
            form.save()  # Save the updated employee data
            messages.success(request, 'ข้อมูลพนักงานถูกแก้ไขเรียบร้อยแล้ว!')
            return redirect('manage_employees')
        else:
            messages.error(request, 'โปรดแก้ไขข้อผิดพลาดด้านล่าง')
    else:
        form = MemberForm(instance=employee)  # Load existing employee data into the form

    return render(request, 'edit_employee.html', {'form': form, 'employee': employee})



@login_required
def delete_employee_view(request, pk):
    # Only allow owners to access this view
    if request.user.member_profile.role != 'owner':
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('home')

    employee = get_object_or_404(Member, pk=pk)

    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'พนักงานถูกลบเรียบร้อยแล้ว!')
        return redirect('manage_employees')

    return render(request, 'delete_employee.html', {'employee': employee})