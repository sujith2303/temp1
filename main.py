from flask import Flask,render_template,request,redirect,url_for,session
import os
from utils import evaluate
from model import generate_questions
import pytesseract
import numpy as np
import cv2

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

def textdetection(img):
    pytesseract.pytesseract.tesseract_cmd = r"D:\Other Files\Tesseract\tesseract\tesseract.exe"
    boxes = pytesseract.image_to_boxes(img)
    s1 = pytesseract.image_to_string(img)
    s = ''
    for b in boxes.splitlines():
        b = b.split(' ')
        s = s + b[0]
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
    if s == '~':
        return 'No Text Detected'
    else:
        return  s1.split('  ')
    
def preprocess(file,num_questions,question_type = 'MCQS'):
    # context = textdetection(file)
    context = """Machine learning (ML) is a field of study in artificial intelligence concerned with the development and study of statistical algorithms that can learn from data and generalize to unseen data, and thus perform tasks without explicit instructions.[1] Recently, generative artificial neural networks have been able to surpass many previous approaches in performance.Machine learning approaches have been applied to many fields including large language models, computer vision, speech recognition, email filtering, agriculture, and medicine, where it is too costly to develop algorithms to perform the needed tasks.[4][5] ML is known in its application across business problems under the name predictive analytics. Although not all machine learning is statistically based, computational statistics is an important source of the field's methods."""
    questions,answers = generate_questions(context=context,question_type=question_type,num_questions=num_questions)
    print(questions)
    print('-'*100)
    print(answers)
    options = []
    if question_type=='MCQS':
        question = []
        for i in questions:
            if 'a)' in i:
                q,o = i.split('a)')
            else:
                q,o = i.split('A)')
            question.append(q)

            if 'b)' in i:
                a,o = o.split('b)')
            else:
                a,o = o.split('B)')
                
            if 'c)' in i:
                b,o = o.split('c)')
            else:
                b,o = o.split('C)')

            if 'd)' in i:
                c,d = o.split('d)')
            else:
                c,d = o.split('D)')
            
            options.append([a,b,c,d])
        questions = question
    return questions,answers,options


@app.route('/',methods  = ['GET','POST'])
def login():
    if request.method == 'POST':
        num_questions = int(request.form['num_questions'])
        question_type = request.form['selected_option']
        print(question_type)
        file = request.form['filename']
        # cv2.imshow('s',cv2.imread(file))
        result = preprocess(file,num_questions,question_type=question_type[:-1])
        questions,answers,options = result
        session['questions'] = questions
        session['answers'] = answers
        session['options'] = options
        session['num_questions'] =num_questions
    
        return redirect(url_for('Questions_TrueOrFalse'))
    return render_template('login.html')

@app.route('/Questions_MCQS',methods = ['GET','POST'])
def Questions_MCQS():
    questions = session.get('questions',[])
    answers = session.get('answers',[])
    options = session.get('options',[])
    num_questions =session.get('num_questions')
    if request.method =='POST':
        responses = []
        for i in range(1,num_questions+1):
            try:
                responses.append(request.form[f'q{i}'])
            except:
                responses.append(f'{i} Unanswered')
        print(responses)
        session['score'] = evaluate(answers,responses,'MCQS',num_questions=num_questions)
        session['user_responses'] = responses
        return redirect(url_for('Summary'))
    return render_template('MCQS.html',num_questions = num_questions,questions = questions,options = options)

@app.route('/Questions_FIBS',methods = ['GET','POST'])
def Questions_FIBS():
    questions = session.get('questions',[])
    answers = session.get('answers',[])
    num_questions =session.get('num_questions')
    if request.method =='POST':
        responses = []
        for i in range(1,num_questions+1):
            try:
                responses.append(request.form[f'q{i}'])
            except:
                responses.append(f'{i} Unanswered')
        session['score'] = evaluate(answers,responses,'FIBS',num_questions=num_questions)
        session['user_responses'] = responses
        return redirect(url_for('Summary'))
    return render_template('FIBS.html',num_questions = num_questions,questions = questions)

@app.route('/Questions_TrueOrFalse',methods =['GET','POST'])
def Questions_TrueOrFalse():
    questions = session.get('questions',[])
    answers = session.get('answers',[])
    num_questions =session.get('num_questions')
    if request.method =='POST':
        responses = []
        for i in range(1,num_questions+1):
            try:
                responses.append(request.form[f'q{i}'])
            except:
                responses.append(f'{i} Unanswered')
        print(responses)
        session['score'] = evaluate(answers,responses,'TrueOrFalse',num_questions=num_questions)
        session['user_responses'] = responses
        return redirect(url_for('Summary'))
    return render_template('TrueOrFalse.html',num_questions = num_questions,questions = questions)

@app.route('/Questions_Essay')
def Questions_Essay():
    questions = session.get('questions',[])
    answers = session.get('answers',[])
    num_questions =session.get('num_questions')
    if request.method =='POST':
        responses = []
        for i in range(1,num_questions+1):
            try:
                responses.append(request.form[f'q{i}'])
            except:
                responses.append(f'{i} Unanswered')
        session['user_responses'] = responses
        session['score'] = evaluate(answers,responses,'Essay',num_questions=num_questions)
        return redirect(url_for('Summary'))
    return render_template('EssayAnswers.html',num_questions = num_questions,questions = questions)

@app.route('/Summary')
def Summary():
    num_questions = session.get('num_questions')
    score = session.get('score')
    # score = 0 
    answers = session.get('answers')
    user_responses = session.get('user_responses')
    return render_template('submittedanswers.html',score = score,num_questions =num_questions,answers =answers,user_responses = user_responses)

if __name__=='__main__':
    app.run(debug=True)