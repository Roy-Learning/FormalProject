import json
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.core.files.base import ContentFile
import base64
import uuid

import pandas as pd

from components.models import (
    Employee,
    User,
    Matirial,
    WareHousing,
    Out,
    Summary,
)

# Create your views here.


# 登入接口 (获取前端传来的用户名和密码，与数据库用户名相同的进行密码校验，匹配则返回success和id，否则返回error和message)
class UserLogin(View):
    def get(self, request):
        data = json.loads(request.body)
        try:
            user = User.objects.get(username=data.get("username"))
            if user.password == data.get("password"):
                return JsonResponse({"message": "success", "id": user.id})
            else:
                return JsonResponse({"message": "error", "message": "密码错误"})
        except User.DoesNotExist:
            return JsonResponse({"message": "error", "message": "用户不存在"})


# 员工信息查询接口 (获取所有员工信息，转为字典，添加到employee_list中，返回employee_list)
class EmployeeSearch(View):
    def get(self, request):
        employees = Employee.objects.all()
        employee_list = []

        gender_mapping = {
            "M": "男",
            "F": "女",
        }

        department_mapping = {
            "SRC": "采购部门",
            "PRD": "生产部门",
            "MTD": "维护部门",
            "SALE": "销售部门",
            "QA": "质量保证部门",
        }

        position_mapping = {
            "C": "总监",
            "M": "经理",
            "E": "工程师",
            "S": "员工",
        }

        for employee in employees:
            employee_dict = model_to_dict(employee)
            employee_dict["gender"] = gender_mapping.get(
                employee_dict["gender"], employee_dict["gender"]
            )
            employee_dict["department"] = department_mapping.get(
                employee_dict["department"], employee_dict["department"]
            )
            employee_dict["position"] = position_mapping.get(
                employee_dict["position"], employee_dict["position"]
            )
            employee_list.append(employee_dict)
        return JsonResponse(employee_list, safe=False)


