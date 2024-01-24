from transformers import AutoModelForSeq2SeqLM,AutoTokenizer
import torch

def load_model_question():
    model_name = 'Sujithanumala/QuizBot.AI-base'
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model,tokenizer

def generate_questions(context,num_questions,question_type):
    model,tokenizer = load_model_question()
    instruction = ''
    if question_type=='MCQS':
        instruction = ' \n  Generate MCQS'
    elif question_type =='FillInTheBlanks':
        instruction = ' \n Generate FIBs'
    elif question_type =='TrueOrFalse':
        instruction = '\n Generate True or False'   
    else:
        instruction = ' \n Generate Essay answers'
    questions = []
    answers = []
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    model.to(device)
    predictions = model.generate(tokenizer(context+instruction,return_tensors='pt').to(device)['input_ids'],max_length = 100,num_beams = 10,num_return_sequences=num_questions)
    for i in predictions:
        result = tokenizer.decode(i,skip_special_tokens=True)
        result = result.split('[ANSWER]:')
        question,answer = result
        question = question.split('[QUESTION]: ')[1]
        questions.append(question)
        answers.append(answer)
    return questions,answers

if __name__=="__main__":
    num_questions = 5
    context = """LanguageTranslatorTakes in an image of text, process it, and gives an audio output of the text in the user-specifiedlanguage(around 99 different languages). Can able to identify 80 different languages of text(computer as wellas handwritten).Downloading DependenciesTesseract-OCR dlick here to download Tesseract into your computer.InstallationYou can simply use pip to install the latest version of pytesseract.pip install pytesseract"""
    questions,answers = generate_questions(context,num_questions,'FillInTheBlanks')
    for i in range(num_questions):
        print(f'Question {i+1}:' , questions[i])
        print(f'Answer:',answers[i])
        print('-'*100)

# textattack/roberta-base-MRPC