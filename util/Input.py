import pandas as pd
import os
import math
from pathlib import Path
import sys
sys.path.append(os.path.abspath('.')) 

from util.GlobalVar import GlobalVar
from util.models import Volunteer, Group, Team
from util.api import readTableAndInterpretKeys, assertIn, assertInfo, getVolIdByName, readTable, getPriviledgedNum, get_excel_name_in_folder
from util.handleCP import add_binary, getCP
from config.config import 正式路径, 工作路径

def handleStaff(file_dir: str):
    """
    添加内部成员
    """
    keys, table = readTableAndInterpretKeys(os.path.join(file_dir,"内部.xlsx"),"内部")
    for j in range(len(table[keys[0]])):
        p_info = {} # 个人信息
        o_info = {} # 其他信息
        s_info = {} # 小组长意向
        for key in keys:
            if key in GlobalVar.personal_info:
                p_info[key] = str(table[key][j])
            if key in GlobalVar.other_info:
                o_info[key] = str(table[key][j])
            if key in GlobalVar.staff_info:
                s_info[key] = str(table[key][j])

        vol=Volunteer()
        vol.init_personal_info(p_info)
        vol.init_other_info(o_info)
        vol.init_staff(s_info)

        # 校验信息是否符合要求
        assertIn(["学号"],vol.personal_info,"存在学生没有学号！")
        assertInfo(GlobalVar.personal_info,vol.personal_info,"内部成员{}个人信息缺东西".format(vol.personal_info["学号"]))
        assertInfo(GlobalVar.other_info,vol.other_info,"内部成员{}其他信息缺东西".format(vol.personal_info["学号"]))
        assertIn(GlobalVar.staff_info,s_info,"内部成员{}小组长意向缺东西。".format(vol.personal_info["学号"]))
        if vol.personal_info["学号"] in GlobalVar.volunteer_info:
            # 可能存在填了两次表！
            print("Error: 内部成员学号{}在\"内部.xlsx\"中重复出现,请确认是怎么回事！！可能填了两次！".format(vol.personal_info["学号"]))
            exit(-1)
        
        # 校验完成后加入数据结构
        GlobalVar.volunteer_info[vol.personal_info["学号"]] = vol
        GlobalVar.volunteer_info[vol.personal_info["学号"]].setPassPrivileged()
    return

def handleFamily(file_dir: str):
    """
    将内部成员的家属添加入数据结构！
    """
    keys, table = readTableAndInterpretKeys(os.path.join(file_dir,"内部.xlsx"),"家属")
    if (len(keys)==0):
        # No such thing called "家属"
        print("注意：此次活动没有家属表,即没有开后门的内部同学！")
        return
    
    for j in range(len(table[keys[0]])):
        p_info = {} # 个人信息
        o_info = {} # 其他信息
        f_info = {} # 家属信息
        for key in keys:
            if key in GlobalVar.personal_info:
                p_info[key] = str(table[key][j])
            if key in GlobalVar.other_info:
                o_info[key] = str(table[key][j])
            if key == "谁的家属":
                # 默认内部人员不会重名。
                member_list = getVolIdByName(str(table[key][j]))
                f_info[key] = None # 需要初始化,否则会出现致命KeyError
                if len(member_list) == 0:
                    print("提示：内部成员\"{}\"没有报名,可以确认一下,不过真的不参加也没有关系,程序也不会挂！".format(table[key][j]))
                elif len(member_list) > 1:
                    print("错误：内部成员\"{}\"有重名".format(table[key][j]))
                    exit(-1)
                else: # len(member_list) == 1
                    f_info[key] = str(member_list[0])
            if key == "是否要和Ta同组":
                f_info[key] = str(table[key][j])

        
        vol=Volunteer()
        vol.init_personal_info(p_info)
        vol.init_other_info(o_info)
        vol.init_family(f_info)

        # 校验信息是否符合要求
        assertIn(["学号"],vol.personal_info,"存在学生没有学号！")
        assertInfo(GlobalVar.personal_info,vol.personal_info,"家属\"{}\",学号{}个人信息缺东西".format(vol.personal_info["姓名"],vol.personal_info["学号"]))
        assertInfo(GlobalVar.other_info,vol.other_info,"家属\"{}\",学号{}其他信息缺东西".format(vol.personal_info["姓名"],vol.personal_info["学号"]))
        assertIn(GlobalVar.family_info,f_info,"家属\"{}\",学号{}没有说明是谁的家属。".format(vol.personal_info["姓名"],vol.personal_info["学号"]))
        if vol.personal_info["学号"] in GlobalVar.volunteer_info:
            # 默认家属与内部成员不相交！
            print("Error: 家属姓名\"{}\",学号{}在\"内部.xlsx\"中重复出现,请确认是怎么回事！！".format(vol.personal_info["姓名"],vol.personal_info["学号"]))
            exit(-1)
        
        GlobalVar.volunteer_info[vol.personal_info["学号"]] = vol
        GlobalVar.volunteer_info[vol.personal_info["学号"]].setPassPrivileged()
        if table["是否要和Ta同组"][j] == "是" and f_info["谁的家属"] in GlobalVar.volunteer_info:
            add_binary(vol.personal_info["学号"],f_info["谁的家属"]) # 为想要同组的内部成员和家属添加二元关系
    return

