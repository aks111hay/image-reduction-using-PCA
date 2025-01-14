from flask import Flask, request, send_file, render_template
from PIL import Image
import numpy as np
from io import BytesIO

app = Flask(__name__)
def pca_image_reduction(image_data, reduction_percentage):
    img = Image.open(BytesIO(image_data))
    img_data = np.array(img)
    original_shape = img_data.shape 
    img_data = img_data.reshape(-1,2)
    
    mean = np.mean(img_data, axis=0)
    centered = img_data - mean
    covariance_matrix = np.cov(centered.T)+mean
    
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    sorted_indices = np.argsort(eigenvalues)[::-1]
    num_components = int(len(eigenvalues) * reduction_percentage / 100)
    top_eigenvectors = eigenvectors[:, sorted_indices[:num_components]]
    
    reduced_data = np.dot(centered,top_eigenvectors)
    reconstructed_data = np.dot(reduced_data,top_eigenvectors.T)
    reconstructed_data = reconstructed_data.reshape(original_shape)
    reduced_img = Image.fromarray(np.uint8(reconstructed_data))
    return reduced_img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No file part", 400

    image_file = request.files['image']
    if image_file.filename == '':
        return "No selected file", 400
    image_data = image_file.read()
    reduction_percentage = int(request.form['reduction'])
    reduced_img = pca_image_reduction(image_data, reduction_percentage)
    img_io = BytesIO()
    reduced_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, as_attachment=True, download_name='reduced_image.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
