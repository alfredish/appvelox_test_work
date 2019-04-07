from flask import Flask, render_template, flash, redirect,request, redirect, url_for,send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField,FileField
from wtforms.validators import DataRequired
import sqlite3
import os
from werkzeug.utils import secure_filename
from flask import request


class LoginForm(FlaskForm):
    data = StringField('{‘height’: h, ‘width’: w}, где h,w – размеры к которым нужно преобразовать изображение в px', validators=[DataRequired()])
    #href = StringField('Ссылка на изображение',  validators=[DataRequired()])
    submit = SubmitField("Отправить запрос")
    file = FileField()


UPLOAD_FOLDER = '../try_find_work/static/images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg'])

app = Flask(__name__) #создаем экземпляр объекта Flask
app.config['SECRET_KEY'] = 'lEay3xpXwDHOMQG0tYTKAiYQlbQ2pl0BS78RtiFQOdwrW7jgU7TleH8qLLr7'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



#добавить проверки на размер в px
@app.route('/', methods=['POST', 'GET'])
def main():
    form = LoginForm()
    if form.validate_on_submit():
        con = sqlite3.connect('ImageSize.db')
        cur = con.cursor()
        cur.execute("select MAX(id) from image")
        max_id = cur.fetchall()
        #Сделать проверку на тип вводимых данных
        max_id = max_id[0][0]
        if max_id == None:
            max_id = 0
        max_id += 1
        var_name = ""
        for i in form.data.data:
            if ord(str(i)) == 44:
                var_name += " "
            if ord(str(i)) >= 48 and ord(str(i)) <= 57:
                var_name += i

        var_name = var_name.split()

        #работа с файлом
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            href = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(href)


        cur.execute("INSERT INTO image(id,href,height,width) VALUES (?, ?, ?, ?)", (max_id, href, var_name[0],var_name[1]))
        con.commit()
        con.close()
        #flask text with id
        flash('ID для изображение {}'.format(max_id))

    return render_template('main.html', form=form)







#Не используется
#функция открывает последнее добавленное изображение
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)






#для отображения статуса и самой фотографии
@app.route('/<n>', methods=['POST', 'GET'])
def check_status(n):

    con = sqlite3.connect('ImageSize.db')
    cur = con.cursor()
    cur.execute("select id from image")
    all_id = cur.fetchall()

    try:
        int(n)
        for i in all_id:
            if i[0] == int(n):
                cur.execute("select height from image where id= ?", n)
                height = cur.fetchall()
                height = height[0][0]
                height = int(height)

                cur.execute("select width from image where id = ?", n)
                width = cur.fetchall()
                width = width[0][0]
                width = int(width)

                cur.execute("select href from image where id = ?", n)
                href = cur.fetchall()
                href = href[0][0]
                href = href[17:]

                return render_template('check_status.html', n=n, width=width, height=height, href=href)
        return "error"
    except:
        return "error"


if __name__ == '__main__':
    app.run(debug=True)
