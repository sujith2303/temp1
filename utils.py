from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def evaluate(actual,predicted,qtype,num_questions):
    score = 0
    for i in range(num_questions):
        if qtype == 'MCQS':
            # print('prediction',actual[i].split(')')[0].lower().strip(),predicted[i].lower(),int(actual[i].split(')')[0].lower().strip()==predicted[i].lower()))
            # print(len(actual[i].split(')')[0].lower()),type(actual[i].split(')')[0].lower()))
            # print(len(predicted[i].lower()),type(predicted[i].lower()))
            score+=int(actual[i].split(')')[0].lower().strip()==predicted[i].lower())
            print(score)
        elif qtype == 'essay'  or qtype =='FIBs':
            score+= int(actual[i].lower()==predicted[i].lower())
        else:
            tokenizer = AutoTokenizer.from_pretrained("textattack/roberta-base-MRPC")
            model = AutoModelForSequenceClassification.from_pretrained("textattack/roberta-base-MRPC")
            logits = model.forward(tokenizer(actual[i]+'.'+predicted[i],return_tensors='pt')).logits
            predictions = torch.argmax(torch.nn.functional.softmax(logits,dim=-1),dim=-1).item()
            result = predictions[1]
            score+=result
    return score
