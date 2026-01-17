from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import numpy as np
from urllib.parse import urlparse, parse_qs
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'xyzsdfg'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'career_guidance'

mysql = MySQL(app)


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

# -------------------------------------------------------------User Master---------------------------------------------------------
# User Login Route
@app.route('/user-login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/user-dashboard')
        else:
            return render_template('user/user-login.html', error='Invalid username or password')

    return render_template('user/user-login.html')


# User Registration Route
@app.route('/user-registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        mysql.connection.commit()
        cursor.close()

        return redirect('/user-login')

    return render_template('user/user-registration.html')


# ------------------------------------------------------- End User Master ------------------------------------------------------------

# --------------------------------------------------------- Start Admin Master --------------------------------------------------------
# Admin Login Route
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        cursor.close()

        if admin:
            session['admin_id'] = admin[0]
            session['admin_username'] = admin[1]
            return redirect('/admin-dashboard')
        else:
            return render_template('admin/admin-login.html', error='Invalid username or password')

    return render_template('admin/admin-login.html')


# Admin Registration Route
@app.route('/admin-registration', methods=['GET', 'POST'])
def admin_registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cursor.close()

        return redirect('/admin-login')

    return render_template('admin/admin-registration.html')

# User Dashboard Route
@app.route('/user-dashboard')
def user_dashboard():
    if 'user_id' in session:
        # User is logged in
        user_id = session['user_id']
        username = session['username']

        # Add your logic here for the user dashboard

        return render_template('user/user-dashboard.html', username=username)
    else:
        return redirect('/user-login')


# Admin Dashboard Route
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_id' in session:
        # Admin is logged in
        admin_id = session['admin_id']
        admin_username = session['admin_username']

        # Retrieve the number of students from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        num_students = cursor.fetchone()[0]
        cursor.close()

        # Retrieve the number of students from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM admins")
        num_admins = cursor.fetchone()[0]
        cursor.close()

        # Retreve the number of Prediction from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM predictions")
        num_predictions = cursor.fetchone()[0]
        cursor.close()

        return render_template('admin/admin-dashboard.html', admin_username=admin_username, num_students=num_students, num_admins=num_admins, num_predictions=num_predictions)
    else:
        return redirect('/admin-login')


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



# Show Users Route
@app.route('/show_users')
def show_users():
    if 'admin_id' in session:
        # Admin is logged in
        admin_id = session['admin_id']
        admin_username = session['admin_username']

        # Retrieve the users' data from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()

        # Debug print statement
        print(users)

        # Pass the users' data to the template for rendering
        return render_template('admin/show_users.html', admin_username=admin_username, users=users)

    else:
        return redirect('/admin-login')


# Edit User Route
@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'admin_id' in session:
        # Admin is logged in
        admin_id = session['admin_id']
        admin_username = session['admin_username']

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']

            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", (username, email, user_id))
            mysql.connection.commit()
            cursor.close()

            return redirect('/show_users')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('admin/edit_user.html', admin_username=admin_username, user=user)
        else:
            return redirect('/show_users')

    else:
        return redirect('/admin-login')


# Delete User Route
@app.route('/admin/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if 'admin_id' in session:
        # Admin is logged in
        admin_id = session['admin_id']
        admin_username = session['admin_username']

        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cursor.close()

        return redirect('/show_users')

    else:
        return redirect('/admin-login')
    


# User Dashboard Route
@app.route('/prediction')
def prediction():
    if 'user_id' in session:
        # User is logged in
        user_id = session['user_id']
        username = session['username']


        return render_template('user/predict.html', username=username)
    else:
        return redirect('/user-login')
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
        'https://www.youtube.com/watch?v=HoXXLklimaA',
        'https://www.youtube.com/watch?v=VElN1eH2AfA',
        'https://www.youtube.com/watch?v=KNP0xepP3CE'
    ],
    'CRM Technical Developer': [
        'https://www.youtube.com/watch?v=sQD7kaZ5h0s',
        'https://www.youtube.com/watch?v=zu_rBFlMTeY',
        'https://www.youtube.com/watch?v=KJiMcyUxObM'
    ],
    'Mobile Applications Developer': [
        'https://www.youtube.com/watch?v=tZTzidVpZ6c',
        'https://www.youtube.com/watch?v=SD9KnFsVKsQ',
        'https://www.youtube.com/watch?v=tCGQ3DXPL9A'
    ],
    'Network Security Engineer': [
        'https://www.youtube.com/watch?v=GM9yGj5tdHc',
        'https://www.youtube.com/watch?v=CaUsPUMqltU',
        'https://www.youtube.com/watch?v=hEQM3SRWC54'
    ],
    'Software Developer': [
        'https://www.youtube.com/watch?v=2tZs2S5gmg0',
        'https://www.youtube.com/watch?v=f6egULnni8Q',
        'https://www.youtube.com/watch?v=fxaOGu_Cdys'
    ],
    'Software Engineer': [
        'https://www.youtube.com/watch?v=PIGrPkNPz1k',
        'https://www.youtube.com/watch?v=BrBRpzx_Q9Y',
        'https://www.youtube.com/watch?v=cnNE83QYobk'
    ],
    'Software Quality Assurance (QA) / Testing': [
        'https://www.youtube.com/watch?v=qkUfVNBVLrI',
        'https://www.youtube.com/watch?v=1wvYjuq9508',
        'https://www.youtube.com/watch?v=g0PrXoWKM2Y&t=1109s'
    ],
    'Systems Security Administrator': [
        'https://www.youtube.com/watch?v=Bc_d-y7-zv8',
        'https://www.youtube.com/watch?v=mVuAIjwr4Gc',
        'https://www.youtube.com/watch?v=SRyJbiFynyk'
    ],
    'Technical Support': [
        'https://www.youtube.com/watch?v=RJ6WiYtaYmo',
        'https://www.youtube.com/watch?v=gLNAF9C39SI',
        'https://www.youtube.com/watch?v=C_y3k_nDSgw'
    ],
    'UX Designer': [
        'https://www.youtube.com/watch?v=3zICP8XADfs',
        'https://www.youtube.com/watch?v=d6xn5uflUjg',
        'https://www.youtube.com/watch?v=y2W0D-fQh-Q'
    ],
    'Web Developer': [
        'https://www.youtube.com/watch?v=MkcfB7S4fq0',
        'https://www.youtube.com/watch?v=5RiZQoULuJ8',
        'https://www.youtube.com/watch?v=TrtwfitXKVg'
    ],
    
}


