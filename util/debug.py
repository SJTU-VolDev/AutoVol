import os
import pandas as pd
import sys
sys.path.append(os.path.abspath('.')) 

from util.GlobalVar import GlobalVar
from util.models import Volunteer, Team
from config.config import 工作路径, 正式路径
from util.Input import splitTeamByPosition,handleStaff,handleFamily
from util.Init import Init

def TestassignLeftovers():
    """
    assignLeftovers()的测试代码
    """
    
    GlobalVar.team_info 
    for i in range(1,10):
        vol = Volunteer()
        vol.init_personal_info({"学号":i})
        vol.interview = "pass"
        GlobalVar.volunteer_info[i] = vol
        GlobalVar.team_info[str(i)] = Team()
        GlobalVar.team_info[str(i)].team_max_size = 2
        GlobalVar.team_info[str(i)].team_size = 2
        GlobalVar.team_info[str(i)].team_member = []
    for i in range(10):
        print(GlobalVar.team_info[str(i)].team_member)

def outputDebug():
    """
    输出志愿者的姓名、学号、是否通过到Excel中。
    """
    os.makedirs(os.path.join(工作路径,"debug"),exist_ok=True)
    data = {
        "姓名": [],
        "学号": [],
        "是否通过": []
    }
    for vol in GlobalVar.volunteer_info:
        data["姓名"].append(GlobalVar.volunteer_info[vol].personal_info["姓名"])
        data["学号"].append(vol)
        data["是否通过"].append(GlobalVar.volunteer_info[vol].interview)
    table = pd.DataFrame(data)
    table.to_excel(os.path.join(工作路径,"debug","当前志愿者信息.xlsx"),index=False)

def outputCPlist():
    """
    输出情侣信息到Excel中。
    """
    # 找到最长的列表长度
    max_length = max(len(cp) for cp in GlobalVar.cp_lists)
    # 使用嵌套列表推导式,将所有列表补齐为相同长度
    lists_padded = [cp + [None] * (max_length - len(cp)) for cp in GlobalVar.cp_lists]
    df = pd.DataFrame(lists_padded).astype(str)
    os.makedirs(os.path.join(工作路径,"debug"),exist_ok=True)
    df.to_excel(os.path.join(工作路径,"debug","情侣信息.xlsx"), index=False)
        
def outputTeamInfo(file_path: str):
    excel_writer = pd.ExcelWriter(file_path,mode="w")
    sheet_name = "小组信息"
    col_names = ["岗位","岗位类型", "小组","小组计划人数"]
    teams = []
    for _,team in GlobalVar.team_info.items():
        team_info = []
        team_info.append(team.position)
        team_info.append(team.position_type)
        team_info.append(team.team_id)
        team_info.append(team.team_max_size)
        teams.append(team_info)
    excel = pd.DataFrame(teams, columns= col_names)
    excel = excel.style.applymap(lambda _: 'text-align: center')
    excel.to_excel(excel_writer, sheet_name=sheet_name, index= False)
    excel_writer.close()

def outputEmptyTeamInfo():
    Init()
    print("开始读取岗位.xlsx并拆分小组")
    recruit_total = splitTeamByPosition(正式路径)
    print("总计需要招募：{:d} 名志愿者！".format(recruit_total))
    outputTeamInfo(os.path.join(工作路径,"debug","小组信息空表.xlsx"))

def outputStaffAndFamily():
    Init()
    print("开始读取内部.xlsx")
    handleStaff(正式路径)
    handleFamily(正式路径)
    outputDebug()

if __name__ == "__main__":
    Init()
    
    outputDebug()