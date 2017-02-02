from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views import generic

from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm
import datetime

# Create your views here.

def index(request):
	"""
	View function for home page of site
	"""

	# Generate counts of some of main objects
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()
	num_genres    = Genre.objects.all().count()
	# Available books(status='a')
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()
	num_authors = Author.objects.count()   # The 'all' is implied by default
	# Number of visits to this view, as counted in session variable
	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1

	# Render the HTML template index.html with the data in the context variable
	context = {
		'num_books': num_books,
		'num_instances': num_instances,
		'num_instances_available': num_instances_available,
		'num_authors': num_authors,
		'num_genres': num_genres,
		'num_visits': num_visits
	}

	return render(request, 'catalog/index.html', context)


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):

	book_inst = get_object_or_404(BookInstance, pk=pk)

	# If POST request then process the Form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request (binding)
		form = RenewBookForm(request.POST)

		# check if form is valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			book_inst.due_back = form.cleaned_data['renewal_date']
			book_inst.save()

			# redirect to a new URL
			return HttpResponseRedirect(reverse('all-borrowed'))
	else:
		# If this is a GET (or any other method) create the default form.
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

	context = {
		'form': form,
		'bookinst': book_inst
	}

	return render(request, 'catalog/book_renew_librarian.html', context)


class BookListView(generic.ListView):

	model = Book     # generic view queries the database to all records for Book model

	paginate_by = 20  # pagination per page

	context_object_name = 'book_list'
	query_set = Book.objects.filter(title__icontains='Tutorial')[:5] #  Get 5 Books containing the title Tutorial
	template_name  = 'catalog/book_list.html'


class BookDetailView(generic.DetailView):

	model = Book


class AuthorListView(generic.ListView):

	model = Author

	paginate_by = 10

	context_object_name = 'author_list'
	template_name = 'catalog/author_list.html'


class AuthorDetailView(generic.DetailView):

	model = Author

	# paginate_by = 1


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	"""
	Generic class-based view listing books on loan to current user
	"""

	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
	"""
	Generic class-based view listing all books on loan
	"""
	permission_required = 'catalog.can_mark_returned'

	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')


class AuthorCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):

	permission_required = 'catalog.can_create_edit_delete_authors'
	model = Author
	fields = '__all__'
	initial = {'date_of_death':'12/10/2016',}


class AuthorUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

	permission_required = 'catalog.can_create_edit_delete_authors'
	model = Author
	fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):

	permission_required = 'catalog.can_create_edit_delete_authors'
	model = Author
	success_url = reverse_lazy('authors')


class BookCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):

	permission_required = 'catalog.can_create_edit_delete_books'
	model = Book
	fields = '__all__'


class BookUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

	permission_required = 'catalog.can_create_edit_delete_books'
	model = Book
	fields = '__all__'


class BookDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):

	permission_required = 'catalog.can_create_edit_delete_books'
	model = Book
	success_url = reverse_lazy('books')
