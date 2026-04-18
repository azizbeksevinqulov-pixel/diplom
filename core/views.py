from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Test, Question, Result, CustomUser
from .utils import grade_answer


# ===================== REGISTER =====================
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

    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Ro'yxatdan o'tish</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #0f172a, #1e2937); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: none; }
        </style>
    </head>
    <body>
        <div class="card p-5 shadow" style="width: 420px;">
            <h2 class="text-center mb-4">Ro'yxatdan o'tish</h2>
            <form method="post">
                <div class="mb-3"><input name="username" class="form-control" placeholder="Username" required></div>
                <div class="mb-3"><input name="password" type="password" class="form-control" placeholder="Parol" required></div>
                <div class="mb-3">
                    <select name="role" class="form-select">
                        <option value="student">Talaba</option>
                        <option value="teacher">O'qituvchi</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary w-100 py-2">Ro'yxatdan o'tish</button>
            </form>
            <p class="text-center mt-3"><a href="/login/" class="text-info">Allaqachon akkaunt bormi? Kirish</a></p>
        </div>
    </body>
    </html>
    """)


# ===================== LOGIN =====================
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

    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Kirish</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #0f172a, #1e2937); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: none; }
        </style>
    </head>
    <body>
        <div class="card p-5 shadow" style="width: 420px;">
            <h2 class="text-center mb-4">Tizimga kirish</h2>
            <form method="post">
                <div class="mb-3"><input name="username" class="form-control" placeholder="Username" required></div>
                <div class="mb-3"><input name="password" type="password" class="form-control" placeholder="Parol" required></div>
                <button type="submit" class="btn btn-success w-100 py-2">Kirish</button>
            </form>
            <p class="text-center mt-3"><a href="/register/" class="text-info">Ro'yxatdan o'tish</a></p>
        </div>
    </body>
    </html>
    """)


# ===================== TEST TOPSHIRISH (Zamonaviy) =====================
@csrf_exempt
@login_required
def take_test(request):
    test = Test.objects.last()
    if not test:
        return HttpResponse("<h2 class='text-center mt-5 text-white'>Hozircha hech qanday test mavjud emas</h2>")

    questions = test.questions.all()

    if request.method == "POST":
        total = sum(grade_answer(request.POST.get(str(q.id), ""), q.correct_answer) for q in questions)
        score = round(total / len(questions), 2) if questions else 0
        Result.objects.create(test=test, user=request.user, score=score)

        return HttpResponse(f"""
        <div class="container mt-5 text-center text-white">
            <div class="card p-5 bg-dark mx-auto" style="max-width: 600px;">
                <h1 class="display-4 text-success">🎉 Natijangiz: <b>{score}%</b></h1>
                <a href="/test/" class="btn btn-primary btn-lg mt-4">Yana topshirish</a>
                <a href="/logout/" class="btn btn-outline-light btn-lg mt-4">Chiqish</a>
            </div>
        </div>
        """)

    html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{test.title}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>body {{ background: #0f172a; color: white; }}</style>
    </head>
    <body>
        <div class="container mt-5">
            <h2 class="text-center mb-5">{test.title}</h2>
            <form method="post">
                {''.join(f'''
                <div class="card mb-4 p-4 bg-dark">
                    <h5 class="mb-3">{q.text}</h5>
                    <input name="{q.id}" class="form-control" placeholder="Javobingizni yozing..." required>
                </div>
                ''' for q in questions)}
                <button type="submit" class="btn btn-success btn-lg w-100 py-3">Natijani ko'rish</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


# ===================== TEST YARATISH =====================
@csrf_exempt
@login_required
def create_test(request):
    if request.method == "POST":
        title = request.POST.get("title")
        if not title:
            return HttpResponse("Test nomi majburiy!")

        test = Test.objects.create(title=title)
        Question.objects.create(
            test=test,
            text=request.POST.get("question"),
            correct_answer=request.POST.get("correct")
        )
        return HttpResponse(f"""
        <h2>Test muvaffaqiyatli yaratildi: <b>{title}</b></h2>
        <a href="/create/" class="btn btn-primary">Yana test yaratish</a>
        <a href="/test/" class="btn btn-success">Testni ko'rish</a>
        """)

    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Test yaratish</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>body { background: #0f172a; color: white; }</style>
    </head>
    <body>
        <div class="container mt-5">
            <h2 class="text-center">Yangi test yaratish</h2>
            <form method="post" class="card p-4 bg-dark mt-4">
                <div class="mb-3"><input name="title" class="form-control" placeholder="Test nomi" required></div>
                <div class="mb-3"><input name="question" class="form-control" placeholder="Savol matni" required></div>
                <div class="mb-3"><input name="correct" class="form-control" placeholder="To'g'ri javob" required></div>
                <button type="submit" class="btn btn-primary w-100">Testni saqlash</button>
            </form>
        </div>
    </body>
    </html>
    """)


# Qolgan oddiy sahifalar
def logout_view(request):
    logout(request)
    return redirect("/login/")

@login_required
def admin_panel(request):
    return HttpResponse("<h2>Admin Panel</h2><p><a href='/users/'>Foydalanuvchilar</a></p>")

def create_admin(request):
    if not CustomUser.objects.filter(username="admin").exists():
        CustomUser.objects.create_superuser(username="admin", password="1234", role="admin")
        return HttpResponse("Admin yaratildi!<br>Username: admin<br>Password: 1234")
    return HttpResponse("Admin allaqachon mavjud")

@login_required
def users_list(request):
    return HttpResponse("<h2>Foydalanuvchilar ro'yxati (keyinroq to'liq qilamiz)</h2>")

@login_required
def results_list(request):
    return HttpResponse("<h2>Natijalar (keyinroq to'liq qilamiz)</h2>")

@login_required
def stats_view(request):
    return HttpResponse("<h2>Statistika (keyinroq Chart.js bilan qilamiz)</h2>")
