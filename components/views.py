import json
from django.db import IntegrityError
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


# 定义一个名为 UserLogin 的视图类，继承自 View
class UserLogin(View):
    # 定义 get 方法，接收一个 request 参数
    def get(self, request):
        # 从请求中获取 "username" 参数
        username = request.GET.get("username")
        # 从请求中获取 "password" 参数
        password = request.GET.get("password")
        try:
            # 从数据库中获取用户名为 username 的 User 对象
            user = User.objects.get(username=username)
            # 如果 User 对象的密码与请求中的密码相同
            if user.password == password:
                # 返回一个 JsonResponse，包含 "message": "success" 和 "id": user.id
                return JsonResponse({"message": "success", "id": user.id})
            else:
                # 如果 User 对象的密码与请求中的密码不同
                # 返回一个 JsonResponse，包含 "message": "error" 和 "message": "密码错误"
                return JsonResponse({"message": "error", "message": "密码错误"})
        # 如果 User.DoesNotExist 异常被引发（即没有找到用户名为 username 的 User 对象）
        except User.DoesNotExist:
            # 返回一个 JsonResponse，包含 "message": "error" 和 "message": "用户不存在"
            return JsonResponse({"message": "error", "message": "用户不存在"})


# 映射字段
def map_fields(data):
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
    mapped_data = data.copy()  # 复制原始数据

    mapped_data.update(
        {
            "gender": gender_mapping.get(data.get("gender"), data.get("gender")),
            "department": department_mapping.get(
                data.get("department"), data.get("department")
            ),
            "position": position_mapping.get(
                data.get("position"), data.get("position")
            ),
        }
    )

    return mapped_data


def reverse_map_fields(data):
    gender_mapping = {
        "男": "M",
        "女": "F",
    }
    department_mapping = {
        "采购部门": "SRC",
        "生产部门": "PRD",
        "维护部门": "MTD",
        "销售部门": "SALE",
        "质量保证部门": "QA",
    }
    position_mapping = {
        "总监": "C",
        "经理": "M",
        "工程师": "E",
        "员工": "S",
    }

    mapped_data = data.copy()  # 复制原始数据

    mapped_data.update(
        {
            "gender": gender_mapping.get(data.get("gender"), data.get("gender")),
            "department": department_mapping.get(
                data.get("department"), data.get("department")
            ),
            "position": position_mapping.get(
                data.get("position"), data.get("position")
            ),
        }
    )

    return mapped_data


# 定义一个名为 EmployeeSearch 的视图类，继承自 View
class EmployeeSearch(View):
    # 定义 get 方法，接收一个 request 参数
    def get(self, request):
        # 从数据库中获取所有 Employee 对象
        employees = Employee.objects.all()
        # 初始化一个空列表，用于存储员工信息
        employee_list = []
        # 遍历所有 Employee 对象
        for employee in employees:
            # 将 Employee 对象转换为字典
            employee_dict = model_to_dict(employee)
            # 如果转换结果为 None，则跳过当前循环
            if employee_dict is None:
                continue
            # 映射字段
            mapped_fields = map_fields(employee_dict)
            # 更新员工字典
            employee_dict.update(mapped_fields)
            # 将员工字典添加到列表中
            employee_list.append(employee_dict)
        # 返回 JsonResponse，包含所有员工信息
        return JsonResponse(employee_list, safe=False)


# 定义一个名为 EmployeeUpdate 的视图类，继承自 View
class EmployeeUpdate(View):
    # 定义 post 方法，接收一个 request 参数
    def post(self, request):
        # 尝试从请求体中获取 JSON 数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # 如果获取失败，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果 data 是一个列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 反向映射字段
        mapped_fields = reverse_map_fields(data)
        # 从 data 中获取 "id" 字段
        id = data.get("id")
        try:
            # 从数据库中获取 id 为 id 的 Employee 对象
            employee = Employee.objects.get(id=id)
            # 更新 Employee 对象的各个字段
            employee.employee_id = mapped_fields["employee_id"]
            employee.name = mapped_fields["name"]
            employee.age = mapped_fields["age"]
            employee.gender = mapped_fields["gender"]
            employee.department = mapped_fields["department"]
            employee.position = mapped_fields["position"]
            # 保存 Employee 对象
            employee.save()
            # 返回 JsonResponse，包含成功信息
            return JsonResponse({"message": "员工信息更新成功"})
        except Employee.DoesNotExist:
            # 如果 Employee.DoesNotExist 异常被引发（即没有找到 id 为 id 的 Employee 对象）
            # 创建一个新的 Employee 对象
            employee = Employee(
                employee_id=mapped_fields["employee_id"],
                name=mapped_fields["name"],
                age=mapped_fields["age"],
                gender=mapped_fields["gender"],
                department=mapped_fields["department"],
                position=mapped_fields["position"],
            )
            # 保存 Employee 对象
            employee.save()
            # 返回 JsonResponse，包含成功信息
            return JsonResponse({"message": "员工信息添加成功"})
        except Exception as e:
            # 如果发生其他异常，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": str(e)}, status=200)


