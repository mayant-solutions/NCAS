import datetime
import uuid as uuid
from time import timezone

from django.core.exceptions import ValidationError
from django.utils.datetime_safe import date
from django.utils.timezone import now

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxLengthValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Course(models.Model):
    name = models.CharField('Name', max_length=10)
    hod = models.CharField('HOD', max_length=20)

    def __str__(self):
        return self.name


class Tutor(models.Model):
    def validate(x):
        if len(str(x)) != 10:
            raise ValidationError("Mobile number must be 10 digit number")
    detail = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=100)
    ph_no = models.IntegerField('Contact No', validators=[validate])

    def __str__(self):
        return self.name


class Student(models.Model):
    def validate(x):
        if len(str(x)) != 10:
            raise ValidationError("Mobile number must be 10 digit number")

    details = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField('Name', max_length=100)
    add_ress = models.CharField('Address', max_length=1000)
    phno = models.IntegerField('Contact No', validators=[validate], null=True)
    adm_no = models.IntegerField('Admission No', validators=[MinValueValidator(1), MaxValueValidator(1000)])
    reg_no = models.IntegerField('Reg No', primary_key=True)
    course = models.ForeignKey(Course, verbose_name='Course', on_delete=models.PROTECT)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, verbose_name='Tutor')

    def __str__(self):
        return self.name


class Subject(models.Model):
    ch = ((1, 'Semester 1'),
          (2, 'Semester 2'),
          (3, 'Semester 3'),
          (4, 'Semester 4'),
          (5, 'Semester 5'),
          (6, 'Semester 6'))
    name = models.CharField('Name', max_length=20)
    course = models.ForeignKey(Course, verbose_name='Course', on_delete=models.CASCADE, blank=False)
    sem = models.IntegerField('Sem', choices=ch, default=0)

    def __str__(self):
        return self.name


class Mark(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    student = models.ForeignKey(Student, verbose_name='Student', on_delete=models.CASCADE)
    sub = models.ForeignKey(Subject, verbose_name='Subject', on_delete=models.CASCADE)
    s_mark1 = models.IntegerField('First Internal mark', validators=[MaxValueValidator(50), MinValueValidator(0)],
                                  blank=True)
    s_mark2 = models.IntegerField('Second Internal mark', validators=[MaxValueValidator(50), MinValueValidator(0)],
                                  blank=True)
    assmnt_mark1 = models.IntegerField('First Assignment mark', validators=[MaxValueValidator(50), MinValueValidator(0)],
                                       blank=True)
    assmnt_mark2 = models.IntegerField('Second Assignment mark', validators=[MaxValueValidator(50), MinValueValidator(0)],
                                       blank=True)
    attndnc_mark = models.IntegerField('Attendance mark', validators=[MaxValueValidator(50), MinValueValidator(0)],
                                       blank=True)

    def __str__(self):
        return self.sub.name


class Assignment(models.Model):
    topic = models.CharField('Topic', max_length=200)
    descrip = models.TextField('Details', max_length=1000)
    date_publish = models.DateTimeField('Date of published', default=now)
    sub = models.ForeignKey(Subject, verbose_name='Subject', on_delete=models.CASCADE)
    last_date = models.DateField('Last date for submit')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, verbose_name='Tutor')
    file = models.FileField(upload_to='assignments/{}/'.format(tutor.name), default='noimg.png')

    def __str__(self):
        return self.topic


class Notification(models.Model):
    topic = models.CharField('Topic', max_length=200)
    date_of_published = models.DateTimeField('Date of published', default=now)
    descrip = models.TextField('Details', max_length=1000)
    fileupload = models.FileField(upload_to='notifications/', default='noimg.png')

    def __str__(self):
        return self.topic


@receiver(post_save, sender=Student, dispatch_uid="create marks")
def update_stock(sender, instance, **kwargs):
    lists = instance.course.subject_set.all()
    for i in lists:
        obj = Mark()
        obj.student = instance
        obj.sub = i
        obj.s_mark1 = 0
        obj.s_mark2 = 0
        obj.save()