import pickle

# Load model once
with open('model/weights.pkl', 'rb') as file:
    clf = pickle.load(file)


@app.route('/career/page1', methods=['GET', 'POST'])
def career_page1():
    if 'user_id' in session:
        # User is logged in
        global user_id, username
        user_id = session['user_id']
        username = session['username']

        if request.method == 'POST':
            session['user_data'] = []
            session['user_data'].append(float(request.form['Logical_quotient_rating']))
            session['user_data'].append(float(request.form['coding_skills_rating']))
            return redirect('/career/page2')
        return render_template('career/1.html')
    else:
    # User is not logged in, redirect to login page
        return redirect(url_for('login'))


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

    # Store the prediction in the database
    cursor = mysql.connection.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO predictions (user_id, username, prediction, timestamp) VALUES (%s, %s, %s, %s)", (user_id, username, prediction[0], current_time))
    mysql.connection.commit()
    cursor.close()

    # Get the recommended video links based on the prediction
    recommended_video_links = video_recommendations.get(prediction[0], [])

    # Create the YouTube video IDs for each recommended video
    youtube_video_ids = []
    for video_link in recommended_video_links[:3]:
        video_id = get_video_id(video_link)
        if video_id:
            youtube_video_ids.append(video_id)

    return render_template('user/result.html', username=username, prediction=prediction, classprobs=predclassprob, youtube_video_ids=youtube_video_ids)




# @app.route('/user_prediction', methods=['GET', 'POST'])
# def user_prediction():
#     if 'user_id' in session:
#         # User is logged in
#         user_id = session['user_id']
#         username = session['username']