def handleMembers(file_dir: str):
    """
    为青志队成员初始化 volunteer_Info (包括“内部成员”与“家属”).

    Args:
        file_dir (str): "内部.xlsx"所在文件夹的路径
    """
    # 1. 处理内部人员报名
    handleStaff(file_dir)
    # 2. 处理可能存在的家属报名
    handleFamily(file_dir)
    return

def handleRecruitment(file_dir: str):
    """
    将普通志愿者添加入数据结构！
    """
    keys, table = readTableAndInterpretKeys(os.path.join(file_dir,"招募总表.xlsx"))

    for j in range(len(table[keys[0]])):
        p_info = {} # 个人信息
        o_info = {} # 其他信息
        for key in keys:
            if key in GlobalVar.personal_info:
                p_info[key] = str(table[key][j])
            if key in GlobalVar.other_info:
                o_info[key] = str(table[key][j])

        vol=Volunteer()
        vol.init_personal_info(p_info)
        vol.init_other_info(o_info)

        # 筛选重复报名的人  
        if vol.personal_info["学号"] in GlobalVar.volunteer_info:
            continue
        
        # 校验信息
        assertIn(["学号"],vol.personal_info,"存在学生没有学号！")
        assertInfo(GlobalVar.personal_info,vol.personal_info,"志愿者\"{}\",学号{}个人信息缺东西".format(vol.personal_info["姓名"],vol.personal_info["学号"]))
        
        # 校验完成后加入数据结构
        GlobalVar.volunteer_info[vol.personal_info["学号"]] = vol
    return

def handleGroups(file_dir: str):
    """
    添加团队成员
    """
    no_data_dict = {"姓名":[],"学号": [],"团队": []}
    file_list = os.listdir(os.path.join(file_dir,"团体"))

    for file_name in file_list:

        # 为每个团队创建一个Group对象
        group_name = file_name.split(".")[0]
        GlobalVar.group_lists[group_name] = Group(group_name)

        # 读取团队成员信息
        keys, table = readTableAndInterpretKeys(os.path.join(file_dir,"团体",file_name))

        for j in range(len(table[keys[0]])):
            g_info = {} # 团队成员信息

            for key in keys:
                if key in GlobalVar.group_info:
                    g_info[key] = str(table[key][j])

            # 校验信息是否符合要求
            if not "学号" in g_info:
                print("Error: 团队成员没有学号！")
                exit(-1)
            if table["学号"][j] in GlobalVar.volunteer_info:
                GlobalVar.volunteer_info[table["学号"][j]].interview = "pass"
                GlobalVar.volunteer_info[table["学号"][j]].init_group(group_name)
                GlobalVar.group_lists[group_name].group_members.append(table["学号"][j])
            else:
                print("Warning: 存在团队成员\"{}\",学号{}没有个人信息,请查阅“团队人员缺失信息表.xlsx”,并将完整信息加入到招募总表中,再次运行程序！".format(table["姓名"][j],table["学号"][j]))
                no_data_dict["姓名"].append(table["姓名"][j])
                no_data_dict["学号"].append(table["学号"][j])
                no_data_dict["团队"].append(group_name)

    table_no_data_excel = pd.DataFrame(no_data_dict)
    table_no_data_excel_path = os.path.join(工作路径,"团队人员缺失信息表.xlsx")
    table_no_data_excel.to_excel(table_no_data_excel_path, index=False)
    if len(no_data_dict["学号"]) > 0:
        exit(-1)
    return

