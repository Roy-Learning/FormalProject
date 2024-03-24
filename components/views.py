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
                return JsonResponse(
                    {
                        "message": "success",
                        "success": True,
                        "id": user.id,
                        "avatar": user.avatar.url if user.avatar else None,
                    }
                )
            else:
                # 如果 User 对象的密码与请求中的密码不同
                # 返回一个 JsonResponse，包含 "message": "error" 和 "message": "密码错误"
                return JsonResponse(
                    {
                        "message": "密码错误",
                        "success": False,
                    }
                )
        # 如果 User.DoesNotExist 异常被引发（即没有找到用户名为 username 的 User 对象）
        except User.DoesNotExist:
            # 返回一个 JsonResponse，包含 "message": "error" 和 "message": "用户不存在"
            return JsonResponse(
                {
                    "message": "用户不存在",
                    "success": False,
                }
            )


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
        "QA": "质检部门",
    }

    position_mapping = {
        "C": "总监",
        "M": "经理",
        "E": "工程师",
        "T": "技术员",
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
        "质检部门": "QA",
    }
    position_mapping = {
        "总监": "C",
        "经理": "M",
        "工程师": "E",
        "技术员": "T",
        "员工": "S",
    }

    # 如果输入是字典，进行字段映射
    if isinstance(data, dict):
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
    # 如果输入是字符串，尝试在所有的映射中查找这个字符串
    elif isinstance(data, str):
        return (
            gender_mapping.get(data)
            or department_mapping.get(data)
            or position_mapping.get(data)
            or data
        )
    else:
        raise ValueError("输入数据类型不正确，应为字典或字符串")


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
            return JsonResponse({"message": "数据错误", "success": False}, status=200)
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
            return JsonResponse({"message": "员工信息更新成功", "success": True})
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
            return JsonResponse({"message": "员工信息添加成功", "success": True})
        except Exception as e:
            # 如果发生其他异常，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": str(e), "success": False}, status=200)


# 定义一个名为 EmployeeDelete 的视图类，继承自 View
class EmployeeDelete(View):
    # 定义 post 方法，接收一个 request 参数
    def post(self, request):
        # 尝试从请求体中获取 JSON 数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # 如果获取失败，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": "数据错误", "success": False}, status=200)
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
            return JsonResponse({"message": "员工信息删除成功", "success": True})
        except Employee.DoesNotExist:
            # 如果 Employee.DoesNotExist 异常被引发（即没有找到 id 为 id 的 Employee 对象）
            # 返回 JsonResponse，包含错误信息
            return JsonResponse(
                {"message": "员工信息不存在", "success": False}, status=200
            )
        except Exception as e:
            # 如果发生其他异常，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": str(e), "success": False}, status=200)


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
        return JsonResponse({"message": "导入成功", "success": True})


