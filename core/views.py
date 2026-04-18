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

    # Oddiy chiroyli register sahifasi
    return HttpResponse("""
    <h2>Ro'yxatdan o'tish</h2>
    <form method="post">
        <input name="username" placeholder="Username" required><br><br>
        <input name="password" type="password" placeholder="Parol" required><br><br>
        <select name="role">
            <option value="student">Talaba</option>
            <option value="teacher">O'qituvchi</option>
        </select><br><br>
        <button type="submit">Ro'yxatdan o'tish</button>
    </form>
    <a href="/login/">Kirish</a>
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

    return HttpResponse("""
    <h2>Kirish</h2>
    <form method="post">
        <input name="username" placeholder="Username" required><br><br>
        <input name="password" type="password" placeholder="Parol" required><br><br>
        <button type="submit">Kirish</button>
    </form>
    <a href="/register/">Ro'yxatdan o'tish</a>
    """)


# Boshqa view lar (take_test, create_test va h.k.) ni keyinroq to'liq qilamiz.
# Hozircha oddiy versiyasi bilan sinab ko'ramiz.

def logout_view(request):
    logout(request)
    return redirect("/login/")


@login_required
def create_test(request):
    return HttpResponse("Test yaratish sahifasi (hozircha oddiy)")

@login_required
def take_test(request):
    return HttpResponse("Test topshirish sahifasi (hozircha oddiy)")

# Qolganlarni vaqtincha oddiy qoldiramiz
@login_required
def admin_panel(request):
    return HttpResponse("Admin Panel")

def create_admin(request):
    return HttpResponse("Admin yaratish")

@login_required
def users_list(request):
    return HttpResponse("Foydalanuvchilar")

@login_required
def results_list(request):
    return HttpResponse("Natijalar")

@login_required
def stats_view(request):
    return HttpResponse("Statistika")
