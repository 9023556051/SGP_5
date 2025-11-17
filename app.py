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

    # Header
    clinic_name = "Sunrise Women's Health Clinic"
    pdf2.setFillColor(colors.HexColor('#2b5aa6'))
    pdf2.setFont("Helvetica-Bold", 18)
    pdf2.drawString(40, height - 50, clinic_name)
    pdf2.setFont("Helvetica", 10)
    pdf2.setFillColor(colors.black)
    pdf2.drawString(40, height - 66, "Comprehensive Gynecology & Endocrinology Services")
    pdf2.line(40, height - 74, width - 40, height - 74)

    # Report title and date
    pdf2.setFont("Helvetica-Bold", 16)
    pdf2.setFillColor(colors.HexColor('#764ba2'))
    pdf2.drawCentredString(width / 2, height - 96, "Medical Consultation Report")
    pdf2.setFont("Helvetica", 9)
    pdf2.setFillColor(colors.black)
    pdf2.drawRightString(width - 40, height - 96, f"Date: {datetime.datetime.now().strftime('%d %b %Y')}")

    # Patient info box
    box_y = height - 130
    pdf2.roundRect(40, box_y - 70, width - 80, 70, 6, stroke=1, fill=0)
    pdf2.setFont("Helvetica-Bold", 11)
    pdf2.drawString(50, box_y - 20, f"Patient: {input_values.get('Full Name', 'N/A')}")
    pdf2.setFont("Helvetica", 10)
    pdf2.drawString(50, box_y - 36, f"Age: {input_values.get('Age', 'N/A')}   |   Phone: {input_values.get('Phone', 'N/A')}")
    pdf2.drawRightString(width - 50, box_y - 20, f"Email: {input_values.get('Email', 'N/A')}")

    # Assessment header
    y = box_y - 90
    pdf2.setFont("Helvetica-Bold", 12)
    pdf2.setFillColor(colors.HexColor('#2b5aa6'))
    pdf2.drawString(40, y, "Clinical Assessment")
    y -= 16
    pdf2.setFont("Helvetica", 10)
    pdf2.setFillColor(colors.black)
    pdf2.drawString(50, y, "The patient presented for PCOS risk assessment. Clinical parameters and lab values are documented below.")
    y -= 22

    # Lab values / Inputs table (two columns)
    pdf2.setFont("Helvetica-Bold", 11)
    pdf2.setFillColor(colors.HexColor('#667eea'))
    pdf2.drawString(40, y, "Measured Parameters")
    y -= 14
    pdf2.setFont("Helvetica", 10)
    pdf2.setFillColor(colors.black)

    labels = [
        ("Weight (kg)", 'Weight'), ("Height (cm)", 'Height'), ("BMI", 'BMI'), ("Pulse Rate (bpm)", 'PulseRate'),
        ("Respiration Rate", 'RR'), ("Systolic BP", 'BP_systolic'), ("Diastolic BP", 'BP_diastolic'),
        ("Follicle Count", 'Follicle_count'), ("FSH (mlU/ml)", 'FSH'), ("LH (mlU/ml)", 'LH'),
        ("FSH:LH Ratio", 'FSH_LH_ratio'), ("TSH (μIU/ml)", 'TSH'), ("AMH (pmol/L)", 'AMH'),
        ("PRL (ng/ml)", 'PRL'), ("Vitamin D3 (ng/ml)", 'VitD3'), ("Progesterone (ng/ml)", 'PRG'),
        ("Waist:Hip Ratio", 'W_H_ratio'), ("Random Blood Sugar (mg/dl)", 'RBS')
    ]

    col_x = 50
    col2_x = width / 2 + 10
    row_h = 14
    for i, (label_text, key) in enumerate(labels):
        if y < 120:
            pdf2.showPage()
            y = height - 80
            pdf2.setFont("Helvetica", 10)
        x = col_x if i % 2 == 0 else col2_x
        val = input_values.get(label_text) or input_values.get(key) or 'N/A'
        pdf2.drawString(x, y, f"{label_text}: ")
        pdf2.drawRightString(x + 120, y, f"{val}")
        if i % 2 == 1:
            y -= row_h

    # Space before diagnosis
    y -= 18
    pdf2.setFont("Helvetica-Bold", 12)
    pdf2.setFillColor(colors.HexColor('#cc2b2b') if result == 'PCOS Positive' else colors.HexColor('#2b8f3e'))
    pdf2.drawString(40, y, "Diagnosis")
    y -= 16
    pdf2.setFont("Helvetica", 11)
    pdf2.setFillColor(colors.black)
    pdf2.drawString(50, y, f"Result: {result}")
    y -= 18

    # Tailored advice/prescription
    pdf2.setFont("Helvetica-Bold", 12)
    pdf2.setFillColor(colors.HexColor('#2b5aa6'))
    pdf2.drawString(40, y, "Recommendations")
    y -= 14
    pdf2.setFont("Helvetica", 10)
    pdf2.setFillColor(colors.black)
    if result == "PCOS Positive":
        adv = [
            "Refer to specialist (Gynecologist/Endocrinologist)",
            "Lifestyle modification: diet, exercise, weight management",
            "Consider hormonal evaluation & tailored treatment plan",
            "Monitor blood glucose and lipid profile"
        ]
    else:
        adv = [
            "Maintain healthy lifestyle and routine follow-up",
            "Repeat evaluation if symptoms persist",
            "Routine screening for metabolic risk factors"
        ]
    for line in adv:
        pdf2.drawString(50, y, f"- {line}")
        y -= 14

    # Signature
    if y < 140:
        pdf2.showPage()
        y = height - 80
    y -= 10
    pdf2.drawString(50, y, "-------------------------------------")
    pdf2.drawString(60, y - 14, "Dr. Olivia Greene")
    pdf2.drawString(60, y - 28, "MBBS, DGO - Consultant Gynecologist")

    pdf2.showPage()
    pdf2.save()
    buffer2.seek(0)
    return send_file(buffer2, as_attachment=True, download_name="Medical_Report.pdf", mimetype="application/pdf")


@app.route('/medical_report_preview')
def medical_report_preview():
    input_values = session.get('input_values')
    result = session.get('prediction_result')
    if not input_values or not result:
        flash('No medical report available. Please generate a prediction first.', 'error')
        return redirect(url_for('home'))
    now = datetime.datetime.now().strftime('%d %b %Y')
    return render_template('medical_report.html', input_values=input_values, result=result, now=now)


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