# 定义一个名为 EmployeeDelete 的视图类，继承自 View
class EmployeeDelete(View):
    # 定义 post 方法，接收一个 request 参数
    def post(self, request):
        # 尝试从请求体中获取 JSON 数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # 如果获取失败，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果 data 是一个列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 从 data 中获取 "id" 字段
        id = data.get("id")
        try:
            # 从数据库中获取 id 为 id 的 Employee 对象
            employee = Employee.objects.get(id=id)
            # 删除 Employee 对象
            employee.delete()
            # 返回 JsonResponse，包含成功信息
            return JsonResponse({"message": "员工信息删除成功"})
        except Employee.DoesNotExist:
            # 如果 Employee.DoesNotExist 异常被引发（即没有找到 id 为 id 的 Employee 对象）
            # 返回 JsonResponse，包含错误信息
            return JsonResponse({"message": "员工信息不存在"}, status=200)
        except Exception as e:
            # 如果发生其他异常，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": str(e)}, status=200)


# 定义一个名为 EmployeeImport 的视图类，继承自 View
class EmployeeImport(View):
    # 定义 post 方法，接收一个 request 参数
    def post(self, request):
        # 从请求中获取文件
        excel_file = request.FILES["file"]
        # 读取 Excel 文件
        data = pd.read_excel(excel_file, engine="openpyxl")
        # 定义字段映射
        field_mapping = {
            "工号": "employee_id",
            "姓名": "name",
            "年龄": "age",
            "性别": "gender",
            "部门": "department",
            "职位": "position",
        }
        # 遍历数据
        for index, row in data.iterrows():
            # 映射字段
            mapped_row = {
                field_mapping[key]: value
                for key, value in row.to_dict().items()
                if key in field_mapping
            }
            # 反向映射字段
            mapped_row = reverse_map_fields(mapped_row)
            # 获取或创建 Employee 对象
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
            # 如果 Employee 对象已存在，更新其字段
            if not created:
                employee.name = mapped_row["name"]
                employee.age = mapped_row["age"]
                employee.gender = mapped_row["gender"]
                employee.department = mapped_row["department"]
                employee.position = mapped_row["position"]
                # 保存 Employee 对象
                employee.save()
        # 返回 JsonResponse，包含成功信息
        return JsonResponse({"message": "Excel file has been processed successfully."})


# 定义一个名为 MatirialAdd 的视图类，继承自 View
class MatirialAdd(View):
    # 定义 post 方法，接收一个 request 参数
    def post(self, request):
        # 尝试从请求体中获取 JSON 数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # 如果获取失败，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果 data 是一个列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 反向映射字段
        mapped_fields = reverse_map_fields(data)
        # 从 data 中获取 "id" 字段
        id = data.get("id")
        # 初始化 read 为 "False"
        read = "False"
        try:
            # 创建一个新的 Matirial 对象
            matirial = Matirial(
                id=id,
                matirial_id=mapped_fields["matirial_id"],
                purchase_date=mapped_fields["purchase_date"],
                matirail_Qualify=mapped_fields["matirail_Qualify"],
                matriaial_QAid=mapped_fields["matriaial_QAid"],
                message=mapped_fields["message"],
                department=mapped_fields["department"],
                read=read,
            )
            # 保存 Matirial 对象
            matirial.save()
            # 返回 JsonResponse，包含成功信息
            return JsonResponse({"message": "原料信息添加成功", "success": True})
        except IntegrityError as e:
            # 如果 IntegrityError 异常被引发（即原料 ID 已存在）
            # 返回 JsonResponse，包含错误信息
            return JsonResponse(
                {"message": "原料ID信息已存在", "success": False}, status=200
            )
        except Exception as e:
            # 如果发生其他异常，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": str(e)}, status=200)


