import sys
import os

from util.GlobalVar import GlobalVar
from util.api import readTable, assertIn
from config.config import 工作路径, 正式路径, 信息说明表路径

def buildConfig(file_path: str):
    """
    Build the Configuration for Info.
    True means required, False means optional.
    Args:
        file_path (str): 信息说明表的路径。
    """
    keys, table = readTable(file_path)
    GlobalVar.SplitTeamMaxSize = int(table["小组最大人数"][0])
    GlobalVar.reserveProportion = float(table["储备志愿者占比"][0])
    assertIn(["个人信息", "个人信息-是否必填"], keys, "信息说明表缺少个人信息栏")
    for key, required in zip(table["个人信息"], table["个人信息-是否必填"]):
        if key != "":
            GlobalVar.personal_info[key] = True if required=="是" else False
    assertIn(["其他报名信息", "其他报名信息-是否必填"], keys, "信息说明表缺少其他报名信息栏")
    for key, required in zip(table["其他报名信息"], table["其他报名信息-是否必填"]):
        if key != "":
            GlobalVar.other_info[key] = True if required=="是" else False
    assertIn(["面试信息"], keys, "信息说明表缺少面试信息栏")
    for key in table["面试信息"]:
        if key != "":
            GlobalVar.interview_info[key] = True
    assertIn(["内部人员信息"], keys, "信息说明表缺少内部人员信息栏")
    for key in table["内部人员信息"]:
        if key != "":
            GlobalVar.staff_info[key] = True
    assertIn(["家属信息"], keys, "信息说明表缺少家属信息栏")
    for key in table["家属信息"]:
        if key != "":
            GlobalVar.family_info[key] = True
    assertIn(["团体信息"], keys, "信息说明表缺少团体信息栏")
    for key in table["团体信息"]:
        if key != "":
            GlobalVar.group_info[key] = True
    assertIn(["情侣信息"], keys, "信息说明表缺少情侣信息栏")
    for key in table["情侣信息"]:
        if key != "":
            GlobalVar.cp_info[key] = True
    assertIn(["岗位信息"], keys, "信息说明表缺少岗位信息栏")
    for key in table["岗位信息"]:
        if key != "":
            GlobalVar.position_info[key] = True
    GlobalVar.serialize()
    return

def Init():
    """
    **对外接口**
    初始化工作目录,并且读取信息说明表。
    """
    GlobalVar.log_file = open('日志.log','w',encoding='utf-8')
    GlobalVar.original_stdout = sys.stdout
    sys.stdout = GlobalVar.log_file
    # # 0. initialize the working directories.
    os.makedirs(工作路径,exist_ok=True)
    os.makedirs(正式路径,exist_ok=True)
    buildConfig(信息说明表路径)