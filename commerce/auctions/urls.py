from django.conf import settings
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.utils.translation import gettext, gettext_lazy as _

from . import views
from .forms import UserPasswordResetForm

app_name = "auctions"
urlpatterns = [
    path("", views.ActiveListingsView.as_view(
								extra_context={'title': _('home')}),
								name="index"),
    path("login", 
			views.UserLoginView.as_view(
								extra_context={'title': _('login')},
								template_name='auctions/auth/login.html'), 
			name="login"),	
    path("logout", 				
			auth_views.LogoutView.as_view(
								extra_context={'message':_('You were logged out.')}), 
			name="logout"),
    path("password_change", 
			auth_views.PasswordChangeView.as_view(
								extra_context={'title': _('password change')},
								template_name='auctions/auth/password_change.html',
								success_url=reverse_lazy('auctions:password_change_done')),
			name="password_change"),
	path("password_change_done", 
			auth_views.PasswordChangeDoneView.as_view(
								extra_context={'title': _('password change completed')},
								template_name='auctions/auth/password_change_done.html'),
			name="password_change_done"),
	path("password_reset", 
			views.UserPasswordResetView.as_view(
								template_name="auctions/auth/password_reset_form.html",
								form_class=UserPasswordResetForm,
								extra_context={'title': _('password reset')},
								extra_email_context={'topic': 'pwdreset'},
								email_template_name="auctions/auth/emails/password_reset_email.html",
								subject_template_name="auctions/auth/emails/password_reset_subject.txt", 
								success_url=reverse_lazy("auctions:password_reset_done")), 
			name='password_reset'),
	path("password_reset_done", 
			auth_views.PasswordResetDoneView.as_view(
								template_name="auctions/auth/password_reset_done.html",
								extra_context={'title': _('password reset link sent')}
								),
			name='password_reset_done'),
	path("get_email_filenames", 
			views.get_message_content, 
			name="get_email_filenames"),
	path("password_reset_confirm/<uidb64>/<token>/", 
			auth_views.PasswordResetConfirmView.as_view(
								extra_context={'title': _('enter new password')},
								template_name="auctions/auth/password_reset_confirm.html",
								success_url=reverse_lazy('auctions:password_reset_complete')),
			name='password_reset_confirm'),
	path("password_reset_complete", 
			auth_views.PasswordResetCompleteView.as_view(
								extra_context={'title': _('password reset completed')},
								template_name='auctions/auth/password_reset_complete.html'),
			name='password_reset_complete'),
    path("register", 
			views.UserRegisterView.as_view(
								extra_context={'title': _('register')},
								template_name='auctions/auth/register.html'),
			name="register"),
    path("registration_confirm", 
			views.RegistrationConfirmView.as_view(
								extra_context={'title': _('confirm registration')},
								extra_email_context={'topic': 'regactivation'},
								template_name = 'auctions/auth/registration_confirm.html'),
			name="registration_confirm"),
	path("registration_complete/<uidb64>/<token>/", 
			views.RegistrationCompleteView.as_view(
								extra_context={'title': _('registration completed')},
								template_name = "auctions/auth/registration_complete.html"),
			name="registration_complete"),
	path("create_profile/<int:pk>/",
			views.UserProfileCreateView.as_view(
								extra_context={'title': _('create profile')},
								template_name="auctions/account/create_profile.html"),
			name="create_profile"),
    path("profile/<int:pk>/",
			views.ProfileView.as_view(
								extra_context={'title': _('account')},
								template_name='auctions/account/profile.html'), 
			name="profile"),
	path("profile/<int:pk>/credentials/",
			views.CredentialsUpdateView.as_view(
								extra_context={'title': _('credentials')},
								template_name="auctions/account/credentials.html"),
			name="credentials"),
	path("profile/<int:pk>/information/",
			views.PersonalInfoView.as_view(
								extra_context={'title': _('personal and contact information')},
								template_name="auctions/account/information.html"),
			name="user_info"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:cat_id>/", views.categories, name="categories"),
    path("create", views.create_listing, name="create_listing"),
    path("messenger", views.messenger, name="messenger"),
    path("listing/<int:listing_id>/", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("search", views.search, name="search")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
