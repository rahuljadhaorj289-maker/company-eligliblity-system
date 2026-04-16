from flask import Flask, render_template, request, redirect
import json
import os
import random
import string

app = Flask(__name__)

FILE_NAME = "data.json"

# ---------- LOAD ----------
def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return {}

# ---------- SAVE ----------
def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

# ---------- KEY ----------
def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- COMPANY ----------
@app.route("/company", methods=["GET", "POST"])
def company():
    if request.method == "POST":
        db = load_data()

        company = {}
        company["10th"] = float(request.form["tenth"])
        company["12th"] = float(request.form["twelfth"])
        company["grad"] = float(request.form["grad"])
        company["backlogs"] = int(request.form["backlogs"])

        questions = []
        n = int(request.form["num"])

        for i in range(1, n+1):
            q = request.form[f"q{i}"]
            ans = request.form[f"a{i}"].lower()
            marks = int(request.form[f"m{i}"])

            questions.append({
                "question": q,
                "correct": ans,
                "marks": marks
            })

        company["questions"] = questions

        key = generate_key()
        db[key] = company
        save_data(db)

        return f"✅ Company Created! Share Key: {key}"

    return render_template("company.html")

# ---------- ENTER KEY ----------
@app.route("/candidate", methods=["GET", "POST"])
def candidate():
    if request.method == "POST":
        key = request.form["key"].upper()
        db = load_data()

        if key not in db:
            return "❌ Invalid Key"

        company = db[key]
        return render_template("candidate_form.html", company=company, key=key)

    return render_template("enter_key.html")

# ---------- SUBMIT ----------
@app.route("/submit", methods=["POST"])
def submit():
    db = load_data()
    key = request.form["key"]
    company = db[key]

    name = request.form["name"]
    tenth = float(request.form["tenth"])
    twelfth = float(request.form["twelfth"])
    grad = float(request.form["grad"])
    backlogs = int(request.form["backlogs"])

    academic_avg = (tenth + twelfth + grad) / 3

    score = 0
    total = 0

    for i, q in enumerate(company["questions"], start=1):
        ans = request.form.get(f"ans{i}", "").lower()
        if ans == q["correct"]:
            score += q["marks"]
        total += q["marks"]

    test_score = (score / total) * 100 if total else 0

    eligible = True
    if (tenth < company["10th"] or
        twelfth < company["12th"] or
        grad < company["grad"] or
        backlogs > company["backlogs"]):
        eligible = False

    final_score = (0.4 * academic_avg) + (0.6 * test_score)

    return render_template("result.html",
                           name=name,
                           academic=round(academic_avg,2),
                           test=round(test_score,2),
                           final=round(final_score,2),
                           status="Eligible ✅" if eligible and test_score>=60 else "Not Eligible ❌")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
