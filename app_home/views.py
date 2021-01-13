from django.shortcuts import render, redirect, HttpResponse

import re

# forms组件
from app_home.home_forms import *

# orm
from app_home.models import *

import json

# 全局变量，当前页面IP
request_ip = None


def get_set_ip(request):
    """ 获取当前页面的IP"""
    global request_ip
    request_ip = re.findall(r'\'[\w/]+\'', str(request))
    request_ip = request_ip[0][1:-1]


def home(request):
    """ 主页，显示所有书籍 """
    # 用户登录状态过期，回到login
    if request.user.is_anonymous:
        return redirect('/app_auth/login/')
    else:
        # post，添加图书
        if request.method == "POST":
            book_name = request.POST.get('book_name').replace("《", "").replace("》", "")
            book_name = f'《{book_name}》'
            pub_id = request.POST.get('pub_id')
            auth_id_list = request.POST.getlist('auth_id_list')
            form = AddFormBook(request.POST)
            # forms规则校验
            if form.is_valid() and pub_id:
                book_obj = Book.objects.create(book_name=book_name, pub_id=pub_id)
                book_obj.auth.add(*auth_id_list)
                # 添加成功，回到主页
                return redirect('/app_home/home/')
            else:
                # 添加失败提示
                return render(request, 'home/home_err.html', locals())
        # get
        get_set_ip(request)  # 获取当前IP
        usr = request.user.username  # 用户名
        book_obj = Book.objects.all().order_by('-pk')  # 所有书
        form = AddFormBook()
        pub_obj = Publish.objects.all()  # 所有出版社，添加新书时用
        auth_obj = Author.objects.all()  # 所有作者，添加新书时用
        return render(request, "home/home.html", locals())


def home_err(request):
    """ 书籍添加失败提示 """
    return render(request, "home/home_err.html")


def publish(request):
    """ 出版社页面 """
    # post，添加出版社
    if request.method == "POST":
        pub_name = request.POST.get('pub_name')
        form = AddFormPub(request.POST)
        # forms校验
        if form.is_valid():
            Publish.objects.create(pub_name=pub_name)
            # 添加成功，刷新页面
            return redirect('/app_home/publish/')
    usr = request.user.username
    pub_obj = Publish.objects.all().order_by('-pk')
    form = AddFormPub()
    return render(request, "home/publish.html", locals())


def author(request):
    """ 作者页面 """
    # post，添加作者
    if request.method == "POST":
        auth_name = request.POST.get('auth_name')
        form = AddFormAuth(request.POST)
        # forms校验
        if form.is_valid():
            Author.objects.create(auth_name=auth_name)
            # 添加成功，刷新页面
            return redirect('/app_home/author/')
    # get
    usr = request.user.username
    auth_obj = Author.objects.all().order_by('-pk')
    form = AddFormAuth()
    return render(request, "home/author.html", locals())


def delete_book(request, b_id):
    """ 删除书 """
    Book.objects.filter(pk=b_id).delete()
    return redirect(request_ip)


def delete_auth(request, a_id):
    """ 删除作者"""
    Author.objects.filter(pk=a_id).delete()
    return redirect('/app_home/author/')


def delete_pub(request, p_id):
    """ 删除出版社，及其对应所有书籍 """
    Publish.objects.filter(pk=p_id).delete()
    return redirect('/app_home/publish/')


def change_book(request, b_id):
    """ 修改书籍信息 """
    # post
    if request.method == "POST":
        book_name = request.POST.get('book_name')
        pub_id = request.POST.get('pub_id')
        auth_id_list = request.POST.get('auth_id_list')
        auth_id_list = json.loads(auth_id_list)
        # 修改表数据
        Book.objects.filter(pk=b_id).update(book_name=book_name, pub_id=pub_id)
        book_obj = Book.objects.filter(pk=b_id).first()
        book_obj.auth.clear()
        book_obj.auth.add(*auth_id_list)
        return HttpResponse(request_ip)


def change_auth(request, a_id):
    """ 修改作者信息 """
    # post
    if request.method == "POST":
        form = AddFormAuth(request.POST)
        # forms校验
        if form.is_valid():
            auth_name = request.POST.get('auth_name')
            # 修改表数据
            Author.objects.filter(pk=a_id).update(auth_name=auth_name)
            return HttpResponse(request_ip)


def change_pub(request, p_id):
    """ 修改出版社信息 """
    # post
    if request.method == "POST":
        form = AddFormPub(request.POST)
        # forms校验
        if form.is_valid():
            pub_name = request.POST.get('pub_name')
            # 修改表数据
            Publish.objects.filter(pk=p_id).update(pub_name=pub_name)
            return HttpResponse(request_ip)


def pub_info(request, p_id):
    """ 出版社超链接：显示该出版社的所有图书 """
    usr = request.user.username
    pub_obj = Publish.objects.filter(pk=p_id).first()
    pub_all_obj = Publish.objects.all()
    auth_all_obj = Author.objects.all()
    book_obj = Book.objects.filter(pub=pub_obj).order_by('-pk')
    # 获取当前请求ip
    get_set_ip(request)
    return render(request, 'home/pub_info.html', locals())


def auth_info(request, a_id):
    """ 作者超链接：显示该作者的所有图书 """
    usr = request.user.username
    auth_obj = Author.objects.filter(pk=a_id).first()
    auth_all_obj = Author.objects.all()
    book_obj = auth_obj.book_set.all().order_by('-pk')
    pub_obj = Publish.objects.all()
    # 获取当前请求ip
    get_set_ip(request)
    return render(request, 'home/auth_info.html', locals())
