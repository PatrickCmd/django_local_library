from django.contrib import admin

from . models import Author, Book, Genre, Language, BookInstance

# Register your models here.

# admin.site.register(Author)
# admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language)

# Registering with ModelAdmin class

# Define the admin class(es)

class BookInline(admin.TabularInline):
	"""
	Defines format of inline book insertion (used in AuthorAdmin)
	"""
	model = Book

class AuthorAdmin(admin.ModelAdmin):
	list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
	fields       = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
	inlines      = [BookInline]
	
# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)


# Also Registering the admin classes for Book using the decorator(same as admin.site.register)

class BooksInstanceInline(admin.TabularInline):
	"""
	Defines format of inline book instance insertion (used in BookAdmin)
	"""
	model = BookInstance

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'display_genre')
	inlines      = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
	list_display = ('book', 'status', 'borrower', 'due_back', 'id')
	list_filter = ('status', 'due_back')

	fieldsets = (
		(None, {
			'fields': ('book', 'imprint', 'id')

		}),

		('Availability', {
			'fields': ('status', 'due_back', 'borrower')

		})
	)