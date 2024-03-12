# AutoVol
Automatic Volunteer Software

## 0. 使用手册

### 0.1 测试用例

获取群聊内压缩包，解压至`./examples`文件夹中。

### 0.2 安装依赖

新引入的库请添加至`requirements.txt`.

运行以下命令安装依赖：
~~~
pip install -r requirements.txt
~~~

### 0.3 使用警告
0. 所有表格标题必须在`config\信息说明.xlsx`中申明。之后在使用时采用最大匹配，如"1. 您的姓名"会格式化匹配为"姓名"，"2. 您的姓名的英文拼音"会变成"姓名的英文拼音"而非"姓名"。但如果申明的是"拼音"就会报错，因为"姓名"和"拼音"同时出现，且长度相等。

1. 报错信息如：`“4、您的身份证号:”不在信息说明表中，请添加进去！`应该是表格标题和信息说明表中的所给不同，请确认一下！

2. 不存在“身份证号”一栏，只存在“证件号”一栏，请手动修正！（可能有侨胞、留学生。）

3. 家属默认和内部成员同组，且家属和内部成员必须<b>不相交</b>！

4. 如果多名内部成员想要同组，请手动添加至情侣表中，并采用铁索连环，同时想要同组的内部成员<b>至多只能有1人想要当领队</b>！(否则不可能同时实现成为领队并且同组。)


## 第一步：建立数据结构（ER Model）

### 1.1 应用模型——ER Model

Entity-Relationship Model。
用实体 (Entity) 和实体间的关系 (Relationship) 来建模。

参见附录Appendix 1 中详细模型，即实体的详细属性说明。

### 1.2 系统设计

~~~
|- `config` 文件夹：内含本次志愿者活动的配置文件。
    |- `config.py`： 指定`正式路径`与`工作路径`等其他路径。
    |- `信息说明.xlsx`: 在表中填写志愿者们要提交哪些信息。
|- `正式路径` 文件夹：包含所有目前获得的excel，如果有修改，需要在文件名中添加`（改）`。逻辑是：认为所有的表相互依赖，则每次运行会将`正式路径`中表可以生成的后续表都生成一遍。另外，也可以可控生成。
|- `工作路径` 文件夹：生成的新表会存储于此路径中，避免覆盖上一版的旧表。（生成完后只需将`工作路径`里面的东西复制走即可。每次开始时，不会清空此文件夹，如果此文件夹内有文件，则新文件命名一律加上系统时间。）
~~~


### 1.3 数据结构

数据结构的建立来源于ER模型。

~~~
志愿者
-- 个人信息，其他信息

    普通渠道报名
    -- 面试信息

    特殊渠道报名
        内部报名 
        -- 必须录取，可能想要当领队，可能会有同组的需求

        情侣志愿者
        -- 对象，可能不会录取

        团队
        -- 必须录取，团队有同组的需求
~~~

以下是Python模型建立

~~~
class Volunteer:
    个人信息
    其他信息

    普通渠道报名 None
    内部报名 None
    情侣志愿者 None
    团队 None

    岗位信息 None
~~~

每个Volunteer类对象代表一个志愿者。将所有志愿者放在全局变量字典GlobalVar.volunteer_dict中。
其中key是学号，唯一标识，不重复，item是类对象。如下所示：

~~~
(global)
volunteer_dict = {"520021919999": hhh (Volunteer 类对象), ...}
~~~


## 第二步：逻辑控制 (Dependency Graph)

### 2.1 依赖图建模策略

1. 将表格建模为节点 e.g. "内部" "岗位" "领队安排"
2. 将软件中的函数建模为边 e.g. "内部" -> "领队安排", "岗位" -> "领队安排"。
3. 整个依赖关系建模为图 (graph) 
4. 对于一个节点，没有边指向它（入度=0） e.g. "内部"：是外部输入（交大问卷、第二课堂）
5. 对于一个节点，没有边指出去（出度=0） e.g. "领队安排"：软件运行结果。
是我们最终需要的！这类节点："领队安排"、"面试时间安排"、"总表"、"车辆安排表"
6. 做控制？
- 建图：把文件之间的依赖关系在程序中表明。
- 输入目标：选一些要的结果表。
- 回溯：从目标节点出发，

回溯算法：
到达一个节点，观察其父亲节点

（存在，使用）从路径中直接用已经生成的表 / （不存在，生成，使用）回溯父亲节点，生成父亲节点。
（存在，覆盖）
（不存在，忽略）

直到目标节点生成。

### 2.2 第二阶段分工

