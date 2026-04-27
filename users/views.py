from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .forms import RegisterForm, LoginForm, ProfileForm, AddressForm, PasswordResetRequestForm, PasswordResetConfirmForm
from .models import Address
import uuid

User = get_user_model()


def send_verification_email(user, request):
    subject = _('Verify your email - Fancy فانسي')
    verification_url = request.build_absolute_uri(
        f'/users/verify-email/{user.email_verification_token}/'
    )
    message = render_to_string('users/emails/verification.html', {
        'user': user,
        'verification_url': verification_url,
        'store_name': settings.STORE_NAME,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message, fail_silently=True)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        send_verification_email(user, request)
        messages.success(request, _('Account created! Please verify your email.'))
        return redirect('users:login')
    return render(request, 'users/register.html', {'form': form})


def verify_email_view(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.save()
        login(request, user, backend='users.backends.EmailBackend')
        messages.success(request, _('Email verified successfully! Welcome to Luxe Bags.'))
        return redirect('home')
    except User.DoesNotExist:
        messages.error(request, _('Invalid or expired verification link.'))
        return redirect('users:login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get('next', '/')
        messages.success(request, _(f'Welcome back, {user.full_name}!'))
        return redirect(next_url)
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, _('You have been logged out.'))
    return redirect('home')


def password_reset_request_view(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            token = user.generate_password_reset_token()
            reset_url = request.build_absolute_uri(f'/users/reset-password/{token}/')
            msg = render_to_string('users/emails/password_reset.html', {
                'user': user, 'reset_url': reset_url, 'store_name': settings.STORE_NAME
            })
            send_mail(_('Password Reset - Fancy فانسي'), msg, settings.DEFAULT_FROM_EMAIL, [email], html_message=msg, fail_silently=True)
        except User.DoesNotExist:
            pass
        messages.info(request, _('If an account exists, a reset link has been sent.'))
        return redirect('users:login')
    return render(request, 'users/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request, token):
    try:
        user = User.objects.get(password_reset_token=token)
        if user.password_reset_expiry and user.password_reset_expiry < timezone.now():
            messages.error(request, _('Reset link expired.'))
            return redirect('users:password_reset_request')
    except User.DoesNotExist:
        messages.error(request, _('Invalid reset link.'))
        return redirect('users:password_reset_request')
    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user.set_password(form.cleaned_data['password'])
        user.password_reset_token = None
        user.password_reset_expiry = None
        user.save()
        messages.success(request, _('Password reset successfully!'))
        return redirect('users:login')
    return render(request, 'users/password_reset_confirm.html', {'form': form})


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Profile updated successfully.'))
        return redirect('users:profile')
    orders = request.user.order_set.all().order_by('-created_at')[:10]
    addresses = request.user.addresses.all()
    return render(request, 'users/profile.html', {'form': form, 'orders': orders, 'addresses': addresses})


@login_required
def add_address_view(request):
    form = AddressForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, _('Address added.'))
        return redirect('users:profile')
    return render(request, 'users/address_form.html', {'form': form, 'title': _('Add Address')})


@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, _('Address deleted.'))
    return redirect('users:profile')


def locked_out_view(request):
    return render(request, 'users/locked_out.html', status=403)


@login_required
def change_password_view(request):
    """Allow logged-in user to change password directly (no email needed)."""
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not request.user.check_password(current_password):
            messages.error(request, _('Current password is incorrect.'))
        elif len(new_password) < 8:
            messages.error(request, _('New password must be at least 8 characters.'))
        elif new_password != confirm_password:
            messages.error(request, _('Passwords do not match.'))
        else:
            request.user.set_password(new_password)
            request.user.save()
            # Re-login so session stays valid
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, _('Password changed successfully!'))
            return redirect('users:profile')

    return render(request, 'users/change_password.html')


def send_password_reset_by_email(request):
    """Send password reset email for logged-in user (from profile page)."""
    if request.user.is_authenticated:
        token = request.user.generate_password_reset_token()
        reset_url = request.build_absolute_uri(f'/users/reset-password/{token}/')
        from django.template.loader import render_to_string
        from django.core.mail import send_mail
        msg = render_to_string('users/emails/password_reset.html', {
            'user': request.user, 'reset_url': reset_url, 'store_name': settings.STORE_NAME
        })
        send_mail(
            f'Password Reset - {settings.STORE_NAME}',
            msg, settings.DEFAULT_FROM_EMAIL,
            [request.user.email], html_message=msg, fail_silently=False
        )
        messages.success(request, _(f'Password reset link sent to {request.user.email}'))
    return redirect('users:profile')
