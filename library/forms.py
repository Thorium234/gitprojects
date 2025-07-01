from django import forms
from .models import Book, Student, Borrow, Shelf, RevisionPaper, Room
from django.utils import timezone

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'publishers',
            'first_publication',
            'ISBN',
            'book_number',
            'shelf',
            'book_picture',
        ]

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'admission_number', 'room', 'student_picture']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['form', 'stream', 'class_teacher']

from django import forms
from .models import Book, Student, Borrow, Shelf, RevisionPaper, Room
from django.utils import timezone

class BorrowForm(forms.ModelForm):
    admission_number = forms.IntegerField(
        label="Student Admission Number",
        help_text="Enter the admission number of the student borrowing this book."
    )
    days = forms.IntegerField(
        label="Number of Days",
        min_value=1,
        help_text="Enter how many days the book will be borrowed for."
    )

    class Meta:
        model = Borrow
        fields = ['book', 'admission_number', 'days']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        borrowed_books = Borrow.objects.filter(returned=False).values_list('book_id', flat=True)
        self.fields['book'].queryset = Book.objects.exclude(id__in=borrowed_books)

    def clean(self):
        cleaned_data = super().clean()
        admission_number = cleaned_data.get('admission_number')
        book = cleaned_data.get('book')
        days = cleaned_data.get('days')
        # Validate student exists
        try:
            student = Student.objects.get(admission_number=admission_number)
        except Student.DoesNotExist:
            raise forms.ValidationError("No student with this admission number exists.")
        # Validate student doesn't have active borrow
        if Borrow.objects.filter(student=student, returned=False).exists():
            raise forms.ValidationError(f"{student} already has a borrowed book. Return it before borrowing another.")
        # Validate book is available
        if book and Borrow.objects.filter(book=book, returned=False).exists():
            raise forms.ValidationError(f"'{book.title}' is already borrowed and must be returned before borrowing again.")
        # Validate days
        if not days or days < 1:
            raise forms.ValidationError("Please enter a valid number of days.")
        # ------ NEW: Check per-shelf borrow limit ------
        if book and book.shelf and book.shelf.max_borrow_per_student:
            current_borrows_on_shelf = Borrow.objects.filter(
                student=student,
                book__shelf=book.shelf,
                returned=False
            ).count()
            if current_borrows_on_shelf >= book.shelf.max_borrow_per_student:
                raise forms.ValidationError(
                    f"{student} has already borrowed the maximum ({book.shelf.max_borrow_per_student}) books allowed from the shelf '{book.shelf.shelf_name}'."
                )
        # Store student for use in view
        self.student = student
        return cleaned_data

# ... rest of forms remain unchanged

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = []

class RevisionPaperForm(forms.ModelForm):
    class Meta:
        model = RevisionPaper
        fields = ['title', 'room', 'subject', 'file']

class ShelfForm(forms.ModelForm):
    class Meta:
        model = Shelf
        fields = ['shelf_name', 'shelf_code', 'category','max_borrow_per_student']