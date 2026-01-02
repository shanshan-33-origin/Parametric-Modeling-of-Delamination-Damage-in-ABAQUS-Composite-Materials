# 大连理工大学24年毕业生力航院董珊珊硕士期间自主编写的复合材料分层损伤、裂纹损伤参数化建模及ABAQUS后处理脚本，Python二次开发，把脚本代码直接复制到ABAQUS，软件自动建模、自动创建损伤、自动计算、自动导出计算结果文件
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=328.551544189453, height=189.933334350586)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
import os
import random
import numpy as np
import math
import csv
import shutil
#import win32com.client as wincl
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(referenceRepresentation=ON)
Mdb()
# =================================坐标显示==================================
session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)
# =================================修改工作目录==================================
workpath = r"F:\四边形节点分离\处理\dongdong\0_90_2.7"
os.chdir(workpath)
num_models = 50
for i1 in range(25,num_models):  # 循环创建多个模型和结果文件
    folder_path = workpath + "\\" + str(i1+1) + '\jieguo'  # 文件夹路径
    if not os.path.exists(folder_path):  # 如果该文件夹不存在
        os.makedirs(folder_path)  # 创建该文件夹及其父级文件夹
        print("Folder created successfully.")
    else:
        print("Folder already exists.")
# =================================再次修改工作目录==================================
    current_workpath = workpath + '\\' + str(i1+1)
    os.chdir(current_workpath)
# =================================Part==================================
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(0, 0), point2=(200, 100))
    p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-1']
    p.BaseSolidExtrude(sketch=s, depth=3)
    s.unsetPrimaryObject()
    del mdb.models['Model-1'].sketches['__profile__']
# ===================================划分网格===================================
# ===================================为边布种===================================
    ep = p.edges
    pickedEdges = ep.findAt(((200.0, 0.0, 0.675), ), ((200.0, 100.0, 0.675), ), ((0.0, 0.0, 0.675), ), ((0.0, 100.0, 0.675), ))
    p.seedEdgeByNumber(edges=pickedEdges, number=30, constraint=FINER)
    pickedEdges = ep.findAt(((150.0, 0.0, 0.0), ), ((50.0, 100.0, 3.0), ), ((50.0, 100.0, 0.0), ), ((150.0, 0.0, 3.0), ))
    p.seedEdgeByNumber(edges=pickedEdges, number=200, constraint=FINER)
    pickedEdges = ep.findAt(((200.0, 75.0, 0.0), ), ((200.0, 75.0, 3.0), ), ((0.0, 25.0, 0.0), ), ((0.0, 25.0, 3.0), ))
    p.seedEdgeByNumber(edges=pickedEdges, number=100, constraint=FINER)
# ===================================指派全局种子===================================
    p.seedPart(size=1, deviationFactor=0.1, minSizeFactor=0.1)
# ===================================为部件划分网格===================================
    p.generateMesh()
# ===================================指派叠层方向===================================
# 顶面棕色是上表面，底面紫色是下表面，铺层是从底到顶，即从紫色面到棕色面
    c = p.cells
    f = p.faces
    pickedCellsup = c.findAt(((200.0, 33.333333, 2.866667), ))
    p.assignStackDirection(referenceRegion=f.findAt(coordinates=(66.666667, 33.333333, 3.0)), cells=pickedCellsup)
# ===================================选择几何阶次为二次===================================
    #elemType1 = mesh.ElemType(elemCode=C3D20R, elemLibrary=STANDARD)
    #elemType2 = mesh.ElemType(elemCode=C3D15, elemLibrary=STANDARD)
    #elemType3 = mesh.ElemType(elemCode=C3D10, elemLibrary=STANDARD)
    #cells = c.findAt(((200.0, 66.666667, 2.0), ))
    #pickedRegions =(cells, )
    #p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
