import requests
import os
import pandas as pd

def download_file(url, cookies, save_path, name):
    if os.path.exists(os.path.join(save_path,name)):
        return
    response = requests.get(url,
                            cookies=cookies,
                            )
    if response.status_code == 200:
        os.makedirs(save_path, exist_ok=True)

        with open(os.path.join(save_path,name), 'wb') as file:
            file.write(response.content)


def getExcel(cookies):
    QuestionDataList = [
        "https://wj.sjtu.edu.cn/api/v1/manage/questionnaire/created/44698/data/table-export/excel?params={}",
        "https://wj.sjtu.edu.cn/api/v1/manage/questionnaire/created/44699/data/table-export/excel?params={}",
        "https://wj.sjtu.edu.cn/api/v1/manage/questionnaire/created/44700/data/table-export/excel?params={}"
                        ]
    for day in range(len(QuestionDataList)):
        url = QuestionDataList[day]
        print("正在下载问卷数据...")
        download_file(url, cookies, "./问卷数据","Day " + str(day)+".xlsx")
    file_list = os.listdir("./问卷数据")
    day = 0
    Interviewer_data = {
        "面试官":[],
        "面试时间":[],
    }
    excelwriter = pd.ExcelWriter(r"./面试官信息.xlsx", engine='xlsxwriter')
    for file in file_list:
        day += 1
        table = pd.read_excel(r"./问卷数据/"+file)
        tot = len(table["提交者"])
        Interviewer_data["面试官"]=(list(table["提交者"]))
        Interviewer_data["面试时间"]=(list(table["Q2. 面试时间段"]))
        it = 0
        for i in range(tot):
            it += 1
            interviewer = table["提交者"][i]
            interview_time = table["Q2. 面试时间段"][i]
            url_list = table["Q3. 请上传面试结果"][i].split("\n")
            print("正在下载\""+str(interviewer)+"\"的面试官打分表，第"+str(day)+"天进度 "+str(it)+" / "+str(tot))
            if url_list == 1:
                file_name = str(interviewer)+"_"+str(interview_time)+".xlsx"
                download_file(url, cookies,r"./面试官打分表/Day "+str(day), file_name)
            else:
                dfs = []
                for i in range(len(url_list)):
                    url = url_list[i]
                    file_name = str(interviewer)+"_"+str(interview_time)+"_"+str(i)+".xlsx"
                    download_file(url, cookies,r"./面试官打分表/Day "+str(day), file_name)
                    dfs.append(pd.read_excel(r"./面试官打分表/Day "+str(day)+"/"+file_name))
                    os.remove(r"./面试官打分表/Day "+str(day)+"/"+file_name)
                pd.concat(dfs,axis = 0).to_excel(r"./面试官打分表/Day "+str(day)+"/"+str(interviewer)+"_"+str(interview_time)+".xlsx", index=False)
        
        pd.DataFrame(Interviewer_data).to_excel(excelwriter, sheet_name="Day "+str(day),index=False)
    excelwriter.close()