# WareHousingAdd视图类用于处理成品入库的添加请求
class WareHousingAdd(View):
    # post方法用于处理POST请求，添加成品入库信息
    def post(self, request):
        # 尝试从请求体中解析JSON数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # 如果解析失败，返回错误信息
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果data是一个列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 获取成品入库信息
        mapped_fields = reverse_map_fields(data)
        # 从data中获取id
        id = data.get("id")
        read = "False"
        # 尝试添加成品入库信息
        try:
            warehousing = WareHousing(
                id=id,
                warhousing_id=mapped_fields["warhousing_id"],
                produce_date=mapped_fields["produce_date"],
                finish_date=mapped_fields["finish_date"],
                qualify=mapped_fields["qualify"],
                warehousing_QAid=mapped_fields["warehousing_QAid"],
                message=mapped_fields["message"],
                department=mapped_fields["department"],
                read=read,
            )
            warehousing.save()
            return JsonResponse({"message": "成品入库信息添加成功", "success": True})
        except IntegrityError as e:
            # 如果成品入库ID已存在，返回错误信息
            return JsonResponse(
                {"message": "成品入库ID信息已存在", "success": False}, status=200
            )
        except Exception as e:
            # 如果出现其他错误，返回错误信息
            return JsonResponse({"message": str(e)}, status=200)


# OutAdd视图类用于处理成品出库的添加请求
class OutAdd(View):
    # post方法用于处理POST请求，添加成品出库信息
    def post(self, request):
        # 尝试从请求体中解析JSON数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # 如果解析失败，返回错误信息
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果data是一个列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 获取成品出库信息
        mapped_fields = reverse_map_fields(data)
        # 从data中获取id
        id = data.get("id")
        read = "False"
        # 尝试添加成品出库信息
        try:
            out = Out(
                id=id,
                out_id=mapped_fields["out_id"],
                out_date=mapped_fields["out_date"],
                out_qualify=mapped_fields["out_qualify"],
                out_QAid=mapped_fields["out_QAid"],
                message=mapped_fields["message"],
                department=mapped_fields["department"],
                read=read,
            )
            out.save()
            return JsonResponse({"message": "成品出库信息添加成功", "success": True})
        except IntegrityError as e:
            # 如果成品出库ID已存在，返回错误信息
            return JsonResponse(
                {"message": "成品出库ID信息已存在", "success": False}, status=200
            )
        except Exception as e:
            # 如果出现其他错误，返回错误信息
            return JsonResponse({"message": str(e)}, status=200)