并行1：张旭、朱乐涛、樊琪钰、胡泓峥
- 纸上建图：(讨论) 依赖
- 程序建图：(networkx)

并行2：王湘、杜楚恒、葛俊豪、李佶来、徐玺柠、赵元梓
- 简单读表
- 表格检查 （讨论）

### 2.3 建图

内部（交大问卷）
家属（交大问卷）
岗位（主办方）
-> 领队安排

招募总表（交大问卷）
面试场次表（手动输入）
-> 面试场次安排

面试官表（交大问卷）
<b>（多选算法）</b> 
面试场次表（手动输入）
-> 面试官场次安排（可选）

面试汇总表（手动输入）
-> 面试分数排名表

内部（交大问卷）
家属（交大问卷）
岗位（主办方）
领队安排 
面试分数排名表
情侣（交大问卷）
团体（团体给出）（特殊：摄影志愿者，分布不同）
超级志愿者（手动生成）
-> 总表

## 第三步：算法实现 (Equivalent Class)

### 3.1 冲突、约束解决方案

冲突：
1. 可简单避免的冲突。
- 内部人员不能又填内部又填家属。                          内部x家属
- 面试分数排名表直接删去内部、家属、团体、超级志愿者。      面试分数排名表x(内部|家属|团体)
- 把内部、家属、团体、超级志愿者设置为面试通过。计数。
- 计数，对`面试分数排名表`排序，可以得到通过名单、储备名单、未通过名单。

2. 需要处理：进软件前处理？进软件后处理？


- 家属、情侣、团体

约束 （满足硬约束，优化软约束）
- <b>通过x2</b>的情侣必须在一起。（<b>通过2</b>；通过+储备；储备2；通过+未通过；储备+未通过；未通过2）（满足硬约束）
- 家属可选是否在一起。（满足硬约束）
- 团体在一起。


- 团体最少能够分在n组，能保证他们一定分在 < n+2组，不一定连续（连续性不予考虑），同时担任小组长的成员及其情侣可能落单。（丑话先说）（优化软约束）


- 对于二元关系构建等价类（要在一起的，给他铁索连环）
~~~
binary_list = [["","",""],["","",""],["",""]]
~~~
对于二元关系（内部、情侣、家属）都可以解决
[a,b]
a,b out：加入[a,b]
a in, b out：把b加入a的list
a,b in：合并2个list

假定没有团体：一个list就安排一组嘛，如list里面有小组长，那么就放那里嘛。（假定铁索连环一个list不会撑爆一组）

- 对于多元关系
如果有团体：
估计需要的组数，指定组，如果团队有小组长，就指定小组长那个组。然后把含有团队成员的list取出（同时移除），先行填入这些组。假如组炸了，就再开。
就安排余下binary_list成员。（如同没有团体）（随机排组）

- 把剩余通过的人安排进组


3. 打印全表


4. 发短信拉群
发短信、通知前允许全部重新运行。

<b>一旦开始发短信拉群了，软件不再使用，也不允许塞人。</b>

可退出，正常补人，补人不再考虑约束，直接从储备表里拿人。


## Appendix 1

志愿者:

+ <u>学号</u>:string
+  姓名:string
+  拼音:string
+  性别:bool
+  证件类型:bool
+  身份证号:string 18位
+  出生日期:string
+  其他证件:string
+  学院:string
+  专业:string
+  班级:string
+  身高:float
+  邮箱:string ^[A-Za-z0-9-_\u4e00-\u9fa5]+ @[a-zA-Z0-9_-]+ (\.[a-zA-Z0-9_-]+ )+ $
+  电话:string 11位
+  QQ号:string
+  政治面貌:enum
+  参与次数:int
+  超级志愿者:bool
+  面试官:enum=none
+  面试得分:float=none
+  归一化分数:float=none

内部关系:
+  <u>学号</u>:string
+  职位:enum{小组长、区长、普通志愿者}

家属关系:
+  <u>内部成员学号</u>:string
+  家属:list[string]
+  是否和家属一组:list[bool]

情侣关系:
+  <u>学号1</u>:string
+  <u>学号2</u>:string

其他组织:
+  <u>组织名</u>:string
+  组织结构(学号):list[string]

小组:
+  <u>小组编号</u>:int
+  小组长(学号):string
+  岗位:string
+  当前小组人数:int
+  小组人数上限:int
+  小组成员(学号):list[string]
 
区:
+  <u>区编号</u>:int
+  区长(学号):string
+  下辖小组(编号):list[int]