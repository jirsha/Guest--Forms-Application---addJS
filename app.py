from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import base64
import json

app = Flask(__name__)
app.secret_key = 'top-secret'

# Configure upload settings - SINGLE SOURCE OF TRUTH
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE_MB = 5  # Only need to change this ONE value
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_BYTES

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_config():
    """Return upload configuration for templates"""
    return {
        'max_file_size_mb': MAX_FILE_SIZE_MB,
        'max_file_size_bytes': MAX_FILE_SIZE_BYTES,
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'allowed_extensions_str': ', '.join(ALLOWED_EXTENSIONS).upper()
    }

# Error handler for file too large
@app.errorhandler(413)
def file_too_large(e):
    error = f"File too large! Maximum file size is {MAX_FILE_SIZE_MB}MB. Please choose a smaller image."
    return render_template('profileForm.html', error=error), 413

@app.route('/')
def index():
    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        quan = request.form.get('quan', '').strip()
        comments = request.form.get('comments', '').strip()
        rel = request.form.get('rel', '').strip()
        accommodations = request.form.get('accommodations') == "yes"
        
        # Validation
        if not name or not email or not quan or not rel:
            error = "Please fill in all required fields"
            return render_template('profileForm.html', error=error, upload_config=get_upload_config())
        
        # Handle file upload
        profile_picture_filename = None
        profile_picture_base64 = None
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                # Check file size first
                file.seek(0, os.SEEK_END)
                file_size_bytes = file.tell()
                file.seek(0)
                file_size_mb = file_size_bytes / (1024 * 1024)
                
                if file_size_bytes > MAX_FILE_SIZE_BYTES:
                    error = f"File too large! Your file is {file_size_mb:.2f}MB. Maximum allowed size is {MAX_FILE_SIZE_MB}MB. Please compress or choose a smaller image."
                    return render_template('profileForm.html', error=error, upload_config=get_upload_config())
                
                if allowed_file(file.filename):
                    # Secure the filename and save the file
                    filename = secure_filename(file.filename)
                    import uuid
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    profile_picture_filename = unique_filename
                    
                    # Also create base64 version for display
                    with open(filepath, 'rb') as img_file:
                        profile_picture_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                else:
                    # Get file extension for error message
                    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
                    error = f"Invalid file type '{file_ext}'. Please upload an image file ({get_upload_config()['allowed_extensions_str']})"
                    return render_template('profileForm.html', error=error, upload_config=get_upload_config())
        
        return render_template(
            'profileSuccess.html',
            name=name,
            email=email,
            quan=quan,
            comments=comments,
            rel=rel,
            accommodations=accommodations,
            profile_picture_filename=profile_picture_filename,
            profile_picture_base64=profile_picture_base64
        )
    
    return render_template('profileForm.html', upload_config=get_upload_config())

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        rating = request.form.get('rating', '').strip()
        feedback = request.form.get('feedback', '').strip()

        if not rating:
            error = "Please provide a rating"
            return render_template('feedbackForm.html', error=error)

        return render_template(
            'feedbackSuccess.html',
            rating=rating,
            feedback=feedback
        )

    return render_template('feedbackForm.html')

@app.route('/upload-config')
def upload_config():
    """API endpoint for JavaScript to fetch configuration"""
    """return jsonify(get_upload_config())"""