from util.GlobalVar import GlobalVar

DEFAULT_IDTYPE = "身份证"

class Volunteer:
    def __init__(self) -> None:
        self.personal_info = {}
        self.other_info = {}
        # 如果是None, 那么就是普通报名
        self.staff = None
        self.family = None
        self.groups = list()
        self.interview = None # 可选填pass/reserve/fail
        self.team = None
        self.isviceleader = False
        pass

    def isPrivileged(self) -> bool:
        """
        判断该志愿者是否属于不需要面试的人员（内部、家属、团体、超级志愿者无需面试）。
        判断是否是小闪电，小闪电预先处理，也认为是已通过的。
        """
        return not (self.staff is None and \
                self.family is None and \
                self.isviceleader == False and \
                len(self.groups)==0)
    
    def setPassPrivileged(self):
        if self.isPrivileged():
            self.interview = "pass"
        return

    def isStaff(self):
        return not (self.staff is None)
    
    def isFamily(self):
        return not (self.family is None)

    def defaultValueHandler(_dict: dict, key: str):
        """
        对于信息表中没有填的必填项，允许自动填充默认值。如果没有默认值，则报错。
        """
        if key == "证件类型":
            _dict["证件类型"] = DEFAULT_IDTYPE
            return
        # if no default is mentioned, then error occurs.
        print("Error: class Volunteer: 存在学生缺{}，且外部调用没有处理！".format(key))
        exit(-1)


    def init_personal_info(self, p_info: dict):
        """
        初始化个人信息。
        """
        self.personal_info=p_info
        # 如果在GlobalVar里面，允许为空的信息，那么就设置为None.
        for key in GlobalVar.personal_info:
            if not (key in self.personal_info):
                if GlobalVar.personal_info[key]:
                    Volunteer.defaultValueHandler(self.personal_info, key)
                self.personal_info[key] = None
        return
        
    def init_other_info(self, o_info: dict):
        """
        初始化其他信息。
        """
        self.other_info=o_info
        # 如果在GlobalVar里面，允许为空的信息，那么就设置为None.
        for key in GlobalVar.other_info:
            if not (key in self.other_info):
                if GlobalVar.other_info[key]:
                    Volunteer.defaultValueHandler(self.other_info, key)
                self.other_info[key] = None
        return
    
    def getName(self):
        if not "姓名" in self.personal_info:
            print("Error: class Volunteer: 姓名不存在！")
            exit(-1)
        elif self.personal_info["姓名"] is None:
            print("Error: class Volunteer: 姓名是选填项！")
            exit(-1)
        return self.personal_info["姓名"]


    def init_staff(self, s_info: dict):
        """
        初始化Staff，此人是内部工作人员。
        """
        self.staff = Staff(s_info["是否愿意以组长身份参加"] == "是",s_info["是否愿意以负责人身份参加"] == "是")
        return
    
    def init_family(self, f_info: dict):
        """
        初始化"家属"对象，此人是家属。
        """
        self.family = FamilyMember(f_info["谁的家属"])
        return

    def init_group(self,group_name):
        if not (group_name in self.groups):
            self.groups.append(group_name)
        return
    
    
    # 普通渠道报名 None
    # 情侣志愿者 None
    # 团队 None
    # 岗位信息 None

class Staff:
    def __init__(self, want_leader=False, want_director=False) -> None:
        self.want_leader = want_leader
        self.want_director = want_director

class FamilyMember:
    def __init__(self, mate_member_id) -> None:     
        self.mate_member_id = mate_member_id

class Team:
    def __init__(self) -> None:
        self.team_id = None
        self.team_leader = None
        self.team_member = []
        self.position = None
        self.position_type = None
        self.team_size = None
        self.team_max_size = None

    def calc_team_vacancy(self, include_leader=False):
        if self.team_leader is None:
            if include_leader:
                return self.team_max_size - self.team_size
            else:
                return self.team_max_size - self.team_size - 1
        else:
            return self.team_max_size - self.team_size
        
    def insert(self, toInsert: list, include_leader=False):
        if self.calc_team_vacancy(include_leader) >= len(toInsert):
            self.team_member.extend(toInsert)
            for vol_id in toInsert:
                if GlobalVar.volunteer_info[vol_id].team is not None:
                    print("错误：学号{0}重复分组！！".format(vol_id))
                    exit(-1)
                else:
                    GlobalVar.volunteer_info[vol_id].team = self.team_id
            self.team_size += len(toInsert)
            return True
        else:
            return False

class Area:
    def __init__(self) -> None:        
        self.area_id = None
        self.area_leader = None
        self.area_member = []

class Group:
    def __init__(self, group_name) -> None:
        self.group_name = group_name
        self.group_members = []
