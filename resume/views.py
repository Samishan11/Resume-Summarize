import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UserProfile
from .forms import ResumeUploadForm
from PyPDF2 import PdfReader
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
import re

nltk.download("punkt")


def extract_email_and_phone(text):
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    phone_pattern = r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    return emails, phones


def extract_experiences_and_skills(text):
    experiences = []
    skills = []
    lines = text.split("\n")
    for line in lines:
        if line.lower().startswith("experiences"):
            experiences = [exp.strip() for exp in line.split(":")[1].split(",")]
        elif line.lower().startswith("skills"):
            skills = [skill.strip() for skill in line.split(":")[1].split(",")]
    return experiences, skills


def upload_resume(request):
    try:
        if request.method == "POST":
            form = ResumeUploadForm(request.POST, request.FILES)
            if form.is_valid():
                # Save the uploaded resume to the user profile
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.resume = form.cleaned_data["resume"]
                user_profile.save()

                # Update file path format to forward slashes
                file_path = user_profile.resume.file.name

                # Extract text from PDF file using PdfReader
                with open(file_path, "rb") as file:
                    pdf_reader = PdfReader(file)
                    text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text()

                    # Parse the text from the PDF file
                    parser = PlaintextParser.from_string(text, Tokenizer("english"))
                    summarizer = LexRankSummarizer()
                    # Get the summary with a specified number of sentences (e.g., 3)
                    summary = summarizer(parser.document, sentences_count=3)

                    # Extract the summarized text from the summary
                    summarized_text = [str(sentence) for sentence in summary]

                    # Convert the summarized text back to a single string
                    summarized_text = " ".join(summarized_text)

                # Extract 'Experiences' and 'Skills' sections from the summarized text
                # a = "Summary Senior Web Developer specializing in front end development.\nSkills:\n- Project management\n- Strong decision maker\n- Complex problem solver\n- Creative design\n- Innovative\n- Service-focused\nExperience:\nWeb Developer - 09/2015 to 05/2019\nLuna Web Design, New York\n- Cooperate with designers to create clean interfaces and simple, intuitive interactions and experiences.\n- Work with senior developer to manage large, complex design projects for corporate clients."
                # a = "Summary: Senior Web Developer specializing in front end development.\nSkills:\n- Project management\n- Strong decision maker\n- Complex problem solver\n- Creative design\n- Innovative\n- Service-focused\nExperience:\nWeb Developer - 09/2015 to 05/2019\nLuna Web Design, New York\n- Cooperate with designers to create clean interfaces and simple, intuitive interactions and experiences.\n- Work with senior developer to manage large, complex design projects for corporate clients."
                a = "Summary: Senior Web Developer specializing in front end development.\nSkills:\n- Project management\n- Strong decision maker\n- Complex problem solver\n- Creative design\n- Innovative\n- Service-focused\nExperience:\nWeb Developer - 09/2015 to 05/2019\nLuna Web Design, New York\n- Cooperate with designers to create clean interfaces and simple, intuitive interactions and experiences.\n- Work with senior developer to manage large, complex design projects for corporate clients."

                experiences, skills = extract_experiences_and_skills(summarized_text)
                # emails, phones = extract_email_and_phone(summarized_text)
                with open(file_path, "rb") as file:
                    pdf_reader = PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text()

                emails, phones = extract_email_and_phone(summarized_text)
                print("Emails:", emails)
                print("Phones:", phones)
                # Print the extracted 'Experiences' and 'Skills' sections
                print("Experiences:")
                for experience in experiences:
                    print("- " + experience)

                print("Skills:")
                for skill in skills:
                    print("- " + skill)

                return render(
                    request,
                    "resume_upload.html",
                    {"summarized_text": summarized_text, "skills": skills},
                )
        else:
            form = ResumeUploadForm()
            return render(request, "resume_upload.html", {"form": form})
    except Exception as e:
        print("error", e)