# 定义一个名为TodoSearch的类，它继承自View类
class TodoSearch(View):
    # 定义一个名为get的方法，它接受两个参数：self和request
    def get(self, request):
        # 创建一个空列表SRC_todo，用于存储部门为SRC的待办事项
        SRC_todo = []
        # 从Matirial模型中筛选出部门为SRC的待办事项，并将结果赋值给SRC_todo_matirial
        SRC_todo_matirial = Matirial.objects.filter(department="SRC")
        # 遍历SRC_todo_matirial中的每一个待办事项
        for matirial in SRC_todo_matirial:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到SRC_todo列表中

        # 创建一个空列表PRD_todo，用于存储部门为PRD的待办事项
        PRD_todo = []
        # 创建一个空列表PRD_todo_temp，用于临时存储待办事项
        PRD_todo_temp = []
        # 从Matirial模型中筛选出部门为PRD的待办事项，并将结果赋值给PRD_todo_matirial
        PRD_todo_matirial = Matirial.objects.filter(department="PRD")
        # 从WareHousing模型中筛选出部门为PRD的待办事项，并将结果赋值给PRD_todo_warehousing
        PRD_todo_warehousing = WareHousing.objects.filter(department="PRD")
        # 遍历PRD_todo_matirial中的每一个待办事项
        for matirial in PRD_todo_matirial:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到PRD_todo_temp列表中
            PRD_todo_temp.append(matirial_dict)
        # 将PRD_todo_temp列表添加到PRD_todo列表中
        PRD_todo.append(PRD_todo_temp)
        # 清空PRD_todo_temp列表
        PRD_todo_temp = []
        # 遍历PRD_todo_warehousing中的每一个待办事项
        for matirial in PRD_todo_warehousing:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到PRD_todo_temp列表中
            PRD_todo_temp.append(matirial_dict)
        # 将PRD_todo_temp列表添加到PRD_todo列表中
        PRD_todo.append(PRD_todo_temp)

        # 创建一个空列表MTD_todo，用于存储部门为MTD的待办事项
        MTD_todo = []
        # 创建一个空列表MTD_todo_temp，用于临时存储待办事项
        MTD_todo_temp = []
        # 从WareHousing模型中筛选出部门为MTD的待办事项，并将结果赋值给MTD_todo_warehousing
        MTD_todo_warehousing = WareHousing.objects.filter(department="MTD")
        # 从Out模型中筛选出部门为MTD的待办事项，并将结果赋值给MTD_todo_out
        MTD_todo_out = Out.objects.filter(department="MTD")
        # 遍历MTD_todo_warehousing中的每一个待办事项
        for matirial in MTD_todo_warehousing:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到MTD_todo_temp列表中
            MTD_todo_temp.append(matirial_dict)
        # 将MTD_todo_temp列表添加到MTD_todo列表中
        MTD_todo.append(MTD_todo_temp)
        # 清空MTD_todo_temp列表
        MTD_todo_temp = []
        # 遍历MTD_todo_out中的每一个待办事项
        for matirial in MTD_todo_out:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到MTD_todo_temp列表中
            MTD_todo_temp.append(matirial_dict)
        # 将MTD_todo_temp列表添加到MTD_todo列表中
        MTD_todo.append(MTD_todo_temp)

        # 创建一个空列表SALE_todo，用于存储部门为SALE的待办事项
        SALE_todo = []
        # 创建一个空列表SALE_todo_temp，用于临时存储待办事项
        SALE_todo_temp = []
        # 从WareHousing模型中筛选出部门为SALE的待办事项，并将结果赋值给SALE_todo_warehousing
        SALE_todo_warehousing = WareHousing.objects.filter(department="SALE")
        # 从Out模型中筛选出部门为SALE的待办事项，并将结果赋值给SALE_todo_out
        SALE_todo_out = Out.objects.filter(department="SALE")
        # 遍历SALE_todo_warehousing中的每一个待办事项
        for matirial in SALE_todo_warehousing:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到SALE_todo_temp列表中
            SALE_todo_temp.append(matirial_dict)
        # 将SALE_todo_temp列表添加到SALE_todo列表中
        SALE_todo.append(SALE_todo_temp)
        # 清空SALE_todo_temp列表
        SALE_todo_temp = []
        # 遍历SALE_todo_out中的每一个待办事项
        for matirial in SALE_todo_out:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到SALE_todo_temp列表中
            SALE_todo_temp.append(matirial_dict)
        # 将SALE_todo_temp列表添加到SALE_todo列表中
        SALE_todo.append(SALE_todo_temp)

        # 创建一个空列表QA_todo，用于存储部门为QA的待办事项
        QA_todo = []
        # 创建一个空列表QA_todo_temp，用于临时存储待办事项
        QA_todo_temp = []
        # 从Matirial模型中筛选出部门为QA的待办事项，并将结果赋值给QA_todo_matirial
        QA_todo_matirial = Matirial.objects.filter(department="QA")
        # 从WareHousing模型中筛选出部门为QA的待办事项，并将结果赋值给QA_todo_warehousing
        QA_todo_warehousing = WareHousing.objects.filter(department="QA")
        # 从Out模型中筛选出部门为QA的待办事项，并将结果赋值给QA_todo_out
        QA_todo_out = Out.objects.filter(department="QA")
        # 遍历QA_todo_matirial中的每一个待办事项
        for matirial in QA_todo_matirial:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到QA_todo_temp列表中
            QA_todo_temp.append(matirial_dict)
        # 将QA_todo_temp列表添加到QA_todo列表中
        QA_todo.append(QA_todo_temp)
        # 清空QA_todo_temp列表
        QA_todo_temp = []
        # 遍历QA_todo_warehousing中的每一个待办事项
        for matirial in QA_todo_warehousing:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到QA_todo_temp列表中
            QA_todo_temp.append(matirial_dict)
        # 将QA_todo_temp列表添加到QA_todo列表中
        QA_todo.append(QA_todo_temp)
        # 清空QA_todo_temp列表
        QA_todo_temp = []
        # 遍历QA_todo_out中的每一个待办事项
        for matirial in QA_todo_out:
            # 使用model_to_dict函数将待办事项转换为字典，并将结果赋值给matirial_dict
            matirial_dict = model_to_dict(matirial)
            # 将matirial_dict添加到QA_todo_temp列表中
            QA_todo_temp.append(matirial_dict)
        # 将QA_todo_temp列表添加到QA_todo列表中
        QA_todo.append(QA_todo_temp)

        # 使用JsonResponse函数返回一个JSON响应，其中包含了各个部门的待办事项列表
        return JsonResponse(
            {
                "SRC": SRC_todo,
                "PRD": PRD_todo,
                "MTD": MTD_todo,
                "SALE": SALE_todo,
                "QA": QA_todo,
            },
            safe=False,
        )