#         if request.method == 'POST':
#             # Extract the form data
#             logical_quotient_rating = float(request.form['Logical_quotient_rating']) 
#             coding_skills_rating = float(request.form['coding_skills_rating']) 
#             hackathons = float(request.form['hackathons']) 
#             public_speaking_points = float(request.form['public_speaking_points']) 
#             self_learning_capability = float(request.form['self_learning_capability']) 
#             extra_courses_did = float(request.form['Extra_courses_did'])  
#             taken_inputs_from_seniors_or_elders = float(request.form['Taken_inputs_from_seniors_or_elders'])  
#             worked_in_teams_ever = float(request.form['worked_in_teams_ever']) 
#             introvert = float(request.form['Introvert'])   
#             reading_and_writing_skills = float(request.form['reading_and_writing_skills'])  
#             memory_capability_score = float(request.form['memory_capability_score'])   

#             a_management = float(request.form['A_Management'])
#             a_technical = float(request.form['A_Technical'])
#             b_hard_worker = float(request.form['B_hard_worker'])
#             b_smart_worker = float(request.form['B_smart_worker'])

#             interested_subjects = float(request.form['Interested_subjects'])    
#             interested_type_of_books = float(request.form['Interested_Type_of_Books'])  
#             certifications = float(request.form['certifications']) 
#             workshops = float(request.form['workshops'])  
#             type_of_company_want_to_settle_in = float(request.form['Type_of_company_want_to_settle_in'])   
#             interested_career_area = float(request.form['interested_career_area']) 

#             # Create a numpy array with the user input
#             userdata = np.array([a_management, a_technical, b_hard_worker, b_smart_worker, logical_quotient_rating, coding_skills_rating, hackathons, public_speaking_points, self_learning_capability, extra_courses_did, taken_inputs_from_seniors_or_elders,
#                         worked_in_teams_ever, introvert, reading_and_writing_skills, memory_capability_score, interested_subjects,
#                         interested_type_of_books, certifications, workshops, type_of_company_want_to_settle_in, interested_career_area]).reshape(1, -1)
            
#             # Make the prediction
#             prediction = clf.predict(userdata)
#             print(prediction)
#             classprobs = clf.predict_proba(userdata)
#             print(classprobs)
#             predclassprob = np.max(classprobs)
#             print(predclassprob)

#             # Store the prediction in the database
#             cursor = mysql.connection.cursor()
#             current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             cursor.execute("INSERT INTO predictions (user_id, username, prediction, timestamp) VALUES (%s, %s, %s, %s)", (user_id, username, prediction[0], current_time))
#             mysql.connection.commit()
#             cursor.close()

#             # Get the recommended video links based on the prediction
#             recommended_video_links = video_recommendations.get(prediction[0], [])

#             # Create the YouTube video IDs for each recommended video
#             youtube_video_ids = []
#             for video_link in recommended_video_links[:3]:
#                 video_id = get_video_id(video_link)
#                 if video_id:
#                     youtube_video_ids.append(video_id)

#             return render_template('user/result.html', username=username, prediction=prediction, classprobs=predclassprob, youtube_video_ids=youtube_video_ids)
        
#         else:
#             return render_template('user_prediction.html', username=username)
#     else:
#         # User is not logged in, redirect to login page
#         return redirect(url_for('login'))
    




# Function to extract YouTube video ID from the URL
def get_video_id(url):
    video_id = None
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'www.youtube.com':
        query_string = parse_qs(parsed_url.query)
        if 'v' in query_string:
            video_id = query_string['v'][0]
    return video_id



# Show Prediction Route
@app.route('/show_prediction')
def show_prediction():
    if 'admin_id' in session:
        # Admin is logged in
        admin_id = session['admin_id']
        admin_username = session['admin_username']

        # Retrieve the users' data from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM predictions")
        predictions = cursor.fetchall()
        cursor.close()

        # Debug print statement
        print(predictions)

        # Pass the users' data to the template for rendering
        return render_template('admin/show_predictions.html', admin_username=admin_username, predictions=predictions)

    else:
        return redirect('/admin-login')
    

# Delete Predictions Route
@app.route('/admin/delete_pred/<int:prediction_id>', methods=['GET', 'POST'])
def delete_prediction(prediction_id):
    if 'admin_id' in session:
        # Admin is logged in
        admin_id = session['admin_id']
        admin_username = session['admin_username']

        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM predictions WHERE id = %s", (prediction_id,))
        mysql.connection.commit()
        cursor.close()

        return redirect('/show_prediction')

    else:
        return redirect('/admin-login')




if __name__ == '__main__':
    app.run(debug=True)
