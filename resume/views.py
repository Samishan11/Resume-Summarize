from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserProfile
from .forms import ResumeUploadForm
import textract
import spacy

def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        print("aahah")
        if form.is_valid():
            # Save the uploaded resume to the user profile
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.resume = form.cleaned_data['resume']
            user_profile.save()
            print('user_profile',user_profile)
            
            # Summarize the resume using spaCy
            file_path = user_profile.resume.path
            print('file_path',file_path)
            text = textract.process(file_path)
            print('text',text)
            nlp = spacy.load('en_core_web_sm')
            doc = nlp(text)
            print('doc',doc)
            summary = summarize_text(doc)
            print('summary',summary)
            
            # Render a new template with the summary
            return render(request, 'resume_upload.html', {'summary': summary})
    else:
        form = ResumeUploadForm()
        print("err")
    return render(request, 'resume_upload.html', {'form': form})

def summarize_text(doc):
    # Extract the candidate's name
    name = None
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name = ent.text
            break
    # Extract the candidate's contact information
    contact_info = []
    for ent in doc.ents:
        if ent.label_ == 'PHONE_NUMBER' or ent.label_ == 'EMAIL':
            contact_info.append(ent.text)
    # Extract the candidate's work experience
    work_experience = []
    for ent in doc.ents:
        if ent.label_ == 'ORG':
            work_experience.append(ent.text)
    # Extract the candidate's education
    education = []
    for ent in doc.ents:
        if ent.label_ == 'EDUCATION':
            education.append(ent.text)
    # Extract the candidate's skills
    skills = []
    for token in doc:
        if token.pos_ == 'NOUN':
            skills.append(token.text)
    # Generate a summary of the most important information
    summary = 'Name: {}\n\nContact Information: {}\n\nWork Experience: {}\n\nEducation: {}\n\nSkills: {}'.format(name, ', '.join(contact_info), ', '.join(work_experience), ', '.join(education), ', '.join(skills))
    print('summary1',summary)
    return summary
