from typing import Any, Dict

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

from .forms import UserBioForm, UploadFileForm



def request_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }

    return render(request=request, template_name="requestdataapp/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm,
    }

    return render(request=request, template_name="requestdataapp/user_bio_form.html", context=context)


def handle_file_upload(request: HttpRequest) -> HttpResponse:

    MAX_FILE_SIZE = 1024 * 1024

    context = {
        "form": UploadFileForm(),
    }

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            my_file: UploadedFile = form.cleaned_data["file"]


            if my_file.size <= MAX_FILE_SIZE:
                file_system = FileSystemStorage()
                filename = file_system.save(name=my_file.name, content=my_file)

                context['uploaded_file'] = {
                    'name': my_file.name,
                    'saved_name': filename,
                    'size': my_file.size,
                    'content_type': my_file.content_type,
                    'url': file_system.url(filename),
                }
                print(f"Saved file '{filename}'")
            else:

                context["error_size"] = True
                print(f"File too large: {my_file.size} bytes")

        else:
            context["form_errors"] = True

    context["form"] = form if request.method == "POST" else UploadFileForm()

    return render(request=request, template_name="requestdataapp/file-upload.html", context=context)