def handleCouples(file_dir: str):
    """
    读入情侣表,建立二元等价类数据结构。
    Args:
        file_path(str): the file path of the xlsx
    Returns:
        None
    """
    keys, table = readTableAndInterpretKeys(os.path.join(file_dir,"情侣.xlsx"))

    for j in range(len(table[keys[0]])):
        if not ((table["同学1学号"][j]) in GlobalVar.volunteer_info):
            print("注意：情侣表中 {} 同学可能没有报名,也可能有其他问题,请确认！".format(table["同学1学号"][j]))
        if not ( str(table["同学2学号"][j]) in GlobalVar.volunteer_info):
            print("注意：情侣表中 {} 同学可能没有报名,也可能有其他问题,请确认！".format(table["同学2学号"][j]))

        add_binary(str(table["同学1学号"][j]),str(table["同学2学号"][j]))
    # Til now, all the couples are handled in GlobalVar.cp_lists
    return

def handleViceLeader(file_dir: str, TeamNum: int):
    """
    读入小闪电表,筛选通过面试的小闪电,通过个数为小组数,将小闪电信息添加入数据结构。
    小闪电表仅有3列,姓名,学号,小闪电归一化得分。
    Args:
        file_path(str): the file path of the xlsx
    Returns:
        None
    """
    keys, table = readTableAndInterpretKeys(os.path.join(file_dir,"小闪电.xlsx"))
    table["小闪电归一化得分"] = table["小闪电归一化得分"].astype(float)
    table_sorted = table.sort_values(by='小闪电归一化得分', ascending=False)
    sorted_list = list(table_sorted["学号"].astype(str))
    print(sorted_list)
    GlobalVar.vice_leader_list.extend(sorted_list) # put the vice_leaders into the GlobalVar.vice_leader_list
    
    # 处理小闪电的特殊情况！
    for vld in GlobalVar.vice_leader_list:
        if GlobalVar.volunteer_info[vld].isPrivileged():
            # 出现特殊情况！此时还不是小组长的有意向的人就已经是特殊了！
            GlobalVar.vice_leader_list.remove(vld)
        for vld_cp in getCP(vld):
            if GlobalVar.volunteer_info[vld_cp].isPrivileged() and (vld in GlobalVar.vice_leader_list):
                # 这个哥么不行！他本人和CP中有人是小组长or团体！
                GlobalVar.vice_leader_list.remove(vld)
            if (vld_cp != vld) and (vld_cp in GlobalVar.vice_leader_list):
                # cp只能有1人担任小闪电，分高的那位！
                GlobalVar.vice_leader_list.remove(vld_cp)
    
    # 择优录取
    if len(GlobalVar.vice_leader_list) < len(GlobalVar.team_info):
        print("小闪电数量不足以分配给所有小组")
        raise Exception("小闪电数量不足以分配给所有小组")
    else:
        # 择优录取！
        GlobalVar.vice_leader_list = GlobalVar.vice_leader_list[:len(GlobalVar.team_info)]
        for vld in GlobalVar.vice_leader_list:
            GlobalVar.volunteer_info[vld].isviceleader = True
            GlobalVar.volunteer_info[vld].interview = "pass"

    return