# ===================================以下是默认的几何阶次为线性，是默认的不需要特意指定（即下面代码可有可无）===================================
#    elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF, hourglassControl=DEFAULT, distortionControl=DEFAULT)
#    elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD)
#    elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
#    cells = c.findAt(((200.0, 66.666667, 2.0), ))
#    pickedRegions =(cells, )
#    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
# ===================================选择单元集合===================================
    def read_csv_file(file_path):
        data = []  # 创建一个空列表，用于存储数据
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)  # 使用制表符作为分隔符
            for row in csv_reader:
                if len(row) > 1 and row[0] != 'Area':  # 忽略空行和表头
                    xy_values = [float(val) for val in re.findall(r'\d+\.\d+', row[1])]  # 使用正则表达式提取坐标值然后将字符串形式的浮点数值转换为浮点数
                    data.append(xy_values)  # 将坐标值列表添加到数据列表中
        return data
        
# 使用示例
    csv_file_path = r'F:\四边形节点分离\处理\dongdong\sui4areapoints.csv'
    csv_data = read_csv_file(csv_file_path)
    while True:
        em = p.elements
        x1, y1, x2, y2, x3, y3, x4, y4 = csv_data[i1][0], csv_data[i1][1], csv_data[i1][2], csv_data[i1][3], csv_data[i1][4], csv_data[i1][5], csv_data[i1][6], csv_data[i1][7]
        print(x1, y1, x2, y2, x3, y3, x4, y4)
        mdb.Model(name='Model-2', modelType=STANDARD_EXPLICIT)
        points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        while True:
            try:
                # 创建草图对象
                sc = mdb.models['Model-2'].ConstrainedSketch(name='random_sketch', sheetSize=200.0)
                gr, vr, dr, cr = sc.geometry, sc.vertices, sc.dimensions, sc.constraints
                sc.setPrimaryObject(option=STANDALONE)
                sc.rectangle(point1=(0.0, 0.0), point2=(200.0, 100.0))
                # 将相邻的点依次连接起来
                #random.shuffle(points)
                for i in range(3):
                    j = (i + 1)
                    p1 = points[i]
                    p2 = points[j]
                    sc.Line(point1=p1, point2=p2)
                sc.Line(point1=points[0], point2=points[-1])
                # 创建零件对象
                pr = mdb.models['Model-2'].Part(name='Part-Random', dimensionality=THREE_D, type=DEFORMABLE_BODY)
                # 创建实体拉伸特征
                pr.BaseSolidExtrude(sketch=sc, depth=0.1)
                print('实体拉伸特征创建成功')
                sc.unsetPrimaryObject()
                del mdb.models['Model-2'].sketches['random_sketch']
                break
            except:
                print('实体拉伸特征创建失败')
                random.shuffle(points)
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = points[0],points[1],points[2],points[3]
        print(x1, y1, x2, y2, x3, y3 , x4, y4)
        xy = x1, y1, x2, y2, x3, y3 , x4, y4
        def is_point_in_triangle(x, y, x1, y1, x2, y2, x3, y3):
            v1 = (x2-x1, y2-y1)
            v2 = (x-x1, y-y1)
            cross1 = v1[0]*v2[1] - v1[1]*v2[0]
            v1 = (x3-x2, y3-y2)
            v2 = (x-x2, y-y2)
            cross2 = v1[0]*v2[1] - v1[1]*v2[0]
            v1 = (x1-x3, y1-y3)
            v2 = (x-x3, y-y3)
            cross3 = v1[0]*v2[1] - v1[1]*v2[0]
            return (cross1 >= 0 and cross2 >= 0 and cross3 >= 0) or (cross1 <= 0 and cross2 <= 0 and cross3 <= 0)
            
        def is_point_in_quadrilateral(x, y, x1, y1, x2, y2, x3, y3, x4, y4):
            # Check if the point is within the four triangles formed by the four edges of the quadrilateral
            return is_point_in_triangle(x, y, x1, y1, x2, y2, x3, y3) or is_point_in_triangle(x, y, x1, y1, x4, y4, x3, y3)
            
        # Determine the bounding box of the quadrilateral
        min_x = min(x1, x2, x3, x4)
        max_x = max(x1, x2, x3, x4)
        min_y = min(y1, y2, y3, y4)
        max_y = max(y1, y2, y3, y4)
        def generate_points_in_quadrilateral(x1, y1, x2, y2, x3, y3, x4, y4):
            # Generate a list of points within the bounding box
            points_ = []
            for x in np.concatenate((np.arange(min_x, max_x + 0.5, 0.5), np.arange(max_x, min_x - 0.5, - 0.5))):
                for y in np.concatenate((np.arange(min_y, max_y + 0.5, 0.5), np.arange(max_y, min_y - 0.5, - 0.5))):
                    # Check if the point is within the quadrilateral
                    if is_point_in_quadrilateral(x, y, x1, y1, x2, y2, x3, y3, x4, y4):
                        points_.append((x, y))
            coordinates_with_half = [coordxy for coordxy in points_ if all(isinstance(val, float) and val % 1 == 0.5 for val in coordxy)]
            return coordinates_with_half
        quadrilateral_points = generate_points_in_quadrilateral(x1, y1, x2, y2, x3, y3, x4, y4)
        print(quadrilateral_points[0:5])
        elements_in_range = []
        # Create a dictionary to store elements for different ranges
        elements_outshang_ranges = {}
        for i in range(1, 31):
            elements_outshang_ranges[i] = []
        # Loop through the elements
        for element in em:
            node_coords = [node.coordinates for node in element.getNodes()]
            centroid = [sum(coords)/len(coords) for coords in zip(*node_coords)]
            minx = min([coord[0] for coord in node_coords])
            maxx = max([coord[0] for coord in node_coords])
            miny = min([coord[1] for coord in node_coords])
            maxy = max([coord[1] for coord in node_coords])
            for i in range(1, 31):
                if i == 30 and 2.9 <= centroid[2] <= 3.0:
                    elements_outshang_ranges[i].append(element)
                elif i == 1 and centroid[2] <= 0.1:
                    elements_outshang_ranges[i].append(element)
                elif (i - 1) * 0.1 <= centroid[2] <= i * 0.1:
                    elements_outshang_ranges[i].append(element)
                    if any((2.7 <= centroid[2] <= 2.8 and minx <= quadrilateral_point[0] <= maxx and miny <= quadrilateral_point[1] <= maxy) for quadrilateral_point in quadrilateral_points):
                        elements_in_range.append(element)
        # Extract the individual lists for each range if needed
        #elements_outshang1_of_range = elements_outshang_ranges[1]
        #检查
        print(len(elements_in_range))
        Larea = len(elements_in_range)
        if 400 <= len(elements_in_range) <= 410 and is_point_in_quadrilateral(x1, y1, x1, y1, x2, y2, x3, y3, x4, y4):
            break
    Ls=[]
    elements_in_rangeset=[]
    for i in range(len(elements_in_range)):
        Ls.append(elements_in_range[i].label)
        elements_in_rangeset.append(em[Ls[i]-1:Ls[i]])
    sunshang_set = p.Set(elements=elements_in_rangeset, name='Set-sunshang')
    # Initialize an empty list to store sets
    fucaishang_sets = []
    # Loop from 1 to 20
    for i in range(1, 31):
        Lfs = []
        elements_outshang_of_rangeset = []
        # Assuming `elements_outshang_of_range` and `em` are available
        # Populate Lfs and elements_outshang_of_rangeset lists
        elements_outshang_of_range = elements_outshang_ranges[i]
        for j in range(len(elements_outshang_of_range)):
            Lfs.append(elements_outshang_of_range[j].label)
            elements_outshang_of_rangeset.append(em[Lfs[j] - 1: Lfs[j]])
        # Create the set and append it to the fucaishang_sets list
        fucaishang_set = p.Set(elements=elements_outshang_of_rangeset, name='Set-fucaishang' + str(i))
        fucaishang_sets.append(fucaishang_set)
