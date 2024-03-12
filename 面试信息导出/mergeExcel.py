import pandas as pd
import os
def mergeExcel(days:int):
    data1 = {
        "姓名": [],
        "学号": [],
        "归一化得分":[],
    }
    data2 = {
        "姓名": [],
        "学号": [],
        "小闪电归一化得分":[],
    }
    for day in range(1, days+1):
        table_path = os.path.join(r"./面试官打分表", r"Day "+str(day))
        file_list = os.listdir(table_path)
        tot = len(file_list)
        it = 0
        for file in file_list:
            it += 1
            print("正在处理\"" + file.split("_")[0] + "\"的面试官打分表,第" + str(day) + "天进度 " + str(it) + " / " + str(tot))
            table = pd.read_excel(os.path.join(table_path, file))
            NameList = []
            IdList = []
            ScoreList = []
            LightningScoreList = []
            if "姓名" not in table.columns:
                NameList = list(table["Q1. 您的姓名"].astype("str"))
            else:
                NameList = list(table["姓名"].astype("str"))
            if "学号" not in table.columns:
                IdList = list(table["Q6. 您的学号"].astype("str"))
                for i in range(len(IdList)):
                    IdList[i] = IdList[i].split(".")[0]
            else:
                IdList = list(table["学号"].astype("str"))
                for i in range(len(IdList)):
                    IdList[i] = IdList[i].split(".")[0]
            ScoreList = list(table["归一化成绩"].astype("float"))
            LightningScoreList = list(table["闪电归一化成绩"].astype("float"))
            
            for i in range(len(NameList)):
                name = NameList[i]
                stu_id = IdList[i]
                score = ScoreList[i]
                lightning_score = LightningScoreList[i]
                if name == "nan" or name == "请delete掉此格，或者覆盖，请勿直接删除！":
                    continue
                data1["姓名"].append(name)
                data1["学号"].append(stu_id)
                data1["归一化得分"].append(score)
                if table["闪电得分(10)"][i] > 0:
                    data2["姓名"].append(name)
                    data2["学号"].append(stu_id)
                    data2["小闪电归一化得分"].append(lightning_score)

    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)
    df1.to_excel(r"./面试汇总表.xlsx", index=False)
    df2.to_excel(r"./小闪电.xlsx", index=False)