from flask import Flask, render_template, url_for, request
app = Flask(__name__)
 
@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        input_dict = request.form
        print(input_dict)
        return render_template("processed.html")
    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)