"""Views for the recruitment board."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def board(request):
    """Render the recruitment board for authenticated users."""
    return render(request, "recruitment/board.html")