# ===================================修改工作===================================
# ===================================找到单元集合中的目标单元面和目标节点===================================
    p = mdb.models['Model-1'].parts['Part-1']
    setElem = p.sets['Set-sunshang'].elements
    elements_s = p.sets['Set-sunshang'].elements
    #nodes = p.sets['Set-sunshang'].nodes
    EF=[]
    EN=[]
    AllEN=[]
    for e in elements_s:
        for ef in e.getElemFaces():
            node_coords = [node.coordinates for node in ef.getNodes()]
            #法一
            if all((round(node_coord[2], 1) == 2.7) for node_coord in node_coords):
                EF.append(ef)
                EN.append(ef.getNodes())
            #法二
            #if not all((round(node_coord[2], 1) == 2.8) for node_coord in node_coords):
                #continue
            #EF.append(ef)
            #EN.append(ef.getNodes())
    AllEN.extend([en for tup in EN for en in tup])
# ===================================删除重复===================================
    def remove_duplicates(lst):
        # 使用列表推导式去除重复元素，并保持原列表顺序
        unique_list = [x for i, x in enumerate(lst) if x not in lst[:i]]
        return unique_list
        
    #EN = remove_duplicates(EN)
    AllEN = remove_duplicates(AllEN)
# ===================================检查是否有重复===================================
    def is_duplicate(lst):
        # Compare the lengths of the list and the list without duplicates
        if len(lst) == len(remove_duplicates(lst)):
            return False  # The list does not contain duplicate elements
        else:
            return True   # The list contains duplicate elements
    # 调用函数进行测试
    print(is_duplicate(AllEN)) # 输出: False则正确
