from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Test, Question, Result, CustomUser
from .utils import grade_answer


@csrf_exempt
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role", "student")

        if CustomUser.objects.filter(username=username).exists():
            return HttpResponse("Bu username allaqachon mavjud!")
        
        CustomUser.objects.create_user(username=username, password=password, role=role)
        return redirect("/login/")

    return HttpResponse(open("core/templates/register.html").read() if hasattr(open, '__call__') else """
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Ro'yxatdan o'tish</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{background:linear-gradient(135deg,#0f172a,#1e2937);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;}</style>
    </head><body>
    <div class="card p-4" style="width:420px;background:rgba(255,255,255,0.1);">
        <h2 class="text-center">Ro'yxatdan o'tish</h2>
        <form method="post">
            <input name="username" class="form-control my-2" placeholder="Username" required><br>
            <input name="password" type="password" class="form-control my-2" placeholder="Parol" required><br>
            <select name="role" class="form-select my-2">
                <option value="student">Talaba</option>
                <option value="teacher">O'qituvchi</option>
            </select><br>
            <button type="submit" class="btn btn-primary w-100">Ro'yxatdan o'tish</button>
        </form>
        <p class="text-center mt-3"><a href="/login/" class="text-info">Kirish</a></p>
    </div>
    </body></html>
    """)


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        user = authenticate(username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            if user.role == "admin": return redirect("/admin-panel/")
            elif user.role == "teacher": return redirect("/create/")
            else: return redirect("/test/")
        return HttpResponse("Login yoki parol noto'g'ri!")

    # Login HTML (Bootstrap)
    return HttpResponse("""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Kirish</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{background:linear-gradient(135deg,#0f172a,#1e2937);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;}</style>
    </head><body>
    <div class="card p-4" style="width:420px;background:rgba(255,255,255,0.1);">
        <h2 class="text-center">Tizimga kirish</h2>
        <form method="post">
            <input name="username" class="form-control my-2" placeholder="Username" required><br>
            <input name="password" type="password" class="form-control my-2" placeholder="Parol" required><br>
            <button type="submit" class="btn btn-success w-100">Kirish</button>
        </form>
        <p class="text-center mt-3"><a href="/register/" class="text-info">Ro'yxatdan o'tish</a></p>
    </div>
    </body></html>
    """)


@login_required
def take_test(request):
    test = Test.objects.last()
    if not test:
        return HttpResponse("<h2 class='text-center mt-5'>Hozircha test yo'q</h2>")

    questions = test.questions.all()

    if request.method == "POST":
        total = sum(grade_answer(request.POST.get(str(q.id), ""), q.correct_answer) for q in questions)
        score = round(total / len(questions), 2) if questions else 0
        Result.objects.create(test=test, user=request.user, score=score)
        return HttpResponse(f"<h1 class='text-center text-success mt-5'>Sizning natijangiz: {score}%</h1><br><a href='/test/' class='btn btn-primary'>Yana topshirish</a>")

    html = f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>{test.title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{{background:#0f172a;color:white;}}</style>
    </head><body>
    <div class="container mt-5">
        <h2 class="text-center">{test.title}</h2>
        <form method="post">
            {''.join(f'<div class="card mb-4 p-4 bg-dark"><h5>{q.text}</h5><input name="{q.id}" class="form-control mt-3" placeholder="Javobingiz..." required></div>' for q in questions)}
            <button type="submit" class="btn btn-success btn-lg w-100">Natijani ko'rish</button>
        </form>
    </div>
    </body></html>
    """
    return HttpResponse(html)


# Qolgan view lar (create_test, admin_panel va h.k.) ni keyingi javobda beraman, chunki juda uzun bo'lib ketdi.
