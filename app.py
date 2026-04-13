from flask import Flask, request, render_template
import pickle
import numpy as np

app = Flask(__name__)

model = pickle.load(open("model.pkl", "rb"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    distance = float(request.form["distance"])
    prep_time = float(request.form["prep_time"])
    traffic = int(request.form["traffic"])

    input_data = np.array([[distance, prep_time, traffic]])
    prediction = model.predict(input_data)

    return render_template("index.html", prediction=round(prediction[0], 2))

if __name__ == "__main__":
    app.run(debug=True)