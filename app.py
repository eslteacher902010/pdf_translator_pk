from flask import Flask, request, render_template, redirect, url_for, flash
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import FlaskForm
from wtforms import SubmitField
from werkzeug.utils import secure_filename
import fitz 
import os
from io import BytesIO
from datetime import datetime
import deepl
from dotenv import load_dotenv
from flask import send_file
import os 

load_dotenv()

auth_key=os.getenv("API_KEY")
translator = deepl.Translator(auth_key)
print("Loaded API Key:", auth_key)



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


class UploadFile(FlaskForm):
    upload = FileField('Select File', validators=[
    FileRequired(),
    FileAllowed([ 'pdf'], 'Only PDFs allowed!')
    ])
    submit = SubmitField('Upload')



@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('uploads', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash("File not found.")
        return redirect(url_for('index'))




@app.route('/', methods=['GET'])
def index():
    form = UploadFile()
    return render_template('index.html', form=form)


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    form = UploadFile()
    if form.validate_on_submit():
        

        uploaded_file = form.upload.data
        os.makedirs("uploads", exist_ok=True) 


        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join('uploads', filename))

        doc = fitz.open(os.path.join('uploads', filename))
        text = ""
        for page in doc:
            text += page.get_text()

        return render_template("confirm_text.html", extracted_text=text)

    return render_template('index.html', form=form)


@app.route('/translate', methods=['POST'])
def translate_text():
    text = request.form.get('text')
    target_lang = request.form.get('target_lang', 'DE')
    form = UploadFile()  # you correctly create the form

    if not text:
        flash("No text provided.")
        return redirect(url_for('index'))

    try:
        result = translator.translate_text(text, target_lang=target_lang)
        if not result or not result.text:
            raise ValueError("No translation received.")

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"translation_{target_lang}_{timestamp_str}.txt"
        output_path = os.path.join('uploads', output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.text)

       
        return render_template("translation.html", translated_txt=result.text, filename=output_filename, form=form)

    except Exception as e:
        print("Translation error:", str(e))
        return render_template("translation.html", translated_txt="Translation failed. Please try again later.", filename=None, form=form)




if __name__ == '__main__':
    app.run(debug=True)








