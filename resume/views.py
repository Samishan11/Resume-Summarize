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
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.http import HttpResponse, JsonResponse

from django.contrib import messages

nltk.download("punkt")


import re


def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        name_pattern = r"^[a-zA-Z0-9@#$%^&+=_\-\s]*[oO][a-zA-Z0-9@#$%^&+=_\-\s]*$"
        if not re.match(name_pattern, name):
            messages.add_message(
                request,
                messages.ERROR,
                "Name can only contain letters, numbers, and special characters @#$%^&+=_- ",
            )
        elif User.objects.filter(username=name).exists():
            messages.add_message(request, messages.ERROR, "Username is already taken.")
        elif User.objects.filter(email=email).exists():
            messages.add_message(
                request, messages.ERROR, messages.ERROR, "Email is already taken."
            )
        elif len(password1) < 6:
            messages.add_message(
                request, messages.ERROR, "Password must be more than 6 characters."
            )
            print("err")
        elif password1 != password2:
            messages.add_message(request, messages.ERROR, "Passwords do not match.")
        else:
            print("success")
            user = User.objects.create_user(
                username=name, email=email, password=password1
            )
            user.save()
            messages.add_message(request, messages.SUCCESS, "Registered successfully.")
            return redirect("/signup")
    return render(request, "signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST.get("name")
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if not user.is_staff:
                auth.login(request, user)
                return redirect("/resume")
            elif user.is_staff:
                auth.login(request, user)
                return redirect("/admin")
        else:
            messages.add_message(
                request, messages.ERROR, "Username or Passwords do not match."
            )
    return render(request, "signin.html")


def logout(request):
    auth.logout(request)
    return redirect("/")


def index(request):
    return render(request, "index.html")


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
                try:
                    user_profile = UserProfile.objects.get(user=request.user)
                    user_profile.resume = form.cleaned_data["resume"]
                    user_profile.save()
                except UserProfile.DoesNotExist:
                    # Create a new UserProfile instance and save the uploaded resume to it
                    user_profile = UserProfile(
                        user=request.user, resume=form.cleaned_data["resume"]
                    )
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
                    experiences, skills = extract_experiences_and_skills(
                        summarized_text
                    )
                    emails, phones = extract_email_and_phone(summarized_text)
                    # remove email addresses
                    summarized_text = re.sub(r"\S+@\S+", "", text)

                    # remove phone numbers
                    summarized_text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "", text)

                    # remove any text containing '@' or 'phone'
                    summarized_text = re.sub(r"@|phone", "", text, flags=re.IGNORECASE)
                    # Print the extracted 'Experiences' and 'Skills' sections
                    form = ResumeUploadForm(initial={"resume": user_profile.resume})
                    print(emails)
                    return render(
                        request,
                        "resume_upload.html",
                        {
                            "form": form,
                            "message": "Resume uploaded successfully!",
                            "summarized_text": summarized_text,
                            "emails": emails[0],
                            "phones": phones[0],
                        },
                    )
                    # return render(
                    #     request,
                    #     "resume_upload.html",
                    #     {"form": form, "message": "Resume uploaded successfully!"},
                    #     {"summarized_text": summarized_text},
                    # )
            else:
                # Form is not valid, handle the error or return an appropriate response
                print("Form is not valid.")
                return render(request, "resume_upload.html", {"form": form})
        else:
            form = ResumeUploadForm()
            if "resume" in request.FILES:
                form.files["resume"] = request.FILES["resume"]
            return render(request, "resume_upload.html", {"form": form})
    except Exception as e:
        print("error", e)
