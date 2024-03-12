import os
from util.Generates import generateTeamExcels

if __name__=="__main__":
    # 替换总表文件名，以及将
    总表路径 = os.path.join(".","输出表格","总表1000.xlsx")
    generateTeamExcels(os.path.dirname(总表路径),os.path.basename(总表路径))