# ===================================创建节点set===================================
    dw_nl = []
    dw_NodeList = []
    for n in range(len(AllEN)):
        dw_nl.append(AllEN[n].label)
        dw_NodeList.append(p.nodes[dw_nl[n]-1:dw_nl[n]])
        
    down_nodelist_set = p.Set(nodes=dw_NodeList, name='down_nodelist')
# ===================================定义从节点（单元面）找到所属单元===================================
    def get_elements_containing_elemNode(p, node):
        # Get the element
        elements_s = p.sets['Set-sunshang'].elements
        # Store the elements containing the specified element face
        containing_elements = []
        # Check if the specified element face is one of the element's faces
        for element in elements_s:
            if node.label in [n.label for n in element.getNodes()]:# node in element.getNodes() 也可以换成单元面if elemFace in element.getElemFaces():# elemFace.label in [ef.label for ef in element.getElemFaces()]，把def里面的参数node换成elemFace。
                containing_elements.append(element)
        return containing_elements
    containing_elementsnode = get_elements_containing_elemNode(p, AllEN[1])
# ===================================找到行中的值===================================
    containing_elements = []
    Node_label = []
    Node_index = []
    alln = len(p.nodes)
    new_node_step = alln + 1
    for index, node in enumerate(AllEN):
        node_index, x, y, z = index + new_node_step, node.coordinates[0], node.coordinates[1], node.coordinates[2]
        Node_label.append(node.label)
        Node_index.append(node_index)
        ee = get_elements_containing_elemNode(p, node)[0]
        if ee not in containing_elements:
            containing_elements.append(ee)
# ===================================定义材料===================================
# ===================================从材料库中导入材料===================================
    from material import createMaterialFromDataString
    createMaterialFromDataString('Model-1', 'CFRP-T300', '2020', """{'name': 'CFRP-T300', 'materialIdentifier': '', 'description': '', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((144000.0, 9300.0, 9300.0, 0.312, 0.312, 0.32, 4680.0, 4680.0, 4000.0),), 'type': ENGINEERING_CONSTANTS}, 'density': {'temperatureDependency': OFF, 'table': ((1.75,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}}""")
# ===================================为剩余完整30层单元集合赋予T300材料属性===================================
    session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)
