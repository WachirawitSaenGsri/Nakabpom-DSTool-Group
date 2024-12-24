from django.shortcuts import render
from .utils import create_plot

# Create your views here.
def plot_view(request):
    plot_image = create_plot()
    return render(request, 'plot.html', {'plot_image': plot_image})