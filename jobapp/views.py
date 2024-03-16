from django.shortcuts import render, redirect
from django.conf import settings
from resume_parser import resumeparse
from pyresparser import ResumeParser
import os
import PyPDF2
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import NewUserForm
from .utils import check_email, check_phone, check_empty, find_jobs

def register_view(request):
    if request.user.is_authenticated:
        return redirect("")
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('')
        else:
            print(form.errors)
    else:
        form = NewUserForm()
    return render(request, 'page-register.html', {'form': form})

@login_required
def home_view(request):
    if request.method == "POST" and request.FILES:
        file = request.FILES['resume']
        path = os.path.join(settings.MEDIA_ROOT, "resume.pdf")
        with open(path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)
        data = resumeparse.read_file(path)
        tmp = ResumeParser(path).get_extracted_data()
        name = check_empty(data["name"], tmp["name"])
        email = check_email(data["email"], tmp["email"])
        phone = check_phone(data["phone"], tmp["mobile_number"])
        designation = check_empty(data["designition"], tmp["designation"])
        university = check_empty(data["university"], tmp["college_name"])
        skills = "\n".join(data["skills"])
        with open(path, 'rb') as pdfFileObj:
            pdfReader = PyPDF2.PdfReader(pdfFileObj)
            for i in range(len(pdfReader.pages)):
                pageObj = pdfReader.pages[i]
                exp = pageObj.extract_text().split("\n")
                exp = "\n".join([x for x in exp if len(x.split()) >= 10])
                skills = skills + exp
        context = {"name": name, "email": email, "phone": phone, "designation": designation, "skills": skills, "university": university}
        return render(request, "candidate-data.html", context=context)
    return render(request, "index.html", {})

@login_required
def candidate_data_view(request):
    if request.method == "POST":
        skills = request.POST["skills"]
        recommended = find_jobs(skills.replace("\n", " "))
        print(recommended)
        return render(request, "jobs-list.html", {"recommended": recommended})
    return redirect("")

#tabdil

def dashboard_power_bi(request):
    # Lien vers le tableau de bord Power BI
    lien_dashboard = "https://app.powerbi.com/groups/212e31d2-b901-4242-bc12-2736a3dd1fdf/reports/c6e93c0b-5ce5-419a-98ac-de5bef7eedb5/ReportSection?experience=power-bi&clientSideAuth=0"
    return render(request, 'dashboard_power_bi.html', {'lien_dashboard': lien_dashboard})