# 定义一个更新待办事项的类，继承自View
class TodoUpdate(View):
    # 定义post方法，接收前端传来的请求
    def post(self, request):
        # 尝试从请求体中解析json数据
        try:
            data = json.loads(request.body)
        # 如果解析失败，返回错误信息
        except json.JSONDecodeError:
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果数据是列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 从数据中获取部门信息
        department = data.get("department")
        # 尝试执行以下操作
        try:
            # 如果部门是"SRC"
            if department == "SRC":
                # 获取所有"SRC"部门的待办事项
                matirials = Matirial.objects.filter(department="SRC")
                # 遍历待办事项，将read状态更新为True
                for matirial in matirials:
                    matirial.read = True
                    matirial.save()
            # 如果部门是"PRD"
            elif department == "PRD":
                # 获取所有"PRD"部门的待办事项
                matirials = Matirial.objects.filter(department="PRD")
                # 遍历待办事项，将read状态更新为True
                for matirial in matirials:
                    matirial.read = True
                    matirial.save()
                # 获取所有"PRD"部门的入库记录
                wareHousings = WareHousing.objects.filter(department="PRD")
                # 遍历入库记录，将read状态更新为True
                for warehousing in wareHousings:
                    warehousing.read = True
                    warehousing.save()
            # 如果部门是"MTD"
            elif department == "MTD":
                # 获取所有"MTD"部门的入库记录
                warehousings = WareHousing.objects.filter(department="MTD")
                # 遍历入库记录，将read状态更新为True
                for warehousing in warehousings:
                    warehousing.read = True
                    warehousing.save()
                # 获取所有"MTD"部门的出库记录
                outs = Out.objects.filter(department="MTD")
                # 遍历出库记录，将read状态更新为True
                for out in outs:
                    out.read = True
                    out.save()
            # 如果部门是"SALE"
            elif department == "SALE":
                # 获取所有"SALE"部门的入库记录
                warehousings = WareHousing.objects.filter(department="SALE")
                # 遍历入库记录，将read状态更新为True
                for warehousing in warehousings:
                    warehousing.read = True
                    warehousing.save()
                # 获取所有"SALE"部门的出库记录
                outs = Out.objects.filter(department="SALE")
                # 遍历出库记录，将read状态更新为True
                for out in outs:
                    out.read = True
                    out.save()
            # 如果部门是"QA"
            elif department == "QA":
                # 获取所有"QA"部门的待办事项
                matirials = Matirial.objects.filter(department="QA")
                # 遍历待办事项，将read状态更新为True
                for matirial in matirials:
                    matirial.read = True
                    matirial.save()
                # 获取所有"QA"部门的入库记录
                warehousings = WareHousing.objects.filter(department="QA")
                # 遍历入库记录，将read状态更新为True
                for warehousing in warehousings:
                    warehousing.read = True
                    warehousing.save()
                # 获取所有"QA"部门的出库记录
                outs = Out.objects.filter(department="QA")
                # 遍历出库记录，将read状态更新为True
                for out in outs:
                    out.read = True
                    out.save()
            # 所有操作成功后，返回成功信息
            return JsonResponse({"message": "success"})
        # 如果执行过程中出现异常，返回异常信息
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=200)


# 定义一个查询事务汇总的类，继承自View
class SummarySearch(View):
    # 定义get方法，接收前端传来的请求
    def get(self, request):
        # 获取所有的事务汇总信息
        summarys = Summary.objects.all()
        # 初始化一个列表，用于存放事务汇总信息
        summary_list = []
        # 遍历所有的事务汇总信息
        for summary in summarys:
            # 将事务汇总信息转为字典
            summary_dict = model_to_dict(summary)
            # 将字典添加到列表中
            summary_list.append(summary_dict)
        # 返回事务汇总信息列表
        return JsonResponse(summary_list, safe=False)


