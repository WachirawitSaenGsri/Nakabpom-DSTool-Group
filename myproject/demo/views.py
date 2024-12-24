from django.shortcuts import render
from .utils import create_plot ,create_plot2

# Create your views here.
def plot_view(request):
    plot_image = create_plot()
    bar_image = create_plot2()
    return render(request, 'plot.html', {'plot_image': plot_image,'bar_image': bar_image})
    