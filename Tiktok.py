from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import random
import os
import datetime
import json

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# File to store posts
POSTS_FILE = 'posts.json'

# Load existing posts from file if available
if os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, 'r') as file:
        posts = json.load(file)
else:
    posts = []

@app.route('/')
def home():
    return render_template('home.html', posts=posts)

@app.route('/create_post', methods=['POST'])
def create_post():
    author = request.form['author']
    title = request.form['title']
    content = request.form['content']
    image_url = request.form['image_url']

    # Check if both image file and image URL are provided
    if 'image_file' in request.files and image_url:
        return "Error: Please provide either an image file or an image URL, not both."

    # Check if an image file was uploaded
    if 'image_file' in request.files:
        image_file = request.files['image_file']

        # Save the uploaded image to the 'uploads' folder
        if image_file and allowed_file(image_file.filename):
            # Use a custom filename based on the current timestamp
            filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
            print("filename:", filename)  # Debugging line
            image_file.save(filename)
            image_url = url_for('uploaded_file', filename=os.path.basename(filename))
            print("image_url:", image_url)  # Debugging line

    # Create a new post
    new_post = {
        'author': author,
        'title': title,
        'image_url': image_url,
        'content': content
    }

    posts.append(new_post)

    # Save the updated posts to the file
    with open(POSTS_FILE, 'w') as file:
        json.dump(posts, file)

    return redirect(url_for('home'))

@app.route('/erase_all_posts', methods=['POST'])
def erase_all_posts():
    # Check if the request comes from an admin (you can enhance this check based on your needs)
    if request.form.get('admin_key') == 'your_secret_admin_key':
        # Erase all posts
        global posts
        posts = []

        # Save the empty posts list to the file
        with open(POSTS_FILE, 'w') as file:
            json.dump(posts, file)

        return jsonify({'success': True, 'message': 'All posts erased successfully.'})
    else:
        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 403

# Helper function to check if the file has an allowed extension
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
