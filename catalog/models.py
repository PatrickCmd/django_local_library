from django.contrib.auth.models import User
from django.urls import reverse  # Used to generate Urls by reversing the urlpatterns
from django.db import models
from datetime import date
import uuid    # Required for unique book instances

# Create your models here.

class Genre(models.Model):
	"""
	Model representing the genre of a book(e.g Science fiction or Non fiction)
	"""

	name = models.CharField(max_length=200, help_text="Enter a book genre")

	def __str__(self):
		"""
		String for representing model object(In admin site etc.)
		"""
		return self.name

class Language(models.Model):
	"""
	Model representing language (e.g English, French, Spanish etc.)
	"""

	name = models.CharField(max_length=200, help_text="Enter the book's natural language (e.g English, French, Spanish etc.)")

	def __str__(self):
		"""
		string representation for language (in admin site etc.)
		"""

		return self.name


class Book(models.Model):
	"""
	Model represent book(but not a specific copy of book)
	"""

	title    =  models.CharField(max_length=200)
	author   =  models.ForeignKey('Author', on_delete = models.SET_NULL, null=True)
	# Foreign Key used because book can only have one author, but authors can have multiple books
	# Author as a string rather than object because it hasn't been declared yet in the file.
	summary  =  models.TextField(max_length=1000, help_text="Enter a brief description of the book")
	isbn     =  models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
	genre    =  models.ManyToManyField(Genre, help_text='Select a genre for this book')
	# ManyToManyField used because genre can contain many books. Books can cover many genres.
	# Genre class has already been defined so we can specify the object above.
	language =  models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

	class Meta:
		permissions = (('can_create_edit_delete_books', 'create edit delete books'),)

	def display_genre(self):
		"""
		Creates a string for genre.   # this is required to display genre in Admin
		"""

		return ', '.join([genre.name for genre in self.genre.all()[:3] ])
	display_genre.short_description = 'Genre'


	def __str__(self):
		"""
		String for representing model object
		"""

		return self.title

	def get_absolute_url(self):
		"""
		Returns the url to access a particular book instance
		"""

		return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
	"""
	Model representing a specific book instance(i.e a book that can be borrowed from the library)
	"""

	id        =  models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular book across whole library")
	book      =  models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
	imprint   = models.CharField(max_length=200)
	borrower  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	due_back  = models.DateField(null=True, blank=True)

	LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

	status    = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='d', help_text='Book Availability')

	class Meta:
		ordering = ["due_back"]
		permissions = (('can_mark_returned', 'set book as returned'),)

	@property
	def is_overdue(self):
		if date.today() > self.due_back:
			return True
		return False

	def __str__(self):
		"""
		string representation for model object
		"""

		return '%s (%s)' % (self.id, self.book.title)


class Author(models.Model):
	"""
	Model for representing author object
	"""

	first_name     = models.CharField(max_length=100)
	last_name      = models.CharField(max_length=100)
	date_of_birth  = models.DateField(null=True, blank=True)
	date_of_death  = models.DateField('died', null=True, blank=True)

	class Meta:
		permissions = (('can_create_edit_delete_authors', 'create edit delete authors'),)


	def get_absolute_url(self):
		"""
		Returns the url to access a particular author instance.
		"""
		return reverse('author-detail', args=[str(self.id)])

	def __str__(self):
		"""
		string representation for model object
		"""

		return '%s, %s' % (self.last_name, self.first_name)

