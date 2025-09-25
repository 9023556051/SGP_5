from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
import pickle
import numpy as np
import os
import io
import base64
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = 'your-very-secret-key'  # Use a fixed string in production

# Load model
try:
    model = pickle.load(open('model.pkl', 'rb'))
except FileNotFoundError:
    print("Warning: model.pkl not found. Please ensure the model file is present.")
    model = None


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route('/download_report')
def download_report():
    input_values = session.get('input_values')
    result = session.get('prediction_result')
    if not input_values or not result:
        flash('No report available. Please generate a prediction first.', 'error')
        return redirect(url_for('home'))
    buffer = io.BytesIO()
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    import datetime
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(colors.HexColor("#667eea"))
    pdf.drawCentredString(width / 2, height - 60, "PCOS Prediction Report")
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, height - 90, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y = height - 120
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Patient Input Details:")
    y -= 20
    pdf.setFont("Helvetica", 11)
    row_height = 16
    for label, value in input_values.items():
        if y < 80:
            pdf.showPage()
            y = height - 60
            pdf.setFont("Helvetica", 11)
        pdf.drawString(50, y, f"{label}: {value}")
        y -= row_height
    y -= 10
    pdf.setFont("Helvetica-Bold", 13)
    pdf.setFillColor(colors.HexColor("#764ba2"))
    pdf.drawString(40, y, "Prediction Result:")
    pdf.setFillColor(colors.black)
    y -= 20
    pdf.drawString(60, y, result)
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="PCOS_Report.pdf", mimetype="application/pdf")


@app.route('/download_medical_report')
def download_medical_report():
    input_values = session.get('input_values')
    result = session.get('prediction_result')
    if not input_values or not result:
        flash('No medical report available. Please generate a prediction first.', 'error')
        return redirect(url_for('home'))
    buffer2 = io.BytesIO()
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    import datetime
    pdf2 = canvas.Canvas(buffer2, pagesize=A4)
    width, height = A4
    pdf2.setFont("Helvetica-Bold", 20)
    pdf2.drawCentredString(width / 2, height - 60, "MEDICAL REPORT")
    y = height - 100
    pdf2.setFont("Helvetica-Bold", 12)
    pdf2.drawString(40, y, "Visit Info")
    y -= 20
    pdf2.setFont("Helvetica", 11)
    pdf2.drawString(60, y, "Doctor: Dr. Olivia Greene")
    pdf2.drawRightString(width - 60, y, f"Visit Date: {datetime.datetime.now().strftime('%d.%m.%Y')}")
    y -= 16
    pdf2.drawString(60, y, "Specialization: Gynecology")
    y -= 30
    pdf2.setFont("Helvetica-Bold", 12)
    pdf2.drawString(40, y, "Patient Info")
    y -= 20
    pdf2.setFont("Helvetica", 11)
    pdf2.drawString(60, y, f"Full Name: {input_values.get('Full Name')}")
    pdf2.drawRightString(width - 60, y, f"Age: {input_values.get('Age')} yrs")
    y -= 16
    pdf2.drawString(60, y, f"Phone: {input_values.get('Phone')}")
    pdf2.drawRightString(width - 60, y, f"Email: {input_values.get('Email')}")
    y -= 30
    pdf2.setFont("Helvetica-Bold", 12)
    pdf2.setFillColor(colors.green)
    pdf2.drawString(40, y, "Assessment")
    y -= 20
    pdf2.setFont("Helvetica", 11)
    pdf2.setFillColor(colors.black)
    pdf2.drawString(60, y, "Patient presented with symptoms and test values.")
    y -= 16
    pdf2.drawString(60, y, "Based on the prediction, results are as follows:")
    y -= 30
    pdf2.setFont("Helvetica-Bold", 12)
    pdf2.setFillColor(colors.green)
    pdf2.drawString(40, y, "Diagnosis")
    y -= 20
    pdf2.setFont("Helvetica", 11)
    pdf2.setFillColor(colors.black)
    pdf2.drawString(60, y, f"Prediction Result: {result}")
    y -= 30
    pdf2.setFont("Helvetica-Bold", 12)
    pdf2.setFillColor(colors.green)
    pdf2.drawString(40, y, "Prescription")
    y -= 20
    pdf2.setFont("Helvetica", 11)
    pdf2.setFillColor(colors.black)
    if result == "PCOS Positive":
        pdf2.drawString(60, y, "Signs of PCOS detected. Consult a gynecologist.")
        y -= 16
        pdf2.drawString(60, y, "Recommended: exercise, balanced diet, stress management.")
    else:
        pdf2.drawString(60, y, "No significant signs of PCOS detected.")
        y -= 16
        pdf2.drawString(60, y, "Maintain healthy lifestyle and regular checkups.")
    pdf2.showPage()
    pdf2.save()
    buffer2.seek(0)
    return send_file(buffer2, as_attachment=True, download_name="Medical_Report.pdf", mimetype="application/pdf")


@app.route("/<name>")
def rande(name):
    return redirect(url_for('about'))


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extended input fields
        input_fields = [
            ("Full Name", "FullName"),
            ("Email", "Email"),
            ("Phone", "Phone"),
            ("Age", "Age"),
            ("Weight (kg)", "Weight"),
            ("Height (cm)", "Height"),
            ("BMI", "BMI"),
            ("Pulse Rate (bpm)", "PulseRate"),
            ("Respiration Rate", "RR"),
            ("Systolic BP (mmHg)", "BP_systolic"),
            ("Diastolic BP (mmHg)", "BP_diastolic"),
            ("Irregular Periods", "Cycle(R/I)"),
            ("Ever Been Pregnant", "Pregnant"),
            ("Number of Abortions", "No. of Abortions"),
            ("Follicle Count", "Follicle_count"),
            ("FSH (mlU/ml)", "FSH"),
            ("LH (mlU/ml)", "LH"),
            ("FSH:LH Ratio", "FSH_LH_ratio"),
            ("TSH (μIU/ml)", "TSH"),
            ("AMH (pmol/L)", "AMH"),
            ("PRL (ng/ml)", "PRL"),
            ("Vitamin D3 (ng/ml)", "VitD3"),
            ("Progesterone (ng/ml)", "PRG"),
            ("Waist:Hip Ratio", "W_H_ratio"),
            ("Random Blood Sugar (mg/dl)", "RBS"),
            ("Weight Gain", "Weight_gain"),
            ("Abnormal Hair Growth", "hair_growth"),
            ("Skin Darkening", "Skin_darkening"),
            ("Hair Loss", "Hair_loss"),
            ("Increased Pimples", "Pimples"),
            ("Fast Food Consumption", "Fast_food"),
            ("Regular Exercise", "Reg_exercise"),
        ]


        features = []
        input_values = {}
        for label, key in input_fields:
            value = request.form.get(key)
            if label in ["Full Name", "Email", "Phone"]:
                input_values[label] = value
            else:
                value = float(value)
                features.append(value)
                input_values[label] = value

        prediction = model.predict([features])
        result = "PCOS Positive" if prediction[0] == 1 else "PCOS Negative"

        # Store only input values and result in session
        session['input_values'] = input_values
        session['prediction_result'] = result

        return render_template('index.html', prediction_text=result)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('index.html')


if __name__ == "__main__":
    if model is None:
        print("Error: Cannot start app without model.pkl")
        exit(1)

    app.run(debug=True, host='0.0.0.0', port=5000)