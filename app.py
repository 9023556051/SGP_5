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


# Chatbot Q&A
CHATBOT_QA = [
    {
        "question": "What is PCOS?",
        "answer": "PCOS (Polycystic Ovary Syndrome) is an endocrine disorder that affects women of reproductive age. It is characterized by irregular menstrual cycles, elevated androgens (male hormones), and polycystic ovaries. Women with PCOS may experience weight gain, hirsutism (excess hair growth), acne, and fertility issues."
    },
    {
        "question": "What are the symptoms of PCOS?",
        "answer": "Common PCOS symptoms include: irregular or absent periods, heavy bleeding, weight gain, difficulty losing weight, excess hair growth (hirsutism), acne, male-pattern baldness, dark patches of skin (acanthosis nigricans), and difficulty getting pregnant."
    },
    {
        "question": "What causes PCOS?",
        "answer": "The exact cause of PCOS is unknown, but it is believed to involve a combination of genetic and environmental factors. Insulin resistance, chronic inflammation, and hormonal imbalances are thought to play a role in the development of PCOS."
    },
    {
        "question": "How is PCOS diagnosed?",
        "answer": "PCOS is typically diagnosed using the Rotterdam criteria, which require two of three features: irregular ovulation/periods, clinical or biochemical signs of elevated androgens, and polycystic ovaries on ultrasound. Blood tests for hormone levels (FSH, LH, testosterone) and imaging are commonly used."
    },
    {
        "question": "What are hormone levels in PCOS?",
        "answer": "In PCOS, typical hormone abnormalities include: elevated LH (Luteinizing Hormone), low or normal FSH, elevated testosterone or free androgen index, elevated AMH (Anti-Müllerian Hormone), and sometimes elevated prolactin or TSH. The FSH:LH ratio is often >3:1 or inverted."
    },
    {
        "question": "Can PCOS be cured?",
        "answer": "PCOS cannot be cured, but it can be managed effectively through lifestyle changes (diet, exercise, weight loss), medications (birth control, metformin), and monitoring. Early diagnosis and management can help reduce symptoms and prevent long-term complications."
    },
    {
        "question": "What lifestyle changes help PCOS?",
        "answer": "Effective lifestyle modifications include: maintaining a healthy weight, eating a balanced diet rich in fiber and low in processed foods, regular physical exercise (150+ min/week), stress management, adequate sleep (7-9 hours), and avoiding smoking and excess alcohol."
    },
    {
        "question": "Can I get pregnant with PCOS?",
        "answer": "Yes, many women with PCOS can conceive with proper treatment. Options include weight loss, ovulation-inducing medications (like clomiphene), insulin-sensitizing agents (metformin), and in some cases, assisted reproductive techniques like IVF. Early intervention and specialist consultation are important."
    },
    {
        "question": "What is the FSH:LH ratio?",
        "answer": "The FSH:LH ratio is used to help diagnose PCOS. Normal ratio is typically 1:1 to 1:3. In PCOS, the ratio is often inverted (higher LH than FSH), commonly 3:1 or greater. This indicates an imbalance in hormones regulating ovulation."
    },
    {
        "question": "What is AMH and why is it elevated in PCOS?",
        "answer": "AMH (Anti-Müllerian Hormone) is produced by ovarian follicles. In PCOS, AMH levels are typically elevated (>48 pmol/L) because there are many immature follicles present. High AMH correlates with polycystic ovaries and can indicate reduced ovulation."
    },
    {
        "question": "What is vitamin D deficiency and PCOS?",
        "answer": "Studies show 67-85% of PCOS patients have vitamin D deficiency (<20 ng/ml). Low vitamin D is associated with insulin resistance, irregular cycles, and reduced fertility. Supplementing vitamin D (1000-4000 IU daily) may help improve PCOS symptoms and metabolic function."
    },
    {
        "question": "What is the best diet for PCOS?",
        "answer": "A PCOS-friendly diet typically includes: high-fiber foods, lean proteins, healthy fats, low glycemic index (GI) carbs, and whole grains. Avoid refined sugars, processed foods, and excess saturated fats. Anti-inflammatory foods and balanced macronutrients help manage insulin resistance."
    },
    {
        "question": "How often should I exercise with PCOS?",
        "answer": "The WHO recommends 150 minutes of moderate-intensity aerobic exercise or 75 minutes of vigorous exercise weekly for adults. Additionally, resistance training 2-3 times per week helps improve insulin sensitivity and supports weight management in PCOS patients."
    },
    {
        "question": "When should I see a doctor for PCOS?",
        "answer": "Consult a healthcare provider if you experience irregular periods, unexplained weight gain, excess hair growth, acne, or fertility problems. A gynecologist or endocrinologist can perform diagnostic tests and recommend a personalized treatment plan. Early diagnosis improves outcomes."
    },
    {
        "question": "What is insulin resistance and PCOS?",
        "answer": "30-40% of PCOS patients have insulin resistance, where cells don't respond properly to insulin. This leads to elevated blood sugar and increased insulin production, which can worsen PCOS symptoms. Managing insulin resistance through diet and exercise is crucial for PCOS management."
    }
]


@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    from flask import jsonify
    user_question = request.json.get('question', '').strip().lower()
    
    # Simple keyword matching
    best_match = None
    max_score = 0
    
    for qa in CHATBOT_QA:
        # Check for keyword overlap
        q_words = set(user_question.split())
        qa_words = set(qa['question'].lower().split())
        score = len(q_words & qa_words)
        if score > max_score:
            max_score = score
            best_match = qa
    
    # If no match or very low score, return default
    if best_match is None or max_score < 1:
        response = "I'm not sure about that. Try asking about PCOS symptoms, diagnosis, treatment, lifestyle changes, or specific hormones (FSH, LH, AMH, etc.)."
    else:
        response = best_match['answer']
    
    return jsonify({'answer': response})


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