# =================================在编辑复合层界面中创建直角坐标系==================================
    vp = p.vertices
    #p.DatumCsysByThreePoints(origin=vp.findAt(coordinates=(0.0, 0.0, 0.0)), name='Datum csys-1', coordSysType=CARTESIAN, point1=p.InterestingPoint(edge=ep.findAt(coordinates=(150.0, 0.0, 0.0)), rule=MIDDLE), point2=p.InterestingPoint(edge=ep.findAt(coordinates=(0.0, 25, 0.0)), rule=MIDDLE))
    p.DatumCsysByThreePoints(origin=vp.findAt(coordinates=(0.0, 0.0, 0.0)), point1=vp.findAt(coordinates=(200.0, 0.0, 0.0)), point2=vp.findAt(coordinates=(0.0, 100.0, 0.0)), name='Datum csys-1', coordSysType=CARTESIAN)
# ===================================编辑复合层===================================
# ===================================key===================================
    key=mdb.models['Model-1'].parts['Part-1'].datums.keys()
    layupOrientation = mdb.models['Model-1'].parts['Part-1'].datums[key[0]]
# ===================================30层===================================
    #compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(name='CompositeLayup-1', description='', elementType=SOLID, symmetric=False, thicknessAssignment=FROM_SECTION)
    #compositeLayup.ReferenceOrientation(orientationType=SYSTEM, localCsys=layupOrientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3)
    for i in range(1, 31):
        region = p.sets['Set-fucaishang' + str(i)]
        compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(name='CompositeLayup-'+ str(i), description='', elementType=SOLID, symmetric=False, thicknessAssignment=FROM_SECTION)
        compositeLayup.ReferenceOrientation(orientationType=SYSTEM, localCsys=layupOrientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3)
        plyName_down = '层-' + str(i)
        orientationValue = 0.0 if i % 2 == 1 else 90.0
        compositeLayup.CompositePly(suppressed=False, plyName=plyName_down, region=region,material='CFRP-T300', thicknessType=SPECIFY_THICKNESS, thickness=1.0,orientationType=SPECIFY_ORIENT, orientationValue=orientationValue,additionalRotationType=ROTATION_NONE, additionalRotationField='',axis=AXIS_3, angle=0.0, numIntPoints=1)
        
# ==================================创建装配体==================================
    a = mdb.models['Model-1'].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    a.Instance(name='Part-1-1', part=p, dependent=ON)
# ==================================创建分析步==================================
    mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
    #session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=('E', ))
    #mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=('E', ), sectionPoints=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30))
    for f in range(1, 31):
        layup_name = 'Part-1-1.CompositeLayup-' + str(f)
        output_name = 'F-Output-' + str(f)
        mdb.models['Model-1'].FieldOutputRequest(name=output_name, createStepName='Step-1', variables=('E', ), layupNames=(layup_name, ), layupLocationMethod=ALL_LOCATIONS, rebar=EXCLUDE)
# =================================定义边界条件=================================
    f1 = a.instances['Part-1-1'].faces
    facesg = f1.findAt(((0.0, 33.333333, 1.8), ))
    regiong = a.Set(faces=facesg, name='Set-1')
    mdb.models['Model-1'].EncastreBC(name='BC-1', createStepName='Step-1', region=regiong, localCsys=None)
    facesz = f1.findAt(((200.0, 33.333333, 2.88), ))
    regionz = a.Set(faces=facesz, name='Set-2')
    mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1', region=regionz, u1=UNSET, u2=UNSET, u3=-5, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
# ==============================创建作业并提交分析==============================
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    jobName = 'Job-' + str(1)
    mdb.Job(name=jobName, model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=32, numDomains=32, numGPUs=0)
    mdb.jobs[jobName].submit(consistencyChecking=OFF)
    mdb.jobs[jobName].waitForCompletion()
# ==================================复制.inp文件===============================
    # 定义源文件和目标文件的路径
    source_file = 'Job-1.inp'
    target_file = 'Job-1-fuben-' + str(5) + '.inp'
    # 检查目标文件是否已经存在
    if os.path.exists(target_file):
        print("目标文件已经存在！")
    else:
        # 复制文件
        shutil.copy2(source_file, target_file)
        print("文件复制成功！")