# 定义一个名为 MatirialAdd 的视图类，继承自 View
class MatirialAdd(View):
    # 定义 post 方法，接收一个 request 参数
    def post(self, request):
        # 尝试从请求体中获取 JSON 数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # 如果获取失败，返回 JsonResponse，包含错误信息
            return JsonResponse({"message": "数据错误", "success": False}, status=200)
        # 如果 data 是一个列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 反向映射字段
        mapped_fields = reverse_map_fields(data)
        # 初始化 read 为 "False"
        read = "False"
        try:
            # 创建一个新的 Matirial 对象
            matirial = Matirial(
                matirial_id=mapped_fields["matirial_id"],
                purchase_date=mapped_fields["purchase_date"],
                matirail_Qualify=mapped_fields["matirail_Qualify"],
                matirail_QAid=mapped_fields["matirail_QAid"],
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
            return JsonResponse({"message": str(e), "success": False}, status=200)


# WareHousingAdd视图类用于处理成品入库的添加请求
class WareHousingAdd(View):
    # post方法用于处理POST请求，添加成品入库信息
    def post(self, request):
        # 尝试从请求体中解析JSON数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # 如果解析失败，返回错误信息
            return JsonResponse({"message": "数据错误", "success": False}, status=200)
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
            return JsonResponse({"message": str(e), "success": False}, status=200)


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
            return JsonResponse({"message": str(e), "success": False}, status=200)


# 定义一个名为TodoSearch的类，它继承自View类
class TodoSearch(View):
    def get(self, request):
        # 获取所有的待办事项
        SRC_todo_matirial = Matirial.objects.filter(department="SRC")
        PRD_todo_matirial = Matirial.objects.filter(department="PRD")
        PRD_todo_warehousing = WareHousing.objects.filter(department="PRD")
        MTD_todo_warehousing = WareHousing.objects.filter(department="MTD")
        MTD_todo_out = Out.objects.filter(department="MTD")
        SALE_todo_warehousing = WareHousing.objects.filter(department="SALE")
        SALE_todo_out = Out.objects.filter(department="SALE")
        QA_todo_matirial = Matirial.objects.filter(department="QA")
        QA_todo_warehousing = WareHousing.objects.filter(department="QA")
        QA_todo_out = Out.objects.filter(department="QA")

        # 初始化待办事项列表
        SRC_todo = []
        PRD_todo = []
        MTD_todo = []
        SALE_todo = []
        QA_todo = []

        # 将待办事项添加到相应的列表中
        for matirial in SRC_todo_matirial:
            matirial_dict = model_to_dict(matirial)
            SRC_todo.append(matirial_dict)

        for matirial in PRD_todo_matirial:
            matirial_dict = model_to_dict(matirial)
            PRD_todo.append(matirial_dict)

        for warehousing in PRD_todo_warehousing:
            warehousing_dict = model_to_dict(warehousing)
            PRD_todo.append(warehousing_dict)

        for warehousing in MTD_todo_warehousing:
            warehousing_dict = model_to_dict(warehousing)
            MTD_todo.append(warehousing_dict)

        for out in MTD_todo_out:
            out_dict = model_to_dict(out)
            MTD_todo.append(out_dict)

        for warehousing in SALE_todo_warehousing:
            warehousing_dict = model_to_dict(warehousing)
            SALE_todo.append(warehousing_dict)

        for out in SALE_todo_out:
            out_dict = model_to_dict(out)
            SALE_todo.append(out_dict)

        for matirial in QA_todo_matirial:
            matirial_dict = model_to_dict(matirial)
            QA_todo.append(matirial_dict)

        for warehousing in QA_todo_warehousing:
            warehousing_dict = model_to_dict(warehousing)
            QA_todo.append(warehousing_dict)

        for out in QA_todo_out:
            out_dict = model_to_dict(out)
            QA_todo.append(out_dict)

        # 返回待办事项列表
        return JsonResponse(
            {
                "SRC_todo": SRC_todo,
                "PRD_todo": PRD_todo,
                "MTD_todo": MTD_todo,
                "SALE_todo": SALE_todo,
                "QA_todo": QA_todo,
            }
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
            return JsonResponse({"message": "数据错误", "success": False}, status=200)
        # 如果数据是列表，取第一个元素
        if isinstance(data, list):
            data = data[0]
        # 从数据中获取部门信息
        department_temp = data.get("department")
        department = reverse_map_fields(department_temp)
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
            return JsonResponse({"message": "success", "success": True})
        # 如果执行过程中出现异常，返回异常信息
        except Exception as e:
            return JsonResponse({"message": str(e), "success": False}, status=200)


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
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "数据错误", "success": False}, status=200)

        if isinstance(data, list):
            data = data[0]

        id = data.get("id")
        date = data.get("date")
        message = data.get("message")

        if id:
            try:
                summary = Summary.objects.get(id=id)
                summary.date = date
                summary.message = message
                summary.save()
                return JsonResponse({"message": "事务信息更新成功", "success": True})
            except Summary.DoesNotExist:
                return JsonResponse(
                    {"message": "没有找到对应的事务", "success": False}, status=200
                )
            except Exception as e:
                return JsonResponse({"message": str(e), "success": False}, status=200)
        else:
            try:
                summary = Summary(date=date, message=message)
                summary.save()
                return JsonResponse({"message": "事务信息添加成功", "success": True})
            except Exception as e:
                return JsonResponse({"message": str(e), "success": False}, status=200)


# 定义一个删除事务汇总的类，继承自View
class SummaryDelete(View):
    # 定义post方法，接收前端传来的请求
    def post(self, request):
        # 尝试从请求体中解析json数据
        try:
            data = json.loads(request.body)
        # 如果解析失败，返回错误信息
        except json.JSONDecodeError:
            return JsonResponse({"message": "数据错误", "success": False}, status=200)
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
            return JsonResponse({"message": "事务信息删除成功", "success": True})
        # 如果事务不存在
        except Summary.DoesNotExist:
            # 返回错误信息
            return JsonResponse(
                {"message": "事务信息不存在", "success": False}, status=200
            )
        # 如果出现其他错误
        except Exception as e:
            # 返回错误信息
            return JsonResponse({"message": str(e), "success": False}, status=200)


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
            return JsonResponse({"error": "用户不存在", "success": False}, status=200)


class UserUpdate(View):
    def post(self, request):
        # 尝试从请求体中解析json数据
        try:
            data = json.loads(request.body)
        # 如果解析失败，返回错误信息
        except json.JSONDecodeError:
            return JsonResponse({"message": "数据错误", "success": False}, status=200)
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
            # 更新用户的用户名、密码
            user.username = username
            user.password = password
            # 如果avatar存在，更新用户的头像
            if avatar_URL:
                user.avatar = avatar_URL
            # 保存用户
            user.save()
            # 返回成功信息
            return JsonResponse(
                {
                    "message": "用户信息更新成功",
                    "success": True,
                    "avatar": user.avatar.url if user.avatar else None,
                }
            )
        # 如果用户不存在
        except User.DoesNotExist:
            # 可在此处添加新用户信息
            return JsonResponse({"message": "用户不存在", "success": False}, status=200)
        # 如果出现其他错误
        except Exception as e:
            # 返回错误信息
            return JsonResponse({"message": str(e), "success": False}, status=200)
