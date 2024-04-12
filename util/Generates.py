import os
import pandas as pd
import sys
import jinja2
from util.handleCP import getCP
from util.GlobalVar import GlobalVar
from config.config import colors

def Generate(file_dir: str) -> None:
    """
    **对外接口**

    Args:
        file_dir(str): 生成文件的目录
    Returns:
        None
    """
    sys.stdout = GlobalVar.log_file
    print("开始导出总表...")
    getGroupColor()
    os.makedirs(file_dir, exist_ok=True)
    generateMain(file_dir)
    print("导出总表完成！")
    sys.stdout = GlobalVar.original_stdout

def getGroupColor():
    import matplotlib.pyplot as plt
    import numpy as np
    cmap = plt.cm.get_cmap('Set3')
    colors = cmap(np.arange(len(GlobalVar.group_lists)))
    index = 0
    for group in GlobalVar.group_lists:
        r = int(colors[index][0] * 255)
        g = int(colors[index][1] * 255)
        b = int(colors[index][2] * 255)
        color_code = f'#{r:02x}{g:02x}{b:02x}'
        GlobalVar.group_colors[group] = color_code
        index += 1
    return

def takeColors(row):
    # 按行着色
    id = row["学号"]
    if GlobalVar.volunteer_info[id].staff is not None:
        if GlobalVar.volunteer_info[id].staff.want_leader == True:
            return ['background-color: ' + colors["team_leader"]] * len(row)
        else:
            return ['background-color: ' + colors["staff"]] * len(row)
    if GlobalVar.volunteer_info[id].isviceleader is True:
        return ['background-color:' + colors["vice_leader"]] * len(row)
    if GlobalVar.volunteer_info[id].family is not None:
        return ['background-color: ' + colors["family"]] * len(row)
    if len(GlobalVar.volunteer_info[id].groups) > 0:
        return ['background-color: ' + GlobalVar.group_colors[GlobalVar.volunteer_info[id].groups[0]]] * len(row)
    if len(getCP(id)) > 1:
        return ['background-color: ' + colors["cp"]] * len(row)
    return [''] * len(row)

def setColumn(excel_writer: pd.ExcelWriter, sheet_name: str, excel: pd.DataFrame, factor=1.8):
    """
    按长度调整列宽
    """
    worksheet = excel_writer.sheets[sheet_name]
    for col_num, col_value in enumerate(excel.columns):
        column_len = max(excel[col_value].astype(str).str.len().max(), len(col_value))*factor
        if col_value == "姓名":
            column_len = 4*factor
        worksheet.set_column(col_num, col_num, column_len + 2)  # 留出一些空隙
    return excel_writer

def generateMain(file_dir: str, need_output_team=True) -> None:
    """
    将总表信息输出到Excel中。
    Args:
        file_name(str): 输出路径
    Returns:
        None
    """
    file_path = os.path.join(file_dir, "总表.xlsx")
    export_info = []
    personal_info_keys = []
    other_info_keys = []
    for _, volunteer in GlobalVar.volunteer_info.items():
        personal_info_keys = list(volunteer.personal_info.keys())
        other_info_keys = list(volunteer.other_info.keys())
        break
    for team_id, team in GlobalVar.team_info.items():
        member_export_info_head = [
            team_id,
            team.position,
            team.position_type,
            GlobalVar.volunteer_info[team.team_leader].personal_info["姓名"]
        ]

        # print the leader first!
        member_export_info = member_export_info_head.copy()
        member = GlobalVar.volunteer_info[team.team_leader]
        for info_key in personal_info_keys:
            member_export_info.append(member.personal_info[info_key])
        for info_key in other_info_keys:
            member_export_info.append(member.other_info[info_key])
        export_info.append(member_export_info)

        for member_id in team.team_member:
            if member_id == team.team_leader:
                continue # skip the leader
            member_export_info = member_export_info_head.copy()
            member = GlobalVar.volunteer_info[member_id]
            for info_key in personal_info_keys:
                member_export_info.append(member.personal_info[info_key])
            for info_key in other_info_keys:
                member_export_info.append(member.other_info[info_key])
            export_info.append(member_export_info)
    col_names = ['小组号', '岗位', '岗位类型', '小组长'] + personal_info_keys + other_info_keys
    excel = pd.DataFrame(export_info, columns= col_names)
    
    # set the style

    excel = excel.style\
    .applymap(lambda _: 'text-align: center')\
    .apply(takeColors, axis=1)
    
    

    # to excel
    excel_writer = pd.ExcelWriter(file_path,mode="w",engine="xlsxwriter")
    excel.to_excel(excel_writer, sheet_name='总表', index= False)
    excel_writer = setColumn(excel_writer, "总表", excel.data)
    generateTeam(excel_writer)
    generateReserved(excel_writer)
    generateColorMap(excel_writer)
    # 调整为合适的列宽
    excel_writer = setColumn(excel_writer, "总表", excel.data)
    
    excel_writer.close()

    # 将总表拆分为各个小组
    generateTeamExcels(file_dir)


