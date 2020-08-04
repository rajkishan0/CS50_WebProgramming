from django.contrib import admin
from .models import User, Listing, Comment, Bid



class ListingAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "description", "starting_bid")

class CommentAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "listing", "date")

class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "username")

class BidAdmin(admin.ModelAdmin):
	list_display = ("bid", "user", "listing", "date")

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)

