from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Test, Question, Result, CustomUser
from .utils import grade_answer


# ===================== REGISTER - ZAMONAVIY DIZAYN =====================
@csrf_exempt
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role", "student")

        if not username or not password:
            return HttpResponse("Username va parol majburiy!")

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
            body {
                background: linear-gradient(135deg, #0f172a 0%, #1e2937 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Segoe UI', sans-serif;
            }
            .card {
                background: rgba(255, 255, 255, 0.09);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 24px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            }
            .btn-primary {
                background: linear-gradient(90deg, #3b82f6, #1e40af);
                border: none;
                padding: 14px;
                font-weight: 600;
                border-radius: 12px;
            }
        </style>
    </head>
    <body>
        <div class="card p-5" style="width: 440px;">
            <div class="text-center mb-4">
                <h2>🎓 Ro'yxatdan o'tish</h2>
                <p class="text-light">Intellektual test baholash tizimi</p>
            </div>
            <form method="post">
                <div class="mb-3">
                    <input name="username" class="form-control form-control-lg" placeholder="Username" required>
                </div>
                <div class="mb-3">
                    <input name="password" type="password" class="form-control form-control-lg" placeholder="Parol" required>
                </div>
                <div class="mb-4">
                    <select name="role" class="form-select form-select-lg">
                        <option value="student">👨‍🎓 Talaba</option>
                        <option value="teacher">👨‍🏫 O'qituvchi</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary w-100 btn-lg">Ro'yxatdan o'tish</button>
            </form>
            <p class="text-center mt-4">
                <a href="/login/" class="text-info text-decoration-none">Allaqachon akkaunt bormi? Tizimga kirish</a>
            </p>
        </div>
    </body>
    </html>
    """)


# ===================== LOGIN - ZAMONAVIY DIZAYN =====================
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        user = authenticate(username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            if user.role == "admin":
                return redirect("/admin-panel/")
            elif user.role == "teacher":
                return redirect("/create/")
            else:
                return redirect("/test/")
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
            body {
                background: linear-gradient(135deg, #0f172a 0%, #1e2937 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .card {
                background: rgba(255, 255, 255, 0.09);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 24px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            }
        </style>
    </head>
    <body>
        <div class="card p-5" style="width: 440px;">
            <div class="text-center mb-4">
                <h2>🔑 Tizimga kirish</h2>
                <p class="text-light">Intellektual test baholash tizimi</p>
            </div>
            <form method="post">
                <div class="mb-3">
                    <input name="username" class="form-control form-control-lg" placeholder="Username" required>
                </div>
                <div class="mb-3">
                    <input name="password" type="password" class="form-control form-control-lg" placeholder="Parol" required>
                </div>
                <button type="submit" class="btn btn-success w-100 btn-lg">Kirish</button>
            </form>
            <p class="text-center mt-4">
                <a href="/register/" class="text-info text-decoration-none">Ro'yxatdan o'tish</a>
            </p>
        </div>
    </body>
    </html>
    """)


# ===================== LOGOUT =====================
def logout_view(request):
    logout(request)
    return redirect("/login/")


# ===================== TALABA - TEST TOPSHIRISH (Asosiy imtihon bo'limi) =====================
@csrf_exempt
@login_required
def take_test(request):
    test = Test.objects.last()
    if not test:
        return HttpResponse("<h2 class='text-center mt-5 text-white'>Hozircha test mavjud emas</h2>")

    questions = test.questions.all()

    if request.method == "POST":
        total_score = 0
        for q in questions:
            student_ans = request.POST.get(str(q.id), "").strip()
            if q.question_type in ['mcq', 'truefalse']:
                if student_ans.lower() == q.correct_answer.lower():
                    total_score += 100
            else:
                total_score += grade_answer(student_ans, q.correct_answer)

        final_score = round(total_score / len(questions), 2)
        Result.objects.create(test=test, user=request.user, score=final_score)

        return HttpResponse(f"""
        <div class="container mt-5 text-center">
            <div class="card p-5 bg-dark mx-auto" style="max-width: 700px;">
                <h1 class="display-3 text-success">🎉 Natijangiz: <b>{final_score}%</b></h1>
                <p class="lead mt-3">Test avtomatik baholandi.<br>
                Yopiq savollar — 100% aniqlikda, ochiq savollar — NLP yordamida.</p>
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
        <style>
            body {{ background: #0f172a; color: white; }}
            .question-card {{ background: #1e2937; border: 1px solid #334155; }}
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <h2 class="text-center mb-5 text-light">{test.title}</h2>
            <form method="post">
                {''.join(f'''
                <div class="question-card card mb-4 p-4">
                    <h5 class="mb-3">{q.text}</h5>
                    <small class="text-info">{"Yopiq savol (100% aniq baholanadi)" if q.question_type in ["mcq", "truefalse"] else "Ochiq savol (NLP bilan baholanadi)"}</small>
                    <input name="{q.id}" class="form-control mt-3" placeholder="Javobingizni yozing..." required>
                </div>
                ''' for q in questions)}
                <button type="submit" class="btn btn-success btn-lg w-100 py-3">Testni yakunlash va natijani ko'rish</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


# ===================== O'QITUVCHI - TEST YARATISH =====================
@csrf_exempt
@login_required
def create_test(request):
    if request.method == "POST":
        title = request.POST.get("title")
        if not title:
            return HttpResponse("Test nomi majburiy!")

        test = Test.objects.create(title=title, teacher=request.user)
        return HttpResponse(f"""
        <div class="container mt-5 text-center">
            <h2 class="text-success">✅ Test muvaffaqiyatli yaratildi: {title}</h2>
            <p>Savollar qo'shishni davom ettirishingiz mumkin.</p>
            <a href="/create/" class="btn btn-primary btn-lg mt-4">Yana test yaratish</a>
            <a href="/test/" class="btn btn-success btn-lg mt-4">Test topshirish bo'limiga</a>
        </div>
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
            <form method="post" class="card p-4 bg-dark mt-4" style="max-width: 600px; margin: 0 auto;">
                <input name="title" class="form-control form-control-lg mb-4" placeholder="Test nomi (masalan: Matematika - 1-chorak)" required>
                <button type="submit" class="btn btn-primary btn-lg w-100">Testni yaratish</button>
            </form>
        </div>
    </body>
    </html>
    """)


# ===================== QOLGAN SAHIFALAR =====================
@login_required
def admin_panel(request):
    return HttpResponse("<h2>Admin Panel</h2>")

def create_admin(request):
    if not CustomUser.objects.filter(username="admin").exists():
        CustomUser.objects.create_superuser(username="admin", password="1234", role="admin")
        return HttpResponse("Admin yaratildi!<br>Username: admin<br>Parol: 1234")
    return HttpResponse("Admin allaqachon mavjud")

@login_required
def users_list(request):
    return HttpResponse("<h2>Foydalanuvchilar ro'yxati</h2>")

@login_required
def results_list(request):
    return HttpResponse("<h2>Natijalar ro'yxati</h2>")

@login_required
def stats_view(request):
    return HttpResponse("<h2>Statistika sahifasi (keyinroq grafiklar qo'shamiz)</h2>")
