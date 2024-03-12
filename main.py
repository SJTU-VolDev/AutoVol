# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath('.')) 
from config.config import 工作路径, 正式路径, 信息说明表路径
from util.GlobalVar import GlobalVar
from util.Init import Init
from util.Generates import Generate
from util.assigns import assignTeams
from util.Input import InputAndPreTreatment
# 示例
def initDataBase():
    """
    [Description]
    Args:
        [param1]([param_type1]): [Description]
        [param2]([param_type2]): [Description]
    Returns:
        [return1]([return_type1]): [Description]
        [return2]([return_type2]): [Description]
    """
    return
from util.debug import outputCPlist
if __name__=="__main__":
    Init()
    InputAndPreTreatment()
    outputCPlist()
    assignTeams()
    Generate(工作路径)