class GlobalVar(object):
    # 一些表头信息
    personal_info = {}
    other_info = {}
    interview_info = {}
    staff_info = {}
    family_info = {}
    group_info = {}
    cp_info = {}

    cp_lists = []
    group_lists = {}
    group_colors = {}
    team_info = {}
    position_info = {}
    # 最关键的！所有志愿者构成的dict
    volunteer_info = {}
    vice_leader_list = []

    #以下两项  在信息说明表中修改！！在这里修改无效！！
    SplitTeamMaxSize = 35 # 规定拆分小组时，默认的每个小组最大人数（在信息说明表中修改！这里修改无效！）
    reserveProportion = 0.125 #储备志愿者与正式志愿者占比reserveProportion（在信息说明表中修改！这里修改无效！）

    log_file = None
    original_stdout = None   
    
    @staticmethod
    def serialize():
        print(GlobalVar.personal_info)
        print(GlobalVar.other_info)
        print(GlobalVar.interview_info)
        print(GlobalVar.volunteer_info)
        pass