def splitTeamByPosition(file_dir : str) -> (int,int):
    """
    按照岗位信息,拆分小组
    Args:
        file_dir(str): 岗位信息表所在的路径
    Returns:
        recruit_total(int): 需要招募的总人数
    """
    key,table = readTableAndInterpretKeys(os.path.join(file_dir,"岗位.xlsx"))
    TeamId = 0
    recruit_total = 0
    print("每组至多有{0}人！".format(GlobalVar.SplitTeamMaxSize))
    for j in range(len(table[key[0]])):
        recruit_total += int(table["人数需求"][j]) 
        team_num = math.ceil(int(table["人数需求"][j]) / GlobalVar.SplitTeamMaxSize)
        # for i in range(team_num - 1):
        #     team = Team()
        #     TeamId += 1
        #     team.team_id = TeamId
        #     team.team_max_size = (int(table["人数需求"][j]) // team_num)
        #     team.team_size = 0
        #     team.position = table["岗位名称"][j]
        #     team.position_type = table["岗位简介"][j]
        #     GlobalVar.team_info[str(len(GlobalVar.team_info)+1)] = team
        # team = Team()
        # TeamId += 1
        # team.team_id = TeamId
        # team.team_max_size = int(table["人数需求"][j]) - (int(table["人数需求"][j]) // team_num) * (team_num - 1)
        # team.team_size = 0
        # team.position = table["岗位名称"][j]
        # team.position_type = table["岗位简介"][j]
        # GlobalVar.team_info[str(len(GlobalVar.team_info)+1)] = team
        for i in range(team_num):
            team = Team()
            TeamId += 1
            team.team_id = TeamId
            team.team_max_size = (int(table["人数需求"][j]) // team_num)
            team.team_size = 0
            team.position = table["岗位名称"][j]
            team.position_type = table["岗位简介"][j]
            GlobalVar.team_info[str(len(GlobalVar.team_info)+1)] = team
        res = int(table["人数需求"][j]) - (int(table["人数需求"][j]) // team_num) * team_num
        while res > 0:
            GlobalVar.team_info[str(TeamId - res + 1)].team_max_size += 1
            res -= 1
        
    return recruit_total,TeamId
   
def divInterviewResult(file_dir:str, pass_num:int, reserve_num:int, to_excel_flag:bool=False) -> None:
    """
    将面试者按照面试的归一化得分排序分为三类: "面试结果-通过" / "面试结果-储备" / "面试结果-未通过".
    面试汇总表仅有3列,姓名,学号,归一化得分。
    Args:
        file_fir (str): 面试结果所在的路径
        pass_num (int): 总通过名额(包括开后门)
        reserve_num (int): 储备名额
    """
    # Read the orignal interview result table.
    keys, table = readTable(os.path.join(file_dir,"面试汇总表.xlsx"))
    # Delete the first two columns and the last column['面试时间','面试官'].
    # keys = keys[2:]
    # table = table.drop(columns=table.columns[[0,1]],axis=1)

    # Sort the table by "评分" in descending order.
    table["归一化得分"] = table["归一化得分"].astype(float)
    table_sorted = table.sort_values(by='归一化得分', ascending=False)

    # 计算无特权的剩余名额
    pass_num -= getPriviledgedNum()
    if pass_num <= 0:
        print("错误：通过人数少于等于开后门人数！！")
        exit(-1)
    # 删除小闪电
    # Divide the table into three parts according to the pass_num and reserve_num.
    table_pass = []
    table_reserve = []
    table_fail = []

    sorted_list = list(table_sorted["学号"])

    # 重复面试的哥们儿取高分,多余的删掉
    duplicated_dict = {}
    for vol in sorted_list:
        if sorted_list.count(vol) > 1:
            duplicated_dict[vol] = 1
    print("注意：以下同学重复面试！", duplicated_dict.keys())
    for vol in duplicated_dict.keys():
        place = sorted_list.index(vol)
        while True:
            try:
                sorted_list.remove(vol)
            except ValueError:
                break
        sorted_list.insert(place,vol)

    # 删除面试表中开后门的
    [sorted_list.remove(vol) for vol in GlobalVar.volunteer_info.keys() if GlobalVar.volunteer_info[vol].isPrivileged() and vol in sorted_list] 

    if len(sorted_list) < pass_num:
        print("注意：招募人数小于通过人数。")

    while len(table_pass) < pass_num and len(sorted_list) > 0:
        table_pass.append(sorted_list.pop(0))
        if table_pass[-1] not in GlobalVar.volunteer_info:
            print("注意：有人冲考！没有报名！")
            table_pass.pop(-1)
        else:
            GlobalVar.volunteer_info[table_pass[-1]].interview = "pass"

    while len(table_reserve) < reserve_num and len(sorted_list) > 0:
        table_reserve.append(sorted_list.pop(0))
        if table_reserve[-1] not in GlobalVar.volunteer_info:
            print("注意：有人冲考！没有报名！")
            table_reserve.pop(-1)
        else:
            GlobalVar.volunteer_info[table_reserve[-1]].interview = "reserve"

    while len(sorted_list) > 0:
        table_fail.append(sorted_list.pop(0))
        if table_fail[-1] not in GlobalVar.volunteer_info:
            print("注意：有人冲考！没有报名！")
            table_fail.pop(-1)
        else:
            GlobalVar.volunteer_info[table_fail[-1]].interview = "fail"

    # 将面试结果写入志愿者信息表
    if to_excel_flag:
        table_interview_folder = os.path.join(工作路径,"面试结果")
        os.makedirs(table_interview_folder,exist_ok=True)

        table_pass_excel = pd.DataFrame(table_pass)
        table_pass_excel_path = os.path.join(table_interview_folder,"面试汇总表-通过.xlsx")
        table_pass_excel.to_excel(table_pass_excel_path, index=False)

        table_reserve_excel = pd.DataFrame(table_reserve)
        table_reserve_excel_path = os.path.join(table_interview_folder,"面试汇总表-储备.xlsx")
        table_reserve_excel.to_excel(table_reserve_excel_path, index=False)

        table_fail_excel = pd.DataFrame(table_fail)
        table_fail_excel_path = os.path.join(table_interview_folder,"面试汇总表-未通过.xlsx")
        table_fail_excel.to_excel(table_fail_excel_path, index=False)
    return

def InputAndPreTreatment():
    """
    **对外接口**
    读取所有文件,并对数据进行预处理。
    """
    excel_name_list = get_excel_name_in_folder(正式路径)

    sys.stdout = GlobalVar.log_file
    if not ("内部" in excel_name_list):
        print("错误：本次活动没有内部同学参与！不能没有组长！")
        exit(-1)
    else:
        print("开始读取内部.xlsx并处理内部和家属的报名情况")
        handleMembers(正式路径)

    if not ("招募总表" in excel_name_list):
        print("注意：本次活动没有外部同学参与！")
    else:
        print("开始读取招募总表.xlsx并处理普通志愿者的报名情况")
        handleRecruitment(正式路径)

    if not (os.path.exists(os.path.join(正式路径,"团体"))):
        print("注意：本次活动没有团体报名！")
    else:
        print("开始读取团体文件夹所有文件并处理团体成员的报名情况")
        handleGroups(正式路径)

    if not ("情侣"in excel_name_list):
        print("注意：本次活动没有情侣报名！")
    else:
        print("开始读取情侣.xlsx并处理情侣的报名情况")
        handleCouples(正式路径)

    if not ("岗位" in excel_name_list):
        print("错误：本次活动没有岗位信息！")
        exit(-1)
    else:
        print("开始读取岗位.xlsx并拆分小组")
        recruit_total, TeamNum = splitTeamByPosition(正式路径)
        print("总计需要招募：{:d} 名志愿者！".format(recruit_total))
    
    if not ("小闪电" in excel_name_list):
        print("注意：本次活动没有小闪电！")
    else:
        print("开始读取小闪电.xlsx并分配小闪电")
        handleViceLeader(正式路径,TeamNum)

    if not ("面试汇总表" in excel_name_list):
        print("注意：本次活动没有面试！请确认")
    else:
        print("开始读取面试汇总表.xlsx并分配面试结果")
        divInterviewResult(正式路径, recruit_total, int(recruit_total*GlobalVar.reserveProportion), to_excel_flag=True)
    
    sys.stdout = GlobalVar.original_stdout
    return