# 员工信息更新接口 (获取前端传来的json数据，根据员工id更新员工信息，返回更新成功的信息；如果员工不存在，则添加员工信息；如果出现其他错误，返回错误信息)
class EmployeeUpdate(View):
    def post(self, request):
        # 获取前端传来的json数据
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]  # 如果data是一个列表，取第一个元素
        # 获取员工信息
        id = data.get("id")
        employee_id = data.get("employee_id")
        name = data.get("name")
        age = data.get("age")
        gender = data.get("gender")
        department = data.get("department")
        position = data.get("position")
        # 根据员工id更新员工信息，返回更新成功的信息
        # 如果员工不存在，则添加员工信息
        # 如果出现其他错误，返回错误信息
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            employee.name = name
            employee.age = age
            employee.gender = gender
            employee.department = department
            employee.position = position
            employee.save()
            return JsonResponse({"message": "员工信息更新成功"})
        except Employee.DoesNotExist:
            employee = Employee(
                employee_id=employee_id,
                name=name,
                age=age,
                gender=gender,
                department=department,
                position=position,
            )
            employee.save()
            return JsonResponse({"message": "员工信息添加成功"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 员工信息删除接口 (获取前端传来的json数据，根据员工id删除员工信息，返回删除成功的信息；如果员工不存在，返回员工信息不存在；如果出现其他错误，返回错误信息)
class EmployeeDelete(View):
    def post(self, request):
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]  # 如果data是一个列表，取第一个元素
        id = data.get("id")
        employee_id = data.get("employee_id")
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            employee.delete()
            return JsonResponse({"message": "员工信息删除成功"})
        except Employee.DoesNotExist:
            return JsonResponse({"message": "员工信息不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 员工信息导入接口 (获取前端传来的json数据，遍历数据，添加员工信息；如果出现其他错误，返回错误信息)
# TODO: 未完成
class EmployeeImport(View):
    def post(self, request):
        excel_file = request.FILES["file"]
        data = pd.read_excel(excel_file, engine="openpyxl")

        field_mapping = {
            "工号": "employee_id",
            "姓名": "name",
            "年龄": "age",
            "性别": "gender",
            "部门": "department",
            "职位": "position",
        }

        for index, row in data.iterrows():
            mapped_row = {
                field_mapping[key]: value
                for key, value in row.to_dict().items()
                if key in field_mapping
            }

            employee, created = Employee.objects.get_or_create(
                employee_id=mapped_row["employee_id"],
                defaults={
                    "name": mapped_row["name"],
                    "age": mapped_row["age"],
                    "gender": mapped_row["gender"],
                    "department": mapped_row["department"],
                    "position": mapped_row["position"],
                },
            )

            if not created:
                employee.name = mapped_row["name"]
                employee.age = mapped_row["age"]
                employee.gender = mapped_row["gender"]
                employee.department = mapped_row["department"]
                employee.position = mapped_row["position"]
                employee.save()

        return JsonResponse({"message": "Excel file has been processed successfully."})


# 原料检测添加接口 (获取前端传来的json数据，添加原料信息；如果出现其他错误，返回错误信息)
class MatirialAdd(View):
    def post(self, request):
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]  # 如果data是一个列表，取第一个元素
        # 获取原料信息
        id = data.get("id")
        matirial_id = data.get("matirial_id")
        purchase_date = data.get("purchase_date")
        matirail_Qualify = data.get("matirail_Qualify")
        matriaial_QAid = data.get("matriaial_QAid")
        message = data.get("message")
        department = data.get("department")
        read = "False"
        try:
            matirial = Matirial(
                id=id,
                matirial_id=matirial_id,
                purchase_date=purchase_date,
                matirail_Qualify=matirail_Qualify,
                matriaial_QAid=matriaial_QAid,
                message=message,
                department=department,
                read=read,
            )
            matirial.save()
            return JsonResponse({"message": "原料信息添加成功"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 成品入库检测添加接口 (获取前端传来的json数据，添加成品入库信息；如果出现其他错误，返回错误信息)
class WareHousingAdd(View):
    def post(self, request):
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]  # 如果data是一个列表，取第一个元素
        # 获取成品入库信息
        id = data.get("id")
        warhousing_id = data.get("warhousing_id")
        produce_date = data.get("produce_date")
        finish_date = data.get("finish_date")
        qualify = data.get("qualify")
        warehousing_QAid = data.get("warehousing_QAid")
        message = data.get("message")
        department = data.get("department")
        read = "False"
        # 添加成品入库信息
        try:
            warehousing = WareHousing(
                id=id,
                warhousing_id=warhousing_id,
                produce_date=produce_date,
                finish_date=finish_date,
                qualify=qualify,
                warehousing_QAid=warehousing_QAid,
                message=message,
                department=department,
                read=read,
            )
            warehousing.save()
            return JsonResponse({"message": "成品入库信息添加成功"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 成品出库检测添加接口 (获取前端传来的json数据，添加成品出库信息；如果出现其他错误，返回错误信息)
class OutAdd(View):
    def post(self, request):
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]  # 如果data是一个列表，取第一个元素
        # 获取成品出库信息
        id = data.get("id")
        out_id = data.get("out_id")
        out_date = data.get("out_date")
        out_QAid = data.get("out_QAid")
        message = data.get("message")
        department = data.get("department")
        read = "False"
        # 添加成品出库信息
        try:
            out = Out(
                id=id,
                out_id=out_id,
                out_date=out_date,
                out_QAid=out_QAid,
                message=message,
                department=department,
                read=read,
            )
            out.save()
            return JsonResponse({"message": "成品出库信息添加成功"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 待办事项查询接口 (获取所有待办事项信息，转为字典，添加到todo_list中，返回todo_list)
class TodoSearch(View):
    def get(self, request):
        # 部门为SRC的待办事项
        SRC_todo = []
        SRC_todo_matirial = Matirial.objects.filter(department="SRC")
        # 将SRC_todo_matirial中的数据转为字典，添加到SRC_todo中
        for matirial in SRC_todo_matirial:
            matirial_dict = model_to_dict(matirial)
            SRC_todo.append(matirial_dict)

        # 部门为PRD的待办事项
        PRD_todo = []
        PRD_todo_temp = []
        PRD_todo_matirial = Matirial.objects.filter(department="PRD")
        PRD_todo_warehousing = WareHousing.objects.filter(department="PRD")
        # 将PRD_todo_matirial和PRD_todo_warehousing中的数据转为字典，根据来源不同添加到PRD_todo中
        for matirial in PRD_todo_matirial:
            matirial_dict = model_to_dict(matirial)
            PRD_todo_temp.append(matirial_dict)
        PRD_todo.append(PRD_todo_temp)
        PRD_todo_temp = []
        for matirial in PRD_todo_warehousing:
            matirial_dict = model_to_dict(matirial)
            PRD_todo_temp.append(matirial_dict)
        PRD_todo.append(PRD_todo_temp)

        # 部门为MTD的待办事项
        MTD_todo = []
        MTD_todo_temp = []
        MTD_todo_warehousing = WareHousing.objects.filter(department="MTD")
        MTD_todo_out = Out.objects.filter(department="MTD")
        # 将MTD_todo_warehousing和MTD_todo_out中的数据转为字典，根据来源不同添加到MTD_todo中
        for matirial in MTD_todo_warehousing:
            matirial_dict = model_to_dict(matirial)
            MTD_todo_temp.append(matirial_dict)
        MTD_todo.append(MTD_todo_temp)
        MTD_todo_temp = []
        for matirial in MTD_todo_out:
            matirial_dict = model_to_dict(matirial)
            MTD_todo_temp.append(matirial_dict)
        MTD_todo.append(MTD_todo_temp)

        # 部门为SALE的待办事项
        SALE_todo = []
        SALE_todo_temp = []
        SALE_todo_warehousing = WareHousing.objects.filter(department="SALE")
        SALE_todo_out = Out.objects.filter(department="SALE")
        # 将SALE_todo_warehousing和SALE_todo_out中的数据转为字典，根据来源不同添加到SALE_todo中
        for matirial in SALE_todo_warehousing:
            matirial_dict = model_to_dict(matirial)
            SALE_todo_temp.append(matirial_dict)
        SALE_todo.append(SALE_todo_temp)
        SALE_todo_temp = []
        for matirial in SALE_todo_out:
            matirial_dict = model_to_dict(matirial)
            SALE_todo_temp.append(matirial_dict)
        SALE_todo.append(SALE_todo_temp)

        return JsonResponse(
            {"SRC": SRC_todo, "PRD": PRD_todo, "MTD": MTD_todo, "SALE": SALE_todo},
            safe=False,
        )


# 更新待办事项接口（获取前端传来的json数据，根据部门更新对应的read状态，返回更新成功的信息；如果出现其他错误，返回错误信息）
class TodoUpdate(View):
    def post(self, request):
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]
        department = data.get("department")
        try:
            # 根据部门更新对应的read状态
            # 将所有待办事项的read状态更新为True
            if department == "SRC":
                matirials = Matirial.objects.filter(department="SRC")
                for matirial in matirials:
                    matirial.read = True
                    matirial.save()
            elif department == "PRD":
                matirials = Matirial.objects.filter(department="PRD")
                for matirial in matirials:
                    matirial.read = True
                    matirial.save()
                wareHousings = WareHousing.objects.filter(department="PRD")
                for warehousing in wareHousings:
                    warehousing.read = True
                    warehousing.save()
            elif department == "MTD":
                warehousings = WareHousing.objects.filter(department="MTD")
                for warehousing in warehousings:
                    warehousing.read = True
                    warehousing.save()
                outs = Out.objects.filter(department="MTD")
                for out in outs:
                    out.read = True
                    out.save()
            elif department == "SALE":
                warehousings = WareHousing.objects.filter(department="SALE")
                for warehousing in warehousings:
                    warehousing.read = True
                    warehousing.save()
                outs = Out.objects.filter(department="SALE")
                for out in outs:
                    out.read = True
                    out.save()
            return JsonResponse({"message": "success"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 事务汇总查询接口（获取所有事务汇总信息，转为字典，添加到summary_list中，返回summary_list）
class SummarySearch(View):
    def get(self, request):
        summarys = Summary.objects.all()
        summary_list = []
        for summary in summarys:
            summary_dict = model_to_dict(summary)
            summary_list.append(summary_dict)
        return JsonResponse(summary_list, safe=False)


# 事务汇总更新接口（获取前端传来的json数据，根据事务id更新事务信息，返回更新成功的信息；如果事务不存在，则添加事务信息；如果出现其他错误，返回错误信息）
class SummaryUpdate(View):
    def post(self, request):
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]
        id = data.get("id")
        date = data.get("date")
        message = data.get("message")
        try:
            summary = Summary.objects.get(id=id)
            summary = Summary(
                date=date,
                message=message,
            )
            summary.save()
            return JsonResponse({"message": "事务信息更新成功"})
        except Summary.DoesNotExist:
            summary = Summary(id=id, date=date, message=message)
            summary.save()
            return JsonResponse({"message": "事务信息添加成功"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 事务汇总删除接口（获取前端传来的json数据，根据事务id删除事务信息，返回删除成功的信息；如果事务不存在，返回事务信息不存在；如果出现其他错误，返回错误信息）
class SummaryDelete(View):
    def post(self, request):
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]
        id = data.get("id")
        try:
            summary = Summary.objects.get(id=id)
            summary.delete()
            return JsonResponse({"message": "事务信息删除成功"})
        except Summary.DoesNotExist:
            return JsonResponse({"message": "事务信息不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


# 用户信息查询接口（获取所有用户信息，转为字典，添加到user_list中，返回user_list）
class UserSearch(View):
    def get(self, request):
        users = User.objects.all()
        user_list = []
        for user in users:
            user_dict = model_to_dict(user)
            if user.avatar:
                user_dict["avatar"] = request.build_absolute_uri(user.avatar.url)
            else:
                user_dict["avatar"] = ""
            user_list.append(user_dict)
        return JsonResponse(user_list, safe=False)


# 用户信息更新接口（获取前端传来的json数据，根据用户id更新用户信息，返回更新成功的信息；如果用户不存在，则提醒；如果出现其他错误，返回错误信息）
class UserUpdate(View):
    def post(self, request):
        data = json.loads(request.body)
        if isinstance(data, list):
            data = data[0]
        id = data.get("id")
        username = data.get("username")
        password = data.get("password")
        avatar = data.get("avatar")
        # 如果avatar是一个列表，取第一个元素
        if isinstance(avatar, list) and avatar:
            avatar = avatar[0]
        # 如果avatar是一个字符串，转为图片文件
        if avatar:
            format, imgstr = avatar.split(";base64,")
            ext = format.split("/")[-1]
            avatar_URL = ContentFile(
                base64.b64decode(imgstr), name=str(uuid.uuid4())[:12] + "." + ext
            )
        try:
            user = User.objects.get(id=id)
            user.username = username
            user.password = password
            user.avatar = avatar_URL
            user.save()
            return JsonResponse({"message": "用户信息更新成功"})
        except User.DoesNotExist:
            # 可在此处添加新用户信息
            return JsonResponse({"message": "用户不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
