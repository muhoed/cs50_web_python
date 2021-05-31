from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = "auctions"
urlpatterns = [
    #path("", views.index, name="index"),
    path("", views.ActiveListingsView.as_view(), name="index"),	
    #path("login", views.login_view, name="login"),
    path("login", views.UserLoginView.as_view(), name="login"),
    #path("logout", views.logout_view, name="logout"),
    path("logout", auth_views.LogoutView.as_view(
								extra_context={'message':'You were logged out.'}), 
								name="logout"),
    path("password_change", 
			auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
			name="password_change"),
	path("password_change_done", auth_views.PasswordChangeDoneView.as_view(
			template_name='password_change_done.html')),
    path("register", views.register, name="register"),
    #path("register", views.UserRegisterView.as_view(
	#									template_name='auctions/register.html'),
	#									name="register"),
    #path("profile", views.profile, name="profile"),
    path("profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:cat_id>/", views.categories, name="categories"),
    path("create", views.create_listing, name="create"),
    path("messenger", views.messenger, name="messenger"),
    path("listing/<int:listing_id>/", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("search", views.search, name="search")
]
