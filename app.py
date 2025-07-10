from flask import Flask, render_template, request
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('camera.html')

@app.route('/upload', methods=['POST'])
def upload():
    data_url = request.form['image']
    header, encoded = data_url.split(",", 1)
    image_data = base64.b64decode(encoded)

    with open("weather_image.jpg", "wb") as f:
        f.write(image_data)

    return "✅ Image saved!"

if __name__ == '__main__':
    app.run(debug=True)