# ==================================修改.inp文件===============================
# ===================================添加行===================================
    # 输入文件路径
    input_file_path = current_workpath + "\\" + target_file
    # 临时文件路径
    temp_file_path_append = current_workpath + "\\" + 'tempap-' + target_file
    # 标记是否到达目标位置
    reached_target = False
    # 打开输入文件
    with open(input_file_path, 'r+') as input_file:
        # 读取所有行内容
        lines_a = input_file.readlines()
        # 查找目标位置
        for i_a, line_a in enumerate(lines_a):
            if line_a.strip().startswith(str(alln)) and lines_a[i_a+1].strip().startswith('*Element, type=C3D8R'):
                # 在目标位置之前插入新的内容
                new_content = ''
                for index, node in enumerate(AllEN):
                    node_index, x, y, z = index + new_node_step, node.coordinates[0], node.coordinates[1], node.coordinates[2]
                    new_line = '{:6d}, {:11.0f}, {:11.0f}, {:11.8f}\n'.format(node_index, x, y, z)
                    new_content += new_line
                # 在目标位置之前插入新内容
                lines_a = lines_a[:i_a+1] + new_content.splitlines(True) + lines_a[i_a+1:]
                reached_target = True
                break
                
    # 如果到达目标位置，则写入临时文件
    if reached_target:
        with open(temp_file_path_append, 'w') as temp_file:
            temp_file.writelines(lines_a)
            # 输出完成提示
            print("文件写入完成！")
    else:
        print("未找到目标位置！")
    # 关闭文件
    input_file.close()
    temp_file.close()
    # 替换原始输入文件
    #shutil.move(temp_file_path_append, input_file_path)# shutil.move(src,dst) 注意：文件/文件夹一旦被移动了，原来位置的文件/文件夹就没了。目标文件夹不存在时， 会报错
    shutil.copyfile(temp_file_path_append, input_file_path)# 原来位置的文件还在
    # 输出完成提示
    print("文件写入处理完成！")
# ===================================找到行中的值===================================
# ===================================替换行中的值===================================
    # 输入文件路径
    # 临时文件路径
    temp_file_path_replace = current_workpath + "\\" + 'temprp-' + target_file
    # 打开输入文件和临时文件
    with open(input_file_path, 'r') as input_file, open(temp_file_path_replace, 'w') as temp_file:
        # 标记是否在目标行范围内
        within_target_range = False
        # 逐行读取输入文件
        for line_r in input_file:
            # 判断是否进入目标行范围
            if line_r.strip().startswith('*Element, type=C3D8R'):
                within_target_range = True
            # 处理目标行范围内的行
            if within_target_range:
                # 查找需要替换的行
                for ec in containing_elements:
                    if line_r.lstrip().startswith(str(ec.label)):
                        # 构建替换的字符串
                        for i_r, label_r in enumerate(Node_label):
                            elems = line_r.rstrip().split(',')[1:]
                            for i_e, elem in enumerate(elems):
                                if str(label_r) == elem.strip():
                                    replacement = str(Node_index[i_r])
                                    line_r = line_r.replace(elems[i_e].strip(), replacement)
            # 写入当前行到临时文件
            temp_file.write(line_r)
            # 判断是否离开目标行范围
            if line_r.strip().startswith('*Elset, elset=Set-sunshang'):
                within_target_range = False
    # 关闭文件
    input_file.close()
    temp_file.close()
    # 替换原始输入文件
    #shutil.move(temp_file_path_replace, input_file_path)
    shutil.copyfile(temp_file_path_replace, input_file_path)
    # 输出完成提示
    print("文件处理完成！")
# ===================================导入.inp文件===================================
    input_file = input_file_path
    input_name = 'Job-1-fuben-' + str(5)
    mdb.ModelFromInputFile(name=input_name, inputFileName=input_file)