def generateTeamExcels(file_dir: str, file_name="总表.xlsx"):
    if not os.path.exists(os.path.join(file_dir, file_name)):
        print("总表不存在！！")
        return
    excel = pd.read_excel(io=os.path.join(file_dir, file_name),
                          sheet_name="总表",
                          dtype=str)
    team_file_dir = os.path.join(file_dir, "按小组名单")
    os.makedirs(team_file_dir, exist_ok=True)
    team_list = excel.groupby("小组号").count().index
    print(team_list)
    for _, team_id in enumerate(team_list):
        team_id = str(team_id)
        team_excel = excel.loc[excel["小组号"]==team_id]
        team_excel = team_excel.style\
        .applymap(lambda _: 'text-align: center')

        team_file_path = os.path.join(team_file_dir, f"{team_id}.xlsx")
        excel_writer = pd.ExcelWriter(team_file_path,mode="w",engine="xlsxwriter")
        team_excel.to_excel(excel_writer, sheet_name='小组名单', index= False)
        excel_writer = setColumn(excel_writer, "小组名单", team_excel.data)
        excel_writer.close()
    return


def generateTeam(excel_writer: pd.ExcelWriter):
    sheet_name = "小组信息"
    col_names = ["岗位","岗位类型", "小组",	"组长", "组长学号", "组长手机号", "小组计划人数", "小组实际人数"]
    teams = []
    for _,team in GlobalVar.team_info.items():
        team_info = []
        team_info.append(team.position)
        team_info.append(team.position_type)
        team_info.append(team.team_id)
        team_info.append(GlobalVar.volunteer_info[team.team_leader].personal_info["姓名"])
        team_info.append(GlobalVar.volunteer_info[team.team_leader].personal_info["学号"])
        team_info.append(GlobalVar.volunteer_info[team.team_leader].personal_info["手机号"])
        team_info.append(team.team_max_size)
        team_info.append(team.team_size)
        teams.append(team_info)
    excel = pd.DataFrame(teams, columns= col_names)
    excel = excel.style.applymap(lambda _: 'text-align: center')
    excel.to_excel(excel_writer, sheet_name=sheet_name, index= False)
    # 调整为合适的列宽
    excel_writer = setColumn(excel_writer, sheet_name, excel.data)
    

def generateReserved(excel_writer: pd.ExcelWriter):
    sheet_name = "储备志愿者"

    export_info = []

    personal_info_keys = []
    other_info_keys = []
    for _, volunteer in GlobalVar.volunteer_info.items():
        personal_info_keys = list(volunteer.personal_info.keys())
        other_info_keys = list(volunteer.other_info.keys())
        break

    for _,vol in GlobalVar.volunteer_info.items():
            if (vol.interview is None) or vol.interview != "reserve":
                continue
            member_export_info = []
            for info_key in personal_info_keys:
                member_export_info.append(vol.personal_info[info_key])
            for info_key in other_info_keys:
                member_export_info.append(vol.other_info[info_key])
            export_info.append(member_export_info)
    col_names = personal_info_keys + other_info_keys
    excel = pd.DataFrame(export_info, columns= col_names)
    excel = excel.style.applymap(lambda _: 'text-align: center')
    excel.to_excel(excel_writer, sheet_name=sheet_name, index= False)
    excel_writer = setColumn(excel_writer, sheet_name, excel.data)

def generateColorMap(excel_writer: pd.ExcelWriter):
    sheet_name = "颜色对照表"
    col_name = ["颜色", "含义"]
    data = []
    data.append([colors["team_leader"], "小组长"])
    data.append([colors["staff"], "内部"])
    data.append([colors["family"], "家属"])
    #data.append([colors["vice_leader"], "小闪电"])
    for group, color in GlobalVar.group_colors.items():
        data.append([color, group])
    excel = pd.DataFrame(data, columns= col_name)
    excel = excel.style\
        .applymap(lambda x: 'background-color: '+ x if x in [c[0] for c in data] else '')\
        .applymap(lambda _: 'text-align: center')
    excel.to_excel(excel_writer, sheet_name=sheet_name, index= False)



