import matplotlib.pyplot as plt
import io
import base64

def create_plot():
    # Generate the plot
    plt.figure(figsize=(6, 4))
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 11]
    plt.plot(x, y, marker='o')
    plt.title("Sample Plot")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    
    # Save the plot to an in-memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Encode the image to base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return image_base64