# ===================================修改载荷===================================
    #a = mdb.models['Job-1-副本-5'].rootAssembly
    #session.viewports['Viewport: 1'].setValues(displayedObject=a)
    #session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON, predefinedFields=ON, connectors=ON)
    #session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    start = 5
    scan = 5
    end = 50 + scan
    for u in range(start,end,scan):
        mdb.models['Job-1-fuben-5'].boundaryConditions['Disp-BC-2'].setValues(u3=-u)
# ===================================创建作业===================================
        jobName_2 = "Job-" + str(2)
        mdb.Job(name=jobName_2, model='Job-1-fuben-5', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=32, numDomains=32, numGPUs=0)
# ===================================提交作业===================================
        mdb.jobs[jobName_2].submit(consistencyChecking=OFF)
        mdb.jobs[jobName_2].waitForCompletion()
# ===================================进入可视化===================================
        odb = session.openOdb(name=current_workpath + r"\Job-2.odb")
        session.viewports['Viewport: 1'].setValues(displayedObject=odb)
        session.viewports['Viewport: 1'].makeCurrent()
# ===================================修改可视化===================================
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='E', outputPosition=INTEGRATION_POINT, refinement=(COMPONENT, 'E22'), )
        session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)# 画出云图
        session.viewports['Viewport: 1'].odbDisplay.setPrimarySectionPoint(activePly="层-30")
        session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionPointScheme=PLY_BASED, plyResultLocation=TOP)
        #session.viewports['Viewport: 1'].odbDisplay.setPrimarySectionPoint(sectionPoint={'solid < composite > < elset = ASSEMBLY_PART-1-1_COMPOSITELAYUP-2-1-1 >':('fraction = -0.962963, Layer = 1', 'fraction = 0.962963, Layer = 27'), 'solid < composite > < elset = ASSEMBLY_PART-1-1_COMPOSITELAYUP-1-1-1 >':('fraction = -0.666667, Layer = 1', 'fraction = 0.666667, Layer = 3')})
        #session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_TOP, sectionPointScheme=CATEGORY_BASED)
# ==================================获取节点label===============================
        def find_node_labels(coordinate_positions, model_name, part_name):
            # 获取模型和部件对象
            myModel = mdb.models[model_name]
            myPart = myModel.parts[part_name]
            nodes = myPart.nodes
            # 初始化保存节点标签的列表
            node_labels = []
            # 遍历坐标位置列表
            for position in coordinate_positions:
                x, y, z = position
                closestNode = None
                minDistance = float('inf')
                # 遍历节点并找到最接近的节点
                for node in nodes:
                    nodeX, nodeY, nodeZ = node.coordinates
                    distance = ((nodeX - x) ** 2 + (nodeY - y) ** 2 + (nodeZ - z) ** 2) ** 0.5
                    if distance < minDistance:
                        minDistance = distance
                        closestNode = node
                if closestNode is not None:
                    nodeLabel = closestNode.label
                    node_labels.append(nodeLabel)
                else:
                    node_labels.append(None)
            return node_labels
            
        node_z=3.0
        coordinatePositions = [(40.0, 5.0, node_z), (190.0, 5.0, node_z), (190, 10.0, node_z), (40.0, 10.0, node_z), (40.0, 15.0, node_z), 
        (190.0, 15.0, node_z), (190.0, 20.0, node_z), (40.0, 20.0, node_z), (40.0, 25.0, node_z), (190.0, 25.0, node_z), (190.0, 30.0, node_z), 
        (40.0, 30.0, node_z), (40.0, 35.0, node_z), (190.0, 35.0, node_z), (190.0, 40.0, node_z), (40.0, 40.0, node_z), (40.0, 45.0, node_z), 
        (190.0, 45.0, node_z), (190.0, 50.0, node_z), (40.0, 50.0, node_z), (40.0, 55.0, node_z), (190.0, 55.0, node_z), (190.0, 60.0, node_z), 
        (40.0, 60.0, node_z), (40.0, 65.0, node_z), (190.0, 65.0, node_z), (190.0, 70.0, node_z), (40.0, 70.0, node_z), (40.0, 75.0, node_z), 
        (190.0, 75.0, node_z), (190.0, 80.0, node_z), (40.0, 80.0, node_z), (40.0, 85.0, node_z), (190.0, 85.0, node_z), (190.0, 90.0, node_z), 
        (40.0, 90.0, node_z), (40.0, 95.0, node_z), (190.0, 95.0, node_z)]
