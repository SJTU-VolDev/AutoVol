from util.GlobalVar import GlobalVar

def add_binary(a: str, b: str):
    """
    为两个人添加二元关系。
    """
    ta = None
    tb = None
    for t in GlobalVar.cp_lists:
        if (a in t) and (b in t):
            # already coupled.
            return
        if a in t:
            ta = t
        if b in t:
            tb = t
    if (ta is not None) and (tb is not None):
        # merge
        ta.extend(tb)
        GlobalVar.cp_lists.remove(tb)
    elif ta is not None:
        # add b
        ta.append(b)
    elif tb is not None:
        # add a
        tb.append(a)
    else:
        # add a and be
        GlobalVar.cp_lists.append([a,b])

def getCP(cp_id: str) -> list:
    """
    根据cp_id返回情侣的学号
    Args:
        cp_id(str): 情侣的id
    Returns:
        (list[str]): 一个list,其中是情侣的学号
    """
    for cps in GlobalVar.cp_lists:
        if cp_id in cps:
            cps_copy = cps.copy()
            for i in cps_copy:
                if not (i in GlobalVar.volunteer_info):
                    print("注意：情侣中{}同学不存在！！".format(i),cps_copy)
                    cps_copy.remove(i)
                elif GlobalVar.volunteer_info[i].interview is None:
                    print("注意：情侣中{}同学没来面试！！".format(i),cps_copy)
                    cps_copy.remove(i)
                elif GlobalVar.volunteer_info[i].interview != "pass":
                    cps_copy.remove(i)
            cps_copy = sort_cps(cps_copy)
            return cps_copy
    return [cp_id]

def sort_cps(cps):
    """
    对情侣进行排序，内部成员在最前面
    """
    staff = []
    for cp in cps:
        if cp not in GlobalVar.volunteer_info:
            continue
        if GlobalVar.volunteer_info[cp].staff is not None:
            staff.append(cp)
            cps.remove(cp)
    cps = staff + cps
    return cps