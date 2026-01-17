from flask import Flask, render_template, request, redirect, session, flash

import numpy as np
from urllib.parse import urlparse, parse_qs
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify

import time
from flask import Flask, render_template, flash, redirect, url_for, session, request

# app = Flask(__name__)
# app.secret_key = 'xyzsdfg'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
# Track the number of prediction attempts within a time period
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)



prediction_attempts = {}

# User Login Route
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')


# User Login Route


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            session['user_id'] = user.id
            return redirect(url_for('user_dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('user/user-login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match.', 'danger')

    return render_template('user/user-registration.html')

@app.route('/logout/')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Admin login successful!', 'success')
            return redirect('/admin-dashboard')
        else:
            flash('Invalid username or password', 'danger')
    return render_template('admin/admin-login.html')

# Admin Registration Route


# Admin Registration
@app.route('/admin-registration', methods=['GET', 'POST'])
def admin_registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        admin = Admin(username=username, password=hashed_password)
        db.session.add(admin)
        db.session.commit()
        flash('Admin registered successfully!', 'success')
        return redirect(url_for('admin_login'))
    return render_template('admin/admin-registration.html')

# User Dashboard Route
@app.route('/user-dashboard')
def user_dashboard():
  
        return render_template('user/user-dashboard.html')
    

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_id' in session:
        admin_username = session['admin_username']

        # Query counts using SQLAlchemy
        num_students = User.query.count()
        num_admins = Admin.query.count()
       

        return render_template(
            'admin/admin-dashboard.html',
            admin_username=admin_username,
            num_students=num_students,
            num_admins=num_admins,
            
        )
    else:
        return redirect('/admin-login')

# Show Users Route
@app.route('/show_users')
def show_users():
    if 'admin_id' in session:
        admin_username = session.get('admin_username')
        users = User.query.all()  # Assuming you are using SQLAlchemy and User model is imported
        return render_template('admin/show_users.html', admin_username=admin_username, users=users)
    else:
        return redirect('/admin-login')



# Edit User Route
@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'admin_id' in session:
        admin_username = session['admin_username']
        user = User.query.get_or_404(user_id)

        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('show_users'))

        return render_template('admin/edit_user.html', admin_username=admin_username, user=user)
    else:
        return redirect('/admin-login')


# Delete User Route
@app.route('/admin/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if 'admin_id' in session:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'info')
        return redirect(url_for('show_users'))
    else:
        return redirect('/admin-login')

# User Dashboard Route
@app.route('/prediction')
def prediction():
   
        # Add your logic here for the user dashboard

        return render_template('user/predict.html')

# ---------------------------------------------------------------------


from urllib.parse import urlencode


# Dictionary mapping predicted labels to lists of YouTube video recommendations
video_recommendations = {
    'Database Developer': [
        
        'https://www.youtube.com/watch?v=xyHDJ8khhvA',
        'https://www.youtube.com/watch?v=UOJZTqA5Loc',
        'https://www.youtube.com/watch?v=BdSoLXmMoGA'
    ],
    
    'Applications Developer': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'CRM Technical Developer': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'Mobile Applications Developer': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'Network Security Engineer': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'Software Developer': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'Software Engineer': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'Software Quality Assurance (QA) / Testing': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'Systems Security Administrator': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'Technical Support': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'UX Designer': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    'Web Developer': [
        'https://www.youtube.com/watch?v=data_science_video_link1',
        'https://www.youtube.com/watch?v=data_science_video_link2',
        'https://www.youtube.com/watch?v=data_science_video_link3'
    ],
    
}







import pickle

with open('model/weights.pkl', 'rb') as file:
    clf = pickle.load(file)



# ------------------------------------------start*-------------------------------------

# @app.route('/user_prediction', methods=['GET', 'POST'])
# def user_prediction():
#     if request.method == 'POST':
#         # Check if the user has made too many prediction attempts within the time period
#         user_id = session.get('user_id')
#         if user_id in prediction_attempts:
#             attempts, last_attempt_time = prediction_attempts[user_id]
#             elapsed_time = time.time() - last_attempt_time
#             if attempts >= 3 and elapsed_time < 600:
#                 session.clear()
#                 flash("You have made too many prediction attempts. Please try again later.")
#                 return render_template('loss.html')
                

#         # Update the prediction attempts for the user
#         if user_id in prediction_attempts:
#             attempts, last_attempt_time = prediction_attempts[user_id]
#             prediction_attempts[user_id] = (attempts + 1, time.time())
#         else:
#             prediction_attempts[user_id] = (1, time.time())

#         # Perform the prediction logic
#         Logical_quotient_rating = float(request.form['Logical_quotient_rating']) 
#         coding_skills_rating = float(request.form['coding_skills_rating']) 
#         hackathons = float(request.form['hackathons']) 
#         public_speaking_points = float(request.form['public_speaking_points']) 
#         self_learning_capability = float(request.form['self_learning_capability']) 
#         Extra_courses_did = float(request.form['Extra_courses_did'])  
#         Taken_inputs_from_seniors_or_elders = float(request.form['Taken_inputs_from_seniors_or_elders'])  
#         worked_in_teams_ever = float(request.form['worked_in_teams_ever']) 
#         Introvert = float(request.form['Introvert'])   
#         reading_and_writing_skills = float(request.form['reading_and_writing_skills'])  
#         memory_capability_score = float(request.form['memory_capability_score'])   

#         A_Management = float(request.form['A_Management'])
#         A_Technical = float(request.form['A_Technical'])
#         B_hard_worker = float(request.form['B_hard_worker'])
#         B_smart_worker = float(request.form['B_smart_worker'])

#         Interested_subjects = float(request.form['Interested_subjects'])    
#         Interested_Type_of_Books = float(request.form['Interested_Type_of_Books'])  
#         certifications = float(request.form['certifications']) 
#         workshops = float(request.form['workshops'])  
#         Type_of_company_want_to_settle_in = float(request.form['Type_of_company_want_to_settle_in'])   
#         interested_career_area = float(request.form['interested_career_area']) 
    
#         # Create a numpy array with the user input
#         pred = [A_Management, A_Technical, B_hard_worker, B_smart_worker,    Logical_quotient_rating, coding_skills_rating, hackathons, public_speaking_points, self_learning_capability, Extra_courses_did, Taken_inputs_from_seniors_or_elders,
#                     worked_in_teams_ever, Introvert, reading_and_writing_skills, memory_capability_score, Interested_subjects,
#                     # worked_in_teams_ever, Introvert, reading_and_writing_skills, memory_capability_score, smart_or_hard_work, Management_or_Techinical, Interested_subjects,
#                     Interested_Type_of_Books, certifications, workshops, Type_of_company_want_to_settle_in, interested_career_area]
        
#         userdata = np.array(pred).reshape(1, -1)
#         # ... rest of the code ...

#         # Make the prediction
#         prediction = clf.predict(userdata)
#         classprobs = clf.predict_proba(userdata)
#         predclassprob = np.max(classprobs)

#         # Get the login username
#         username = session.get('username')

#         # Get the recommended video links based on the prediction 
#         recommended_video_links = video_recommendations.get(prediction[0], [])
    
#         # Create the YouTube video IDs for each recommended video
#         youtube_video_ids = []
#         for video_link in recommended_video_links[:3]:
#             video_id = get_video_id(video_link)
#             if video_id:
#                 youtube_video_ids.append(video_id)

#         return render_template('user/result.html', prediction=prediction, classprobs=classprobs,
#                                predclassprob=predclassprob, username=username, youtube_video_ids=youtube_video_ids)

#     return render_template('user_prediction.html')

# -----------------------end*---------------------------------



@app.route('/career/page1', methods=['GET', 'POST'])
def career_page1():
    if request.method == 'POST':
        # Check if the user has made too many prediction attempts within the time period
        user_id = session.get('user_id')
        if user_id in prediction_attempts:
            attempts, last_attempt_time = prediction_attempts[user_id]
            elapsed_time = time.time() - last_attempt_time
            if attempts >= 3 and elapsed_time < 600:
                session.clear()
                flash("You have made too many prediction attempts. Please try again later.")
                return render_template('loss.html')
                

        # Update the prediction attempts for the user
        if user_id in prediction_attempts:
            attempts, last_attempt_time = prediction_attempts[user_id]
            prediction_attempts[user_id] = (attempts + 1, time.time())
        else:
            prediction_attempts[user_id] = (1, time.time())
            
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

from flask import Flask, render_template, session
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

@app.route('/career/result')
def career_result():
    user_data = session.get('user_data', [])
    if not user_data or len(user_data) != 21:
        return "Insufficient data. Please complete the form."

    userdata_np = np.array(user_data).reshape(1, -1)

    prediction = clf.predict(userdata_np)[0]
    classprobs = clf.predict_proba(userdata_np)[0]
    predclassprob = np.max(classprobs)

    username = session.get('username')

    # Get the recommended video links based on the prediction
    recommended_video_links = video_recommendations.get(prediction, [])

    # Create the YouTube video IDs for each recommended video
    youtube_video_ids = []
    for video_link in recommended_video_links[:3]:
        video_id = get_video_id(video_link)
        if video_id:
            youtube_video_ids.append(video_id)

    # Career relationship map
    related_career_recommendations = {
        'Database Developer': ['Data Analyst', 'Database Administrator'],
        'Applications Developer': ['Software Developer', 'Mobile Applications Developer'],
        'CRM Technical Developer': ['ERP Developer', 'Business Intelligence Developer'],
        'Mobile Applications Developer': ['iOS Developer', 'Android Developer'],
        'Network Security Engineer': ['Cybersecurity Analyst', 'Information Security Manager'],
        'Software Developer': ['Full Stack Developer', 'Applications Developer'],
        'Software Engineer': ['DevOps Engineer', 'Machine Learning Engineer'],
        'Software Quality Assurance (QA) / Testing': ['Automation Test Engineer', 'Performance Test Engineer'],
        'Systems Security Administrator': ['Network Administrator', 'IT Security Specialist'],
        'Technical Support': ['Help Desk Technician', 'IT Support Specialist'],
        'UX Designer': ['UI Designer', 'Interaction Designer'],
        'Web Developer': ['Front-End Developer', 'Back-End Developer'],
    }

    def plot_career_graphs(career_name):
        labels = [career_name] + related_career_recommendations.get(career_name, [])
        sizes = [50, 30, 20]

        # Bar Chart
        plt.figure(figsize=(6, 4))
        plt.bar(labels, sizes, color=['blue', 'green', 'orange'])
        plt.title('Career Relevance - Bar Chart')
        plt.ylabel('Percentage')
        bar_chart_io = io.BytesIO()
        plt.tight_layout()
        plt.savefig(bar_chart_io, format='png')
        bar_chart_io.seek(0)
        bar_chart_base64 = base64.b64encode(bar_chart_io.read()).decode()
        plt.close()

        # Pie Chart
        plt.figure(figsize=(6, 4))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['blue', 'green', 'orange'])
        plt.title('Career Relevance - Pie Chart')
        pie_chart_io = io.BytesIO()
        plt.tight_layout()
        plt.savefig(pie_chart_io, format='png')
        pie_chart_io.seek(0)
        pie_chart_base64 = base64.b64encode(pie_chart_io.read()).decode()
        plt.close()

        return bar_chart_base64, pie_chart_base64, labels[1:]  # Return related careers too

    bar_chart, pie_chart, related_careers = plot_career_graphs(prediction)

    return render_template('career/result_new.html',
                           prediction=prediction,
                           classprobs=classprobs,
                           predclassprob=predclassprob,
                           username=username,
                           youtube_video_ids=youtube_video_ids,
                           bar_chart=bar_chart,
                           pie_chart=pie_chart,
                           related_careers=related_careers)



# Function to extract YouTube video ID from the URL
def get_video_id(url):
    video_id = None
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'www.youtube.com':
        query_string = parse_qs(parsed_url.query)
        if 'v' in query_string:
            video_id = query_string['v'][0]
    return video_id

import pandas as pd
# Load questions once
df = pd.read_excel("questions.xlsx")

@app.route('/choose')
def new_home():
    return render_template('new_home.html')

@app.route('/start', methods=['POST'])
def start():
    selected_stream = request.form['stream']
    session['stream'] = selected_stream
    stream_questions = df[df['Stream'] == selected_stream].to_dict(orient='records')
    session['questions'] = stream_questions
    session['index'] = 0
    session['answers'] = []
    return redirect(url_for('question'))

@app.route('/question', methods=['GET', 'POST'])
def question():
    index = session.get('index', 0)
    questions = session.get('questions', [])

    if request.method == 'POST':
        selected = request.form.get('option')
        session['answers'].append(selected)
        session['index'] = index + 1
        index += 1

    if index >= len(questions):
        return redirect(url_for('tenth_result'))

    q = questions[index]
    return render_template('form.html', q=q, index=index + 1, total=len(questions))

@app.route('/10th_result')
def tenth_result():
    answers = session.get('answers', [])
    questions = session.get('questions', [])
    correct_count = 0

    for user_answer, q in zip(answers, questions):
        if user_answer == q['Correct Answer']:
            correct_count += 1

    total = len(questions)
    return f"Quiz complete. You got {correct_count} out of {total} correct!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