# ===================================路径===================================
        nodeLabels = find_node_labels(coordinatePositions, 'Model-1', 'Part-1')
        print("nodeLabel:", nodeLabels)
        session.Path(name='Path-1', type=NODE_LIST, expression=(('PART-1-1', (nodeLabels[0], nodeLabels[1], nodeLabels[2], 
        nodeLabels[3], nodeLabels[4], nodeLabels[5], nodeLabels[6], nodeLabels[7], nodeLabels[8], nodeLabels[9], nodeLabels[10], 
        nodeLabels[11], nodeLabels[12], nodeLabels[13], nodeLabels[14], nodeLabels[15], nodeLabels[16], nodeLabels[17], nodeLabels[18], 
        nodeLabels[19], nodeLabels[20], nodeLabels[21], nodeLabels[22], nodeLabels[23], nodeLabels[24], nodeLabels[25], nodeLabels[26], 
        nodeLabels[27], nodeLabels[28], nodeLabels[29], nodeLabels[30], nodeLabels[31], nodeLabels[32], nodeLabels[33], nodeLabels[34], 
        nodeLabels[35], nodeLabels[36], nodeLabels[37], )), ))
        pth = session.paths['Path-1']
        session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=True, projectOntoMesh=False, pathStyle=PATH_POINTS, numIntervals=10, projectionTolerance=0, shape=DEFORMED, labelType=X_COORDINATE, removeDuplicateXYPairs=True, includeAllElements=False)# 注意：shape参数我改成了已变形DEFORMED，未变形是UNDEFORMED，之前的脚本都是未变形参数设置的shape=UNDEFORMED，节点分离法的脚本改成了已变形shape=DEFORMED。
# ===================================数据保存至txt or rpt===================================
        x0 = session.xyDataObjects['XYData-1']
        session.xyReportOptions.setValues(numDigits=8)
        Fm = current_workpath + r"\jieguo\abaqus" + str(u) + ".rpt"
        session.writeXYReport(fileName=Fm, xyData=(x0, ))
# ===================================保存模型===================================
    mdb.saveAs(pathName=current_workpath + r"\jieguo\test" + str(i1+1))
    filename_xy = "26_50_xy_0_90_2.7.csv"
    # 指定要保存的文件路径
    file_path_xy = os.path.join(workpath, filename_xy)
    file_exists_xy = os.path.exists(file_path_xy)
    # 写入数据到 .csv 文件
    with open(file_path_xy, mode='a') as file_xy:
        writer_xy = csv.writer(file_xy)
        if not file_exists_xy:
            writer_xy.writerow(['Area', 'xy'])
        writer_xy.writerow([Larea, xy])
        #file_xy.write(os.linesep)
    print("数据已成功写入 CSV 文件。")
    filename_x_y = "26_50_x_y_0_90_2.7.csv"
    # 指定要保存的文件路径
    file_path_x_y = os.path.join(workpath, filename_x_y)
    file_exists_x_y = os.path.exists(file_path_x_y)
    # 写入数据到 .csv 文件
    with open(file_path_x_y, mode='a') as file_x_y:
        writer_x_y = csv.writer(file_x_y)
        if not file_exists_x_y:
            writer_x_y.writerow(['Area', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4'])
        writer_x_y.writerow([Larea, x1, y1, x2, y2, x3, y3, x4, y4])
        #file_x_y.write(os.linesep)
    print("数据已成功写入 CSV 文件。")


