from flask import Flask, request, redirect, render_template, session
import numpy as np
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

# Load model once
with open('model/weights.pkl', 'rb') as file:
    clf = pickle.load(file)


@app.route('/career/page1', methods=['GET', 'POST'])
def career_page1():
    if request.method == 'POST':
        session['user_data'] = []
        session['user_data'].append(float(request.form['Logical_quotient_rating']))
        session['user_data'].append(float(request.form['coding_skills_rating']))
        return redirect('/career/page2')
    return render_template('career/1.html')


@app.route('/career/page2', methods=['GET', 'POST'])
def career_page2():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['hackathons']))
        data.append(float(request.form['public_speaking_points']))
        session['user_data'] = data
        return redirect('/career/page3')
    return render_template('career/2.html')


@app.route('/career/page3', methods=['GET', 'POST'])
def career_page3():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['self_learning_capability']))
        data.append(float(request.form['Extra_courses_did']))
        session['user_data'] = data
        return redirect('/career/page4')
    return render_template('career/3.html')


@app.route('/career/page4', methods=['GET', 'POST'])
def career_page4():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['Taken_inputs_from_seniors_or_elders']))
        data.append(float(request.form['worked_in_teams_ever']))
        session['user_data'] = data
        return redirect('/career/page5')
    return render_template('career/4.html')


@app.route('/career/page5', methods=['GET', 'POST'])
def career_page5():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['Introvert']))
        data.append(float(request.form['reading_and_writing_skills']))
        session['user_data'] = data
        return redirect('/career/page6')
    return render_template('career/5.html')


@app.route('/career/page6', methods=['GET', 'POST'])
def career_page6():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['memory_capability_score']))
        data.append(float(request.form['B_smart_worker']))
        session['user_data'] = data
        return redirect('/career/page7')
    return render_template('career/6.html')


@app.route('/career/page7', methods=['GET', 'POST'])
def career_page7():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['B_hard_worker']))
        data.append(float(request.form['A_Management']))
        session['user_data'] = data
        return redirect('/career/page8')
    return render_template('career/7.html')


@app.route('/career/page8', methods=['GET', 'POST'])
def career_page8():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['A_Technical']))
        data.append(float(request.form['Interested_subjects']))
        session['user_data'] = data
        return redirect('/career/page9')
    return render_template('career/8.html')


@app.route('/career/page9', methods=['GET', 'POST'])
def career_page9():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['Interested_Type_of_Books']))
        data.append(float(request.form['certifications']))
        session['user_data'] = data
        return redirect('/career/page10')
    return render_template('career/9.html')


@app.route('/career/page10', methods=['GET', 'POST'])
def career_page10():
    if request.method == 'POST':
        data = session['user_data']
        data.append(float(request.form['workshops']))
        data.append(float(request.form['Type_of_company_want_to_settle_in']))
        data.append(float(request.form['interested_career_area']))
        session['user_data'] = data
        return redirect('/career/result')
    return render_template('career/10.html')


@app.route('/career/result')
def career_result():
    user_data = session.get('user_data', [])
    if not user_data or len(user_data) != 21:
        return "Insufficient data. Please complete the form."

    userdata_np = np.array(user_data).reshape(1, -1)

    prediction = clf.predict(userdata_np)[0]
    classprobs = clf.predict_proba(userdata_np)[0]
    predclassprob = np.max(classprobs)

    return render_template('career/result.html',
                           prediction=prediction,
                           classprobs=classprobs,
                           predclassprob=predclassprob)


if __name__ == '__main__':
    app.run(debug=True)
