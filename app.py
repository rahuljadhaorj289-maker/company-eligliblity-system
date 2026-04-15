from flask import Flask, render_template, request
import random, string, json, os

app = Flask(__name__)
FILE_NAME = "data.json"

# ---------- LOAD ----------
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as f:
                return json.load(f)
        except:
            return {}
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
    return render_template("home.html")

# ---------- COMPANY ----------
@app.route("/company", methods=["GET", "POST"])
def company():
    if request.method == "POST":
        database = load_data()

        company = {
            "10th": float(request.form["tenth"]),
            "12th": float(request.form["twelfth"]),
            "grad": float(request.form["grad"]),
            "backlogs": int(request.form["backlogs"]),
            "questions": []
        }

        for i in range(1, 4):
            company["questions"].append({
                "question": request.form[f"q{i}"],
                "correct": request.form[f"a{i}"].lower(),
                "marks": int(request.form[f"m{i}"])
            })

        key = generate_key()
        database[key] = company
        save_data(database)

        return f"✅ Company Created! Your Key: {key}"

    return render_template("company.html")

# ---------- CANDIDATE ----------
@app.route("/candidate", methods=["GET", "POST"])
def candidate():
    if request.method == "POST":
        database = load_data()
        key = request.form["key"].upper()

        if key not in database:
            return "❌ Invalid Key"

        company = database[key]

        name = request.form["name"]
        tenth = float(request.form["tenth"])
        twelfth = float(request.form["twelfth"])
        grad = float(request.form["grad"])
        backlogs = int(request.form["backlogs"])

        academic_avg = (tenth + twelfth + grad) / 3

        score = 0
        total = 0

        for i, q in enumerate(company["questions"], start=1):
            ans = request.form[f"ans{i}"].lower()
            if ans == q["correct"]:
                score += q["marks"]
            total += q["marks"]

        test_score = (score / total) * 100 if total > 0 else 0

        eligible = not (
            tenth < company["10th"] or
            twelfth < company["12th"] or
            grad < company["grad"] or
            backlogs > company["backlogs"]
        )

        final_score = (0.4 * academic_avg) + (0.6 * test_score)

        return render_template("result.html",
                               name=name,
                               academic=round(academic_avg, 2),
                               test=round(test_score, 2),
                               final=round(final_score, 2),
                               status="Eligible ✅" if eligible and test_score >= 60 else "Not Eligible ❌")

    return render_template("candidate.html")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
