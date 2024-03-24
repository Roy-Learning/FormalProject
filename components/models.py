from django.db import models

# Create your models here.


# userInfoSettings
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, blank=False, null=False)
    password = models.CharField(max_length=100, blank=False, null=False)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    # email = models.EmailField()
    # phone = models.CharField(max_length=20)
    # role = models.CharField(
    #     max_length=100,
    #     choices=[
    #         ("admin", "admin"),
    #         ("user", "user"),
    #     ],
    # )
    # status = models.CharField(
    #     max_length=100,
    #     choices=[
    #         ("active", "active"),
    #         ("inactive", "inactive"),
    #     ],
    # )


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[("M", "Male"), ("F", "Female")])
    # department can only be one of the following: 'SRC', 'PRD', 'MTD', 'SALE', 'QA'
    department = models.CharField(
        max_length=100,
        choices=[
            ("SRC", "采购部门"),
            ("PRD", "生产部门"),
            ("MTD", "维修部门"),
            ("SALE", "销售部门"),
            ("QA", "质检部门"),
        ],
    )
    # position can only be one of the following: 'commissioner', 'manager', 'engineer', 'staff'
    position = models.CharField(
        max_length=100,
        choices=[
            ("C", "总监"),
            ("M", "经理"),
            ("E", "工程师"),
            ("T", "技术员"),
            ("S", "员工"),
        ],
    )


class Matirial(models.Model):
    id = models.AutoField(primary_key=True)
    matirial_id = models.CharField(max_length=20, unique=True)
    purchase_date = models.DateField()
    matirail_Qualify = models.CharField(max_length=50)
    matirail_QAid = models.CharField(max_length=40)
    message = models.CharField(max_length=100)
    department = models.CharField(max_length=20)
    read = models.BooleanField(default=False)


class WareHousing(models.Model):
    id = models.AutoField(primary_key=True)
    warhousing_id = models.CharField(max_length=20, unique=True)
    produce_date = models.DateField()
    finish_date = models.DateField()
    qualify = models.CharField(max_length=50)
    warehousing_QAid = models.CharField(max_length=20)
    message = models.CharField(max_length=100)
    department = models.CharField(max_length=20)
    read = models.BooleanField(default=False)


class Out(models.Model):
    id = models.AutoField(primary_key=True)
    out_id = models.CharField(max_length=20, unique=True)
    out_date = models.DateField()
    out_qualify = models.CharField(max_length=50)
    out_QAid = models.CharField(max_length=20)
    message = models.CharField(max_length=100)
    department = models.CharField(max_length=20)
    read = models.BooleanField(default=False)


class Summary(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    message = models.CharField(max_length=1024)
