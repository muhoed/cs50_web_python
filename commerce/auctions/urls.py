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
	path("account/<int:pk>/profile",
			views.ProfileView.as_view(
								extra_context={'title': _('create profile')},
								template_name="auctions/account/user_profile.html"),
			name="user_profile"),
    path("account/<int:pk>/summary/",
			views.ActivitiesSummaryView.as_view(
								extra_context={'title': _('account')},
								template_name='auctions/account/summary.html'), 
			name="profile"),
	path("account/<int:pk>/credentials/",
			views.CredentialsUpdateView.as_view(
								extra_context={'title': _('credentials')},
								template_name="auctions/account/credentials.html"),
			name="credentials"),
	path("account/<int:pk>/selling/",
			views.SellActivitiesView.as_view(
								extra_context={'title': _('selling activities')},
								template_name="auctions/account/selling.html"),
			name="sell_activities"),
	path("account/<int:pk>/buying/",
			views.BuyActivitiesView.as_view(
								extra_context={'title': _('purchase activities')},
								template_name="auctions/account/buying.html"),
			name="purchase_activities"),
	path("account/<int:pk>/watchlist/",
			views.UserWatchlistView.as_view(
								extra_context={'title': _('watchlist')},
								template_name="auctions/account/watchlist.html"),
			name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:cat_id>/", views.categories, name="categories"),
    path("account/<int:pk>/listing/create", views.CreateListingView.as_view(
								extra_context={'title': _('create listing')},
								template_name='auctions/account/create_listing.html'), 
			name="create_listing"),
	path("account/<int:pk>/product/create/", views.ProductView.as_view(
								extra_context={'title': _('create product')},
								template_name="auctions/account/create_product.html"),
			name="create_product"),
    path("messenger", views.messenger, name="messenger"),
    path("account/<int:pk>/listing/<int:listing_pk>/", 
						views.UpdateListingView.as_view(
								extra_context={'title': _('listing')},
								template_name="auctions/account/update_listing.html"),
							name="update_listing"),
    path("bid", views.bid, name="bid"),
    path("search", views.search, name="search")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
