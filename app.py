from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dense, Dropout, LSTM, Reshape
from tensorflow.keras.preprocessing.text import Tokenizer
import numpy as np
import pandas as pd
import colorsys

app = Flask(__name__, static_folder='templates')
CORS(app)

# Load model with custom objects
# model = load_model('model.h5', custom_objects=custom_objects)
model = load_model('model.keras')

data = pd.read_csv('colors.csv')
names = data["name"]

maxlen = 25
t = Tokenizer(char_level=True)
t.fit_on_texts(names)
tokenized = t.texts_to_sequences(names)
padded_names = tf.keras.preprocessing.sequence.pad_sequences(tokenized, maxlen=maxlen)
one_hot_names = tf.keras.utils.to_categorical(padded_names)
num_classes = one_hot_names.shape[-1]

def scale(n):
    return int(n * 255)

def get_complementary_color(rgb):
    hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    complementary_hue = (hsv[0] + 0.5) % 1
    complementary_rgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(complementary_hue, hsv[1], hsv[2]))
    return complementary_rgb

def get_analogous_colors(rgb):
    hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    analogous_hues = [(hsv[0] + 0.083) % 1, (hsv[0] - 0.083) % 1]
    analogous_colors = [tuple(round(c * 255) for c in colorsys.hsv_to_rgb(hue, hsv[1], hsv[2])) for hue in analogous_hues]
    return analogous_colors

def get_triadic_colors(rgb):
    hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    triadic_hues = [(hsv[0] + 0.333) % 1, (hsv[0] + 0.667) % 1]
    triadic_colors = [tuple(round(c * 255) for c in colorsys.hsv_to_rgb(hue, hsv[1], hsv[2])) for hue in triadic_hues]
    return triadic_colors

def get_tetradic_colors(rgb):
    hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    tetradic_hues = [(hsv[0] + 0.25) % 1, (hsv[0] + 0.5) % 1, (hsv[0] + 0.75) % 1]
    tetradic_colors = [tuple(round(c * 255) for c in colorsys.hsv_to_rgb(hue, hsv[1], hsv[2])) for hue in tetradic_hues]
    return tetradic_colors

def get_monochromatic_colors(rgb):
    hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    monochromatic_colors = []
    for value in [0.8, 0.9, 1.0, 1.1, 1.2]:
        monochromatic_rgb = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(hsv[0], hsv[1], min(max(value, 0), 1)))
        monochromatic_colors.append(monochromatic_rgb)
    return monochromatic_colors

def predict(name):
    name = name.lower()
    tokenized = t.texts_to_sequences([name])
    padded = tf.keras.preprocessing.sequence.pad_sequences(tokenized, maxlen=maxlen)
    one_hot = tf.keras.utils.to_categorical(padded, num_classes=num_classes)
    pred = model.predict(np.array(one_hot))[0]
    r, g, b = scale(pred[0]), scale(pred[1]), scale(pred[2])

    colors = {
        "original": (r, g, b),
        "complementary": get_complementary_color((r, g, b)),
        "analogous": get_analogous_colors((r, g, b)),
        "triadic": get_triadic_colors((r, g, b)),
        "tetradic": get_tetradic_colors((r, g, b)),
        "monochromatic": get_monochromatic_colors((r, g, b))
    }
    return colors

def rgb_from_hex(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_palette_from_rgb(rgb):
    colors = {
        "original": rgb,
        "complementary": get_complementary_color(rgb),
        "analogous": get_analogous_colors(rgb),
        "triadic": get_triadic_colors(rgb),
        "tetradic": get_tetradic_colors(rgb),
        "monochromatic": get_monochromatic_colors(rgb)
    }
    return colors

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_color():
    try:
        if request.is_json:
            data = request.get_json()
            name = data['name']
        else:
            data = request.form
            name = data['name']
        
        colors = predict(name)
        return jsonify(colors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/color_palette', methods=['POST'])
def color_palette():
    try:
        if request.is_json:
            data = request.get_json()
            color_value = data['color_value']
        else:
            data = request.form
            color_value = data['color_value']
            
        if color_value.startswith('#'):
            rgb = rgb_from_hex(color_value)
        else:
            rgb = tuple(map(int, color_value.split(',')))
        colors = generate_palette_from_rgb(rgb)
        return jsonify(colors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
