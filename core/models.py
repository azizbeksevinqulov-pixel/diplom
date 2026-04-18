from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'O‘qituvchi'),
        ('student', 'Talaba'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

class Test(models.Model):
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tests')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Yopiq savol (Ko‘p variantli)'),
        ('truefalse', 'True/False'),
        ('open', 'Ochiq savol'),
    )
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES, default='open')
    correct_answer = models.TextField()           # To'g'ri javob
    options = models.TextField(blank=True, null=True)  # MCQ uchun variantlar (masalan: A) variant1|B) variant2)

    def __str__(self):
        return self.text[:70]

class Result(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}%"
