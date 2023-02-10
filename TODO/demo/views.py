from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as loginuser, logout
from .models import TODO, CustomUser, UserOTP
from .forms import SignupForm, UserLoginForm, TODOForm, UpdateForm, ForgetPasswordForm, PasswordResetForm
from django.contrib import messages
import random
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from .tasks import send_email_task


# Create your views here.

# -----------------------------------HOME PAGE-----------------------------
# @login_required(login_url='login')
def home(request):
    if request.user.is_authenticated:
        user = request.user
        form = TODOForm()
        todos = TODO.objects.filter(user=user).order_by('priority')

        return render(request, 'index.html', {'form': form, 'todos': todos})
    else:
        return redirect('login')


# --------------------------SIGNUP VIA OTP VERIFICATION---------------------
''' using smtp for sending otp on emails and celery for doing it in background'''


def signup(request):
    if request.method == 'GET':
        form = SignupForm()
        context = {
            "form": form
        }
        return render(request, 'signup.html', context=context)
    else:
        form = SignupForm(request.POST)
        # print(request.POST)
        print(form.is_valid())

        if form.is_valid():
            # print(request.POST)
            # email = form.cleaned_data.get('email')
            # password = form.cleaned_data.get('password')
            # import pdb
            # pdb.set_trace()
            user = form.save()
            # print('user\t', user)
            user.is_active = False  # can't signup without otp verification
            # user = authenticate(email=email, password=password)
            user.save()
            request.session['uid'] = user.id
            # print(user)

            if user is not None:
                u_otp = otp()
                print(u_otp)  # print on console(backup)
                user_otp = UserOTP(user=user, otp=u_otp)
                user_otp.save()

                print(user.email,"\t",u_otp)
                # usr = CustomUser.objects.get(id=user.id)
                send_email_task.apply_async([user.email, u_otp])

                # email = user.email

                messages.success(request, "OTP Sent Successfully, check your email")

            return render(request, 'check_otp.html', {'otp': True, 'usr': user})
        else:
            form = SignupForm()
            return render(request, 'signup.html', {'form': form})


# -------------------------LOGIN---------------------------------------
def login(request):
    if request.method == "GET":
        form = UserLoginForm()

        return render(request, 'login.html', {'form': form})

    else:
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # user = authenticate(email=email, password=password)

            user = CustomUser.objects.get(email = email)

            if user is not None:
                loginuser(request,user)
                messages.success(request, "Logged in Successfully")
                return redirect('add-todo')

            else:
                messages.warning(request, "Wrong password or email")
                return render(request, 'login.html', {'form': form})


        else:
            form = UserLoginForm()
            return render(request, 'login.html', {'form': form})


def otp():
    return random.randint(100000, 999999)


# ----------------------RESEND OTP------------------------
def Resend_otp(request):
    if request.method == "GET":
        temp = request.session['uid']
        print(temp)
        get_usr = CustomUser.objects.filter(id=temp)
        print(get_usr)

        if get_usr.exists():
            user = CustomUser.objects.get(id=temp)
            user_otp = UserOTP.objects.filter(user=user)

            if user_otp.exists():
                # user_otp = UserOTP.objects.get(user=user)
                print(user_otp)

                my_otp = otp()
                user_otp.otp = my_otp
                user_otp.save()
                print(user_otp.otp)

            return render(request, 'check_otp.html', {'otp': True, 'user': user})

    return HttpResponse("OTP Can't Send")


# ------------------------VERIFY OTP-----------------------
def verify(request):
    if request.method == "POST":
        get_otp = request.POST.get('otp')
        if get_otp:
            # import pdb
            # pdb.set_trace()
            get_usr = request.POST.get('usr')
            print(get_usr)

            user = CustomUser.objects.get(email=get_usr)

            if int(get_otp) == UserOTP.objects.filter(user=user).first().otp:
                user.is_active = True
                user.save()

                messages.success(request, f"Account Created {user.email}")

                return redirect('login')
            else:
                messages.warning(request, "Entered Wrong OTP")
                return render(request, 'check_otp.html', {'otp': True, 'user': user})


        else:
            return HttpResponse("OTP Not Found")


