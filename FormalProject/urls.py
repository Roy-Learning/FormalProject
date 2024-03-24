"""
URL configuration for FormalProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from components.views import (
    UserLogin,
    EmployeeSearch,
    EmployeeUpdate,
    EmployeeDelete,
    EmployeeImport,
    MatirialAdd,
    WareHousingAdd,
    OutAdd,
    TodoSearch,
    TodoUpdate,
    SummarySearch,
    SummaryUpdate,
    SummaryDelete,
    UserSearch,
    UserUpdate,
    avatarUpdate,
)

urlpatterns = [
    # path("admin/", admin.site.urls),
    # 登入接口
    path("api/userinfo/", UserLogin.as_view()),  # 用户登入检查,GET
    # 员工信息接口
    path("api/employee_search/", EmployeeSearch.as_view()),  # 员工信息查询,GET
    path("api/employee_update/", EmployeeUpdate.as_view()),  # 员工信息更新,POST
    path("api/employee_delete/", EmployeeDelete.as_view()),  # 员工信息删除,POST
    path("api/employee_import/", EmployeeImport.as_view()),  # 员工信息导入,POST
    # 原料检测接口
    path("api/matirial_add/", MatirialAdd.as_view()),  # 原料检测添加,POST
    # 成品入库检测接口
    path("api/warehousing_add/", WareHousingAdd.as_view()),  # 成品入库检测添加,POST
    # 成品出库检测接口
    path("api/out_add/", OutAdd.as_view()),  # 成品出库检测添加,POST
    # 待办事项接口
    path("api/todo_search/", TodoSearch.as_view()),  # 待办事项查询,GET
    path("api/todo_update/", TodoUpdate.as_view()),  # 待办事项更新,POST
    # 事项汇总接口
    path("api/summary_search/", SummarySearch.as_view()),  # 事项汇总查询,GET
    path("api/summary_update/", SummaryUpdate.as_view()),  # 事项汇总更新,POST
    path("api/summary_delete/", SummaryDelete.as_view()),  # 事项汇总删除,POST
    # 个人信息接口
    path("api/userinfo_search/", UserSearch.as_view()),  # 用户信息查询,GET
    path("api/userinfo_update/", UserUpdate.as_view()),  # 用户信息更新,POST
    path("api/userinfo_avatar/", avatarUpdate.as_view()),  # 用户信息删除,POST
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
