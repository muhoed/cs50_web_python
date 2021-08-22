from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.ActiveListingsView.as_view(
								extra_context={'title': 'home'}),
								name="index"),
    path("login", 
			views.UserLoginView.as_view(
								extra_context={'title': 'login'},
								template_name='auctions/auth/login.html'), 
			name="login"),	
    path("logout", 				
			auth_views.LogoutView.as_view(
								extra_context={'message':'You were logged out.'}), 
			name="logout"),
    path("password_change", 
			auth_views.PasswordChangeView.as_view(
								extra_context={'title': 'password change'},
								template_name='auctions/auth/password_change.html',
								success_url=reverse_lazy('auctions:password_change_done')),
			name="password_change"),
	path("password_change_done", 
			auth_views.PasswordChangeDoneView.as_view(
								extra_context={'title': 'password change completed'},
								template_name='auctions/auth/password_change_done.html'),
			name="password_change_done"),
	path("password_reset", 
			auth_views.PasswordResetView.as_view(), 
			name='password_reset'),
	path("password_reset_done", 
			auth_views.PasswordResetDoneView.as_view(),
			name='password_reset_done'),
	path("password_reset_confirm", 
			auth_views.PasswordResetConfirmView.as_view(),
			name='password_reset_confirm'),
	path("password_reset_complete", 
			auth_views.PasswordResetCompleteView.as_view(),
			name='password_reset_complete'),
    path("register", 
			views.UserRegisterView.as_view(
								extra_context={'title': 'register'},
								template_name='auctions/auth/register.html'),
			name="register"),
    path("registration_confirm", 
			views.RegistrationConfirmView.as_view(
								extra_context={'title': 'confirm registration'},
								template_name = 'auctions/auth/registration_confirm.html'),
			name="registration_confirm"),
	path("registration_complete/<uidb64>/<token>/", 
			views.RegistrationCompleteView.as_view(
								extra_context={'title': 'registration completed'},
								template_name = "auctions/auth/registration_complete.html"),
			name="registration_complete"),
	path("create_profile/<int:pk>/",
			views.UserProfileCreateView.as_view(
								extra_context={'title': 'create profile'},
								template_name="auctions/account/create_profile.html"),
			name="create_profile"),
    path("profile/<int:pk>/",
			views.ProfileView.as_view(
								extra_context={'title': 'account'},
								template_name='auctions/account/profile.html'), 
			name="profile"),
	path("credentials/<int:pk>/",
			views.CredentialsUpdateView.as_view(
								extra_context={'title': 'credentials'},
								template_name="auctions/account/credentials.html"),
			name="credentials"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:cat_id>/", views.categories, name="categories"),
    path("create", views.create_listing, name="create_listing"),
    path("messenger", views.messenger, name="messenger"),
    path("listing/<int:listing_id>/", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("search", views.search, name="search")
]
