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
        <style>body { background: linear-gradient(135deg, #0f172a, #1e2937); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }</style>
    </head>
    <body>
        <div class="card p-5" style="width: 420px; background: rgba(255,255,255,0.1);">
            <h2 class="text-center mb-4">Ro'yxatdan o'tish</h2>
            <form method="post">
                <input name="username" class="form-control mb-3" placeholder="Username" required>
                <input name="password" type="password" class="form-control mb-3" placeholder="Parol" required>
                <select name="role" class="form-select mb-3">
                    <option value="student">Talaba</option>
                    <option value="teacher">O'qituvchi</option>
                </select>
                <button type="submit" class="btn btn-primary w-100">Ro'yxatdan o'tish</button>
            </form>
            <p class="text-center mt-3"><a href="/login/" class="text-info">Kirish</a></p>
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
        <style>body { background: linear-gradient(135deg, #0f172a, #1e2937); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }</style>
    </head>
    <body>
        <div class="card p-5" style="width: 420px; background: rgba(255,255,255,0.1);">
            <h2 class="text-center mb-4">Tizimga kirish</h2>
            <form method="post">
                <input name="username" class="form-control mb-3" placeholder="Username" required>
                <input name="password" type="password" class="form-control mb-3" placeholder="Parol" required>
                <button type="submit" class="btn btn-success w-100">Kirish</button>
            </form>
            <p class="text-center mt-3"><a href="/register/" class="text-info">Ro'yxatdan o'tish</a></p>
        </div>
    </body>
    </html>
    """)


# ===================== LOGOUT =====================
def logout_view(request):
    logout(request)
    return redirect("/login/")


# ===================== TEST TOPSHIRISH (Asosiy imtihon bo'limi) =====================
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
            <div class="card p-5 bg-dark mx-auto" style="max-width: 650px;">
                <h1 class="display-3 text-success">Natijangiz: {final_score}%</h1>
                <a href="/test/" class="btn btn-primary btn-lg mt-4">Yana topshirish</a>
                <a href="/logout/" class="btn btn-outline-light mt-4">Chiqish</a>
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
                    <h5>{q.text}</h5>
                    <input name="{q.id}" class="form-control mt-3" placeholder="Javobingiz..." required>
                </div>
                ''' for q in questions)}
                <button type="submit" class="btn btn-success btn-lg w-100">Natijani ko'rish</button>
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
        Test.objects.create(title=title, teacher=request.user)
        return HttpResponse(f"Test yaratildi: {title} ✅ <br><a href='/create/'>Yana yaratish</a>")

    return HttpResponse("""
    <h2>Test yaratish</h2>
    <form method="post">
        <input name="title" placeholder="Test nomi" required><br><br>
        <button type="submit">Yaratish</button>
    </form>
    """)


# ===================== QOLGAN SAHIFALAR =====================
@login_required
def admin_panel(request):
    return HttpResponse("<h2>Admin Panel</h2>")

def create_admin(request):
    if not CustomUser.objects.filter(username="admin").exists():
        CustomUser.objects.create_superuser(username="admin", password="1234", role="admin")
        return HttpResponse("Admin yaratildi!<br>Login: admin<br>Parol: 1234")
    return HttpResponse("Admin allaqachon mavjud")

@login_required
def users_list(request):
    return HttpResponse("<h2>Foydalanuvchilar</h2>")

@login_required
def results_list(request):
    return HttpResponse("<h2>Natijalar</h2>")

@login_required
def stats_view(request):
    return HttpResponse("<h2>Statistika</h2>")
