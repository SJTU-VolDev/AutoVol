import random
import sys

from util.GlobalVar import GlobalVar
from util.handleCP import getCP
from config.config import 工作路径

def calculateGroupTeamLeader(group_member: list):
    """
    计算团体中报名的小组长
    Args:
        group_member(list): 团体成员的学号
    Returns:
        team_leader(list): 团体中报名的小组长的学号
    """
    team_leader = []
    for member in group_member:
        member_cps = getCP(member)
        for cp in member_cps:
            if (cp in GlobalVar.volunteer_info) and \
                GlobalVar.volunteer_info[cp].staff is not None and \
                GlobalVar.volunteer_info[cp].staff.want_leader == True and \
                GlobalVar.volunteer_info[cp].team is None:
                team_leader.append(cp)
    return team_leader


def assignGroups(leader_abundant=False):
    """
    对于每一个团体：
    估计需要的组数,指定组,如果团队有小组长,就指定小组长那个组。
    然后把含有团队成员的list取出(同时移除),先行填入这些组。
    假如组炸了,就再开。
    """
    group_num = len(GlobalVar.group_lists)
    if group_num == 0:
        return
    
    # 随机指定一个组填充团队
    team_id = random.randint(1,len(GlobalVar.team_info) // group_num // 2)
    # 按照团体执行插入操作
    for _,group in GlobalVar.group_lists.items():
        print(group.group_name)
        group_staff = calculateGroupTeamLeader(group.group_members)
        cp_of_staff = []
        for staff in group_staff:
            cp_of_staff.extend(getCP(staff))
        group_member = group.group_members.copy()
        for member in cp_of_staff:
            if member in group_member:
                group_member.remove(member)
        #random.shuffle(group_member)
        while team_id <= len(GlobalVar.team_info) and len(group_member) > 0:
            # 先尝试插入从团队内找到的小组长
            while(len(group_staff) > 0):
                group_leader = group_staff.pop()
                if GlobalVar.volunteer_info[group_leader].team is None:
                    GlobalVar.team_info[str(team_id)].insert(getCP(group_leader),True)
                    GlobalVar.team_info[str(team_id)].team_leader = group_leader
                    break # 找到组长了，跳出循环
            
            # 再尝试插入团队成员
            while GlobalVar.team_info[str(team_id)].calc_team_vacancy() >= 0 and len(group_member) > 0:
                to_insert = group_member.pop()
                if GlobalVar.volunteer_info[to_insert].team is not None:
                    continue
                    #已经被插入过了
                   
                # 插入时连同CP一起插入
                cps = getCP(to_insert)
                if GlobalVar.team_info[str(team_id)].insert(cps,True) == False:
                    team_id += 1
                    group_member.append(to_insert)
                    break
                else:
                    for cp in cps:
                        if cp in group_member:
                            group_member.remove(cp)
        # 剩下的小组长候选人作为普通组员加入
        
        if leader_abundant:
            while len(group_staff) > 0:
                group_leader = group_staff.pop()
                if GlobalVar.volunteer_info[group_leader].team is not None:
                    continue
                GlobalVar.volunteer_info[group_leader].staff.want_leader = False
                if GlobalVar.team_info[str(team_id)].calc_team_vacancy() >= len(getCP(group_leader)):
                    GlobalVar.team_info[str(team_id)].insert(getCP(group_leader))
                else:
                    team_id += 1
                    GlobalVar.team_info[str(team_id)].insert(getCP(group_leader),True)
                    GlobalVar.team_info[str(team_id)].team_leader = group_leader
        # 一个团体分配完毕，指针指向下一个组
        
        team_id += 1

def assignViceLeader():
    """
    给每个小组分配一个小闪电。
    假定小闪电不是小组长、也不是团队中人，如果是，直接从小闪电里面踢掉。
    情侣中取得分高的为小闪电。
    """
    if len(GlobalVar.vice_leader_list) == 0:
        return
    random.shuffle(GlobalVar.vice_leader_list)
    for team_id, team in GlobalVar.team_info.items():
        if len(GlobalVar.vice_leader_list) == 0:
            print("小闪电数量不足以分配给所有小组")
            raise Exception("小闪电数量不足以分配给所有小组")
        # 插入
        viceleader = None
        for possi_leader in GlobalVar.vice_leader_list:
            if team.insert(getCP(possi_leader),False):
                viceleader = possi_leader
                break
        if viceleader is None:
            print(f"没有能分配至小组号为{team_id}的小闪电志愿者,因为小组空余人数不足以填入小闪电及其CP")
            raise Exception(f"没有能分配至小组号为{team_id}的小闪电志愿者,因为小组空余人数不足以填入小闪电及其CP")
        GlobalVar.vice_leader_list.remove(viceleader)
    return

def assignMembers():
    """
    把想要当小组长并且不是团体成员的内部成员分配给没有小组长的组。
    """
    staff_leaders = [] # 小组长候选人
    for vol_id, volunteer in GlobalVar.volunteer_info.items():
        # 如果是内部成员,并且不是团体成员,并且想要当小组长,并且没有小组,就加入到小组长候选人中
        if  not volunteer.staff is None and \
            len(volunteer.groups) == 0 and \
            volunteer.staff.want_leader == True and \
            volunteer.team is None:
            staff_leaders.append(vol_id)
    # 按小组分配小组长
    random.shuffle(staff_leaders)
    for team_id, team in GlobalVar.team_info.items():
        if not team.team_leader is None:
            continue
        if len(staff_leaders) == 0:
            print("错误：内部想当小组长的志愿者数量不足以分配给所有小组")
            raise Exception("内部想当小组长的志愿者数量不足以分配给所有小组")
        # 插入
        leader = None
        for possi_leader in staff_leaders:
            if team.insert(getCP(possi_leader),True):
                leader = possi_leader
                break
        if leader is None:
            print(f"没有能分配至小组号为{team_id}的内部小组长志愿者,因为小组空余人数不足以填入小组长及其CP")
            raise Exception(f"没有能分配至小组号为{team_id}的内部小组长志愿者,因为小组空余人数不足以填入小组长及其CP")
        staff_leaders.remove(leader)
        team.team_leader = leader
    return

def assignStaff():
    """
    将其余内部成员分配到小组中
    """
    toInsert = []
    for vol_id, volunteer in GlobalVar.volunteer_info.items():
        if volunteer.staff is not None and volunteer.team is None:
            toInsert.append(vol_id)
            GlobalVar.volunteer_info[vol_id].staff.want_leader = False
    
    random.shuffle(toInsert)
    while len(toInsert) > 0: #直到插入完毕
        for team_id in GlobalVar.team_info.keys(): # 遍历小组
            for vol in toInsert: # 寻找可以插入的成员
                if GlobalVar.team_info[str(team_id)].insert(getCP(vol)):
                    toInsert.remove(vol)
                    for cp_vol in getCP(vol):
                        if cp_vol in toInsert:
                            toInsert.remove(cp_vol) # 如果有,一起remove掉！
                    break
    return

def assignLeftovers():
    """
    将通过成员添加入总表
    """
    teamid = 1 # 小组编号从第一组开始
    not_single = []
    single = []
    for vol in GlobalVar.volunteer_info.keys():
        if GlobalVar.volunteer_info[vol].interview is None:
            continue # 没来面试的不分组
        if (GlobalVar.volunteer_info[vol].interview == "pass") and (GlobalVar.volunteer_info[vol].team is None):
            toInsert = getCP(vol)
            if len(toInsert) > 1:
                not_single.append(vol)
            else:
                single.append(vol)

    # 随机打乱
    random.shuffle(not_single)
    random.shuffle(single)
    # 先分配情侣，插入策略是遍历小组，找到第一个能插入的小组就插入
    for vol in not_single:
        if not (GlobalVar.volunteer_info[vol].team is None):
            continue # 别人的cp,已经加入过了。
        toInsert = getCP(vol)
        teamid = random.randint(1,len(GlobalVar.team_info))
        while not GlobalVar.team_info[str(teamid)].insert(toInsert):
            teamid = random.randint(1,len(GlobalVar.team_info))

    teamid = 1 # 插入情侣后可能有小组仍有空位，从第一组开始插入直到填满
    for vol in single:
        while teamid <= len(GlobalVar.team_info):
            if GlobalVar.team_info[str(teamid)].insert([vol]):
                break
            else: 
                # 满了,插入失败！下一组走起 
                teamid += 1
                continue
            
    if teamid > len(GlobalVar.team_info):
        print("Error: 通过人数大于招募总人数！")
        exit(-1)
    return

def assignTeams():
    """
    **对外接口**
    对于每一个小组：
    估计需要的组数,指定组,如果团队有小组长,就指定小组长那个组。
    然后把含有团队成员的list取出(同时移除),先行填入这些组。
    假如组炸了,就再开。
    接着安排余下binary_list成员。(如同没有团体)(随机排组)
    """
    sys.stdout = GlobalVar.log_file
    print("开始分配小闪电")
    assignViceLeader()
    print("开始分配团体")
    assignGroups(leader_abundant=True)
    print("开始分配小组长")
    assignMembers()
    print("开始分配内部")
    assignStaff()
    print("开始分配剩余人员")
    assignLeftovers()
    sys.stdout = GlobalVar.original_stdout
