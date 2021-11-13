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
	path("watchlist/<int:listing_pk>/<str:action>/", 
					views.change_watchlist, name="change_watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:cat_id>/", views.categories, name="categories"),
    path("account/<int:pk>/listing/create", views.CreateListingView.as_view(
								extra_context={'title': _('create listing')},
								template_name='auctions/account/create_listing.html'), 
			name="create_listing"),
    path("account/<int:user_pk>/listing/<int:pk>/", 
						views.UpdateListingView.as_view(
								extra_context={'title': _('modify listing')},
								template_name="auctions/account/update_listing.html"),
							name="update_listing"),
	path(
		"account/<int:user_pk>/listing/<int:listing_pk>/cancel/", 
		views.cancel_listing, name="cancel_listing"
		),
	path(
		"account/<int:user_pk>/cancel_listings/", 
		views.cancel_listings, name="cancel_listings"
		),
	path("account/<int:user_pk>/listing/<int:listing_pk>/shipped/", 
		views.mark_shipped, name="listing_shipped"
		),
	path("account/<int:user_pk>/listing/<int:listing_pk>/paid/", 
		views.mark_paid, name="listing_paid"
		),
	path("account/<int:user_pk>/listing/<int:listing_pk>/delivered/", 
		views.mark_delivered, name="listing_delivered"
		),
	path("listing/<int:pk>/", views.ListingView.as_view(
								extra_context={'title': _('listing details')},
								template_name="auctions/listing.html"
								), 
							name="listing"),
	path("account/<int:pk>/product/create/", views.CreateProductView.as_view(
								extra_context={'title': _('create product')},
								template_name="auctions/account/create_product.html"),
			name="create_product"),
	path("account/<int:user_pk>/product/<int:pk>/", views.UpdateProductView.as_view(
								extra_context={'title': _('modify product')},
								template_name="auctions/account/update_product.html"),
			name="update_product"),
	path("account/<int:user_pk>/product/<int:pk>/delete/", views.DeleteProductView.as_view(
								extra_context={'title': _('confirm product delete')},
								template_name="auctions/account/product_delete_confirm.html"),
			name="delete_product"),
    #path("listing/<int:listing_pk>/comment/", views.comment, name="comment"),
	path("account/<int:user_pk>/comments/", views.ManageCommentsView.as_view(
								extra_context={'title': _('manage comments')},
								template_name="auctions/account/comments/comments.html"),
			name="manage_comments"),
	path("account/<int:user_pk>/comment/<int:comment_pk>/answer/", views.CreateRespondToCommentView.as_view(
								extra_context={'title': _('answer comment')},
								template_name="auctions/account/comments/respond.html"),
			name="answer_comment"),
    path("bid/<int:listing_pk>/<val>/", views.bid, name="bid"),
    path("account/<int:user_pk>/messenger/<int:listing_pk>/sendmessage/", views.CreateMessageView.as_view(
								extra_context={'title': _('send message')},
								template_name="auctions/account/messenger/send_message.html"),
			name="send_message"),
    path("account/messenger/<int:pk>/message/", views.MessageView.as_view(
								extra_context={'title': _('message')},
								template_name="auctions/account/messenger/message.html"),
			name="message"),
    path("account/messenger/", views.MessengerView.as_view(
        extra_context={'title': _('messenger')},
								template_name="auctions/account/messenger/messenger.html"), name="messenger"),
    path("search", views.search, name="search")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