# -------------------------CRUD OPERATIONS-------------------------------------
@login_required(login_url='login')
def add_todo(request):
    if request.user.is_authenticated:
        user = request.user
        form = TODOForm(request.POST)

        if form.is_valid():
            todo = form.save(commit=False)
            todo.user=user
            todo.save()

            return redirect('home')

        else:
            return render(request, 'add_todo.html', {'form': form})


@login_required(login_url='login')
def update_todo(request, id):
    if request.user.is_authenticated:
        user = request.user
        obj = TODO.objects.get(pk=id)
        form = UpdateForm(request.POST, instance=obj)

        if form.is_valid():
            todo = form.save()
            todo.user = user
            todo.save()
            return redirect('home')
        else:
            form = UpdateForm(instance=obj)
            return render(request, 'updateview.html', {'form': form})


def delete_todo(request, id):
    TODO.objects.get(pk=id).delete()
    return redirect('home')


def change_status(request, id, status):
    todo = TODO.objects.get(pk=id)
    todo.status = status
    todo.save()
    return redirect('home')


@login_required(login_url='login')
def change_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = PasswordChangeForm(user=request.user, data=request.POST)
            if fm.is_valid():
                fm.save()
            return redirect('home')
        else:
            fm = PasswordChangeForm(user=request.user)
        return render(request, 'changepass.html', {'form': fm})


def signout(request):
    request.session.flush()
    logout(request)
    return redirect('login')


# ------------------------RESET PASSWORD VIA OTP--------------------------
def forgetPassword(request):
    if request.method == "GET":
        form = ForgetPasswordForm()
        return render(request, 'forget_password.html', {'form': form})

    else:
        form = ForgetPasswordForm(request.POST)

        email = request.POST.get('email')
        user_email = CustomUser.objects.filter(email=email)

        if user_email:
            user = CustomUser.objects.get(email=email)
            # user = user_email
            user.is_active = False
            user.save()
            request.session['email'] = request.POST['email']

            if user is not None:
                usr_otp = UserOTP.objects.filter(user=user)
                if usr_otp:
                    usr_otp = UserOTP.objects.get(user=user)
                    my_otp = otp()
                    usr_otp.otp = my_otp
                    usr_otp.save()
                    print(usr_otp.otp)
                    print(user.email)
                    send_email_task.apply_async([user.email, my_otp])

                    messages.success(request, "OTP Sent Successfully check email")
                return render(request, 'otp_check1.html', {'otp': True, 'usr': user})
        else:
            messages.warning(request, 'invalid user email')
            return render(request, 'forget_password.html', {'form': form})


# ---------------RESET PASSWORD VERIFY-------------------------------------
def verify1(request):
    if request.session.has_key('email'):
        email = request.session['email']
        get_otp = request.POST.get('otp')
        if get_otp:
            # import pdb
            # pdb.set_trace()
            get_usr = request.POST.get('usr')
            print(get_usr)
            usr = CustomUser.objects.get(email=get_usr)

            if int(get_otp) == UserOTP.objects.filter(user=usr).first().otp:
                usr.is_active = True
                usr.save()
                messages.success(request, 'your Email is verified')
                return redirect('password_reset')
            else:
                messages.warning(request, 'you have entered a wrong otp')
                return render(request, 'otp_check1.html', {'otp': True, 'usr': usr})


# --------------------------------FORGOT PASSWORD RESET---------------------------------------
def password_reset(request):
    if request.session.has_key('email'):
        email = request.session['email']
        print(email)
        user = CustomUser.objects.get(email=email)
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if not new_password:
                messages.warning(request, f'Enter New Password')
            elif not confirm_password:
                messages.warning(request, f'plz Enter Your Confirm Password')
            elif new_password == user.password:
                messages.warning(request, f'Password Already Exists!!!!!Plz Enter New Password ')
            elif new_password != confirm_password:
                messages.warning(request, f'Password is not matched')
            else:

                user.set_password(new_password)
                user.save()
                messages.success(request, f'Password changed successfully')
                return redirect('login')
        else:
            form = PasswordResetForm()
            return render(request, 'password_reset.html', {'form': form})
