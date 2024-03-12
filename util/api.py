import pandas as pd
import os
from pathlib import Path
import sys
import math
from util.GlobalVar import GlobalVar

def readTable(file_path: str, sheet_name=0):
    """
    Read in a table from a xlsx file.
    Args:
        file_path(str): the file path of the xlsx
    Returns:
        keys(list): the keys
        table(pd.DataFrame): the whole table
    """
    # empty str "" is parsed as None / nan
    table = pd.read_excel(io=file_path,
                              sheet_name=sheet_name,
                              keep_default_na=False,
                              dtype=str)
    keys = list(table.keys())
    return keys, table

def matchKey(key: str, _dict: dict, matched_key=""):
    """
    看看key能否与_dict中的info_key匹配上,采用最大长度匹配策略！
    """
    for info_key in _dict:
        if info_key in key:
            if len(matched_key) < len(info_key):
                matched_key = info_key
    return matched_key

def interpretKeys(keys: list, table: pd.DataFrame):
    """
    Interpret keys to standardized format: "1、您的姓名" -> "姓名"
    Raise Error if keys are not registered in 信息说明.xlsx
    采用最大长度匹配
    """
    for j in range(len(keys)):
        matched_key = ""
        matched_key = matchKey(keys[j], GlobalVar.personal_info, matched_key)
        matched_key = matchKey(keys[j], GlobalVar.other_info, matched_key)
        matched_key = matchKey(keys[j], GlobalVar.staff_info, matched_key)
        matched_key = matchKey(keys[j], GlobalVar.family_info, matched_key)
        matched_key = matchKey(keys[j], GlobalVar.interview_info, matched_key)
        matched_key = matchKey(keys[j], GlobalVar.group_info, matched_key)
        matched_key = matchKey(keys[j], GlobalVar.cp_info, matched_key)
        matched_key = matchKey(keys[j], GlobalVar.position_info, matched_key)
        if (len(matched_key)==0):
            print("“{}”不在信息说明表中,请添加进去！".format(keys[j]))
            exit(-1)
        else:
            keys[j] = matched_key
    table.columns=keys
    return keys,table

def readTableAndInterpretKeys(file_path: str, sheet_name=0):
    """
    合并了readTable和interpretKeys
    Args:
        file_path(str): xlsx的文件路径
    Returns:   
        keys(list): 信息说明表中的key
        table(pd.DataFrame): 信息说明表中的table
    """
    keys, table = readTable(file_path, sheet_name)
    return interpretKeys(keys, table)

def assertIn(item_list, _dict, msg=""):
    """
    断言所有item_list中的东西都在_dict中。
    
    Args:
        item_list(list): 需要判断的信息
        _dict(dict): 从信息说明表中读取的信息
        msg(str): 错误提示
    """
    for item in item_list:
        if not (item in _dict):
            print(msg)
            print("Error!")
            print(item,end=' ')
            print("not in iterable")
            exit(-1)

def assertInfo(info_dict: dict, _dict, msg=""):
    """
    所有info_dict中True的东西必须在_dict中。

    Args:
        info_dict(dict): 需要判断的信息
        _dict(dict): 从信息说明表中读取的信息
        msg(str): 错误提示
    """
    for key in info_dict.keys():
        if (info_dict[key]):
            if not (key in _dict):
                print(msg)
                exit(-1)

def getVolIdByName(vol_name: str):
    """
    根据志愿者姓名获取志愿者学号

    Args:
        vol_name(str): 志愿者姓名
    Returns:
        vol_id(str): 志愿者学号
    """
    ans = []
    for stu_id in GlobalVar.volunteer_info.keys():
        if GlobalVar.volunteer_info[stu_id].getName()==vol_name:
            ans.append(stu_id)
    return ans

def getPriviledgedNum(assertion_enabled=False):
    """
    统计已经被设为通过的人数
    """
    count = 0
    for vol_id in GlobalVar.volunteer_info.keys():
        vol = GlobalVar.volunteer_info[vol_id]
        if vol.isPrivileged():
            if assertion_enabled:
                assert vol.interview == "pass"
            count += 1
    return count

def get_excel_name_in_folder(folder: str):
    """
    返回一个文件夹中所有excel的文件名(不含后缀),作为一个list

    Args:
        folder (str): 绝对路径或相对路径
    Returns:
        (list[str]): 一个list,其中是excel文件名(不含后缀)。
    """
    return [os.path.basename(str(path)).split(".xls")[0] for path in Path(folder).glob("*.xls*")]
