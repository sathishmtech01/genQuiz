from flask import Flask, render_template, request, redirect, url_for
import fitz  # PyMuPDF
import os
from transformers import pipeline

app = Flask(__name__)

# Initialize the Hugging Face pipeline
generator = pipeline('text-generation', model='gpt-3.5-turbo')  # You can choose another model

def extract_text_from_pdf(pdf_path):
    """ Extract text from PDF file """
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def generate_quiz_from_text(text):
    """ Generate quiz questions using Hugging Face model """
    prompt = f"Generate a quiz with 5 questions and answers from the following text:\n\n{text}\n\nQuiz:"
    response = generator(prompt, max_length=500, num_return_sequences=1)
    quiz = response[0]['generated_text'].strip()
    questions = []
    for q in quiz.split('\n\n'):
        parts = q.split('\n')
        question = parts[0]
        options = parts[1:-1]
        answer = parts[-1].replace("Answer: ", "")
        questions.append({'question': question, 'options': options, 'answer': answer})
    return questions

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return redirect(request.url)
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return redirect(request.url)
        if pdf_file:
            pdf_path = os.path.join("uploads", pdf_file.filename)
            pdf_file.save(pdf_path)
            policy_text = extract_text_from_pdf(pdf_path)
            questions = generate_quiz_from_text(policy_text)
            return render_template('quiz.html', questions=questions)
    return render_template('index.html')

@app.route('/check_answers', methods=['POST'])
def check_answers():
    results = []
    for i in range(1, 6):  # Assuming 5 questions
        user_answer = request.form.get(f'question{i}')
        correct_answer = request.form.get(f'answer{i}')
        question = request.form.get(f'question{i}')
        is_correct = user_answer == correct_answer
        results.append({
            'question': question,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })
    return render_template('results.html', results=results)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