# 定义一个更新事务汇总的类，继承自View
class SummaryUpdate(View):
    # 定义post方法，接收前端传来的请求
    def post(self, request):
        # 尝试从请求体中解析json数据
        try:
            data = json.loads(request.body)
        # 如果解析失败，返回错误信息
        except json.JSONDecodeError:
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果数据是列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 从数据中获取事务id、日期和信息
        id = data.get("id")
        date = data.get("date")
        message = data.get("message")
        # 尝试执行以下操作
        try:
            # 根据id获取事务
            summary = Summary.objects.get(id=id)
            # 更新事务的日期和信息
            summary = Summary(
                date=date,
                message=message,
            )
            # 保存事务
            summary.save()
            # 返回成功信息
            return JsonResponse({"message": "事务信息更新成功"})
        # 如果事务不存在
        except Summary.DoesNotExist:
            # 创建新的事务
            summary = Summary(id=id, date=date, message=message)
            # 保存事务
            summary.save()
            # 返回成功信息
            return JsonResponse({"message": "事务信息添加成功"})
        # 如果出现其他错误
        except Exception as e:
            # 返回错误信息
            return JsonResponse({"message": str(e)}, status=200)


# 定义一个删除事务汇总的类，继承自View
class SummaryDelete(View):
    # 定义post方法，接收前端传来的请求
    def post(self, request):
        # 尝试从请求体中解析json数据
        try:
            data = json.loads(request.body)
        # 如果解析失败，返回错误信息
        except json.JSONDecodeError:
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果数据是列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 从数据中获取事务id
        id = data.get("id")
        # 尝试执行以下操作
        try:
            # 根据id获取事务
            summary = Summary.objects.get(id=id)
            # 删除事务
            summary.delete()
            # 返回成功信息
            return JsonResponse({"message": "事务信息删除成功"})
        # 如果事务不存在
        except Summary.DoesNotExist:
            # 返回错误信息
            return JsonResponse({"message": "事务信息不存在"}, status=200)
        # 如果出现其他错误
        except Exception as e:
            # 返回错误信息
            return JsonResponse({"message": str(e)}, status=200)


# 定义一个查询用户信息的类，继承自View
class UserSearch(View):
    # 定义get方法，接收前端传来的请求
    def get(self, request):
        # 从请求中获取用户id
        id = request.GET.get("id")
        # 尝试执行以下操作
        try:
            # 根据id获取用户
            user = User.objects.get(id=id)
            # 将用户信息转为字典
            user_dict = model_to_dict(user)
            # 如果用户有头像，获取头像的url
            if user.avatar:
                user_dict["avatar"] = request.build_absolute_uri(user.avatar.url)
            # 如果用户没有头像，设置头像为""
            else:
                user_dict["avatar"] = ""
            # 返回用户信息
            return JsonResponse(user_dict, safe=False)
        # 如果用户不存在
        except User.DoesNotExist:
            # 返回错误信息
            return JsonResponse({"error": "用户不存在"}, status=200)


# 定义一个更新用户信息的类，继承自View
class UserUpdate(View):
    # 定义post方法，接收前端传来的请求
    def post(self, request):
        # 尝试从请求体中解析json数据
        try:
            data = json.loads(request.body)
        # 如果解析失败，返回错误信息
        except json.JSONDecodeError:
            return JsonResponse({"message": "数据错误"}, status=200)
        # 如果数据是列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 从数据中获取用户id、用户名、密码和头像
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
        else:
            avatar_URL = None
        # 尝试执行以下操作
        try:
            # 根据id获取用户
            user = User.objects.get(id=id)
            # 更新用户的用户名、密码和头像
            user.username = username
            user.password = password
            user.avatar = avatar_URL
            # 保存用户
            user.save()
            # 返回成功信息
            return JsonResponse({"message": "用户信息更新成功"})
        # 如果用户不存在
        except User.DoesNotExist:
            # 可在此处添加新用户信息
            return JsonResponse({"message": "用户不存在"}, status=200)
        # 如果出现其他错误
        except Exception as e:
            # 返回错误信息
            return JsonResponse({"message": str(e)}, status=200)
