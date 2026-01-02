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
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(referenceRepresentation=ON)
Mdb()
# =================================坐标显示==================================
session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)
# =================================修改工作目录==================================
workpath = r"D:\董珊珊\随机四边形批量化建模及结果后处理"
os.chdir(workpath)
num_models = 2
folder_paths = []

for i1 in range(num_models):  # 循环创建多个模型和结果文件
    folder_path = str(i1+1) + '\\结果文件'# 文件夹路径
    folder_paths.append(folder_path)  # 将文件夹路径添加到列表中

# 依次创建所有的文件夹
for folder_path in folder_paths:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Folder created successfully.")
    else:
        print("Folder already exists.")

# =================================再次修改工作目录==================================
for i1 in range(num_models):
    current_workpath = workpath + '\\' + str(i1+1)
    os.chdir(current_workpath)
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(0, 0), point2=(200, 100))
    p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-1']
    p.BaseSolidExtrude(sketch=s, depth=3)
    s.unsetPrimaryObject()
    del mdb.models['Model-1'].sketches['__profile__']
# ===================================创建基准平面===================================
    p = mdb.models['Model-1'].parts['Part-1']
    p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=2.7)
    p = mdb.models['Model-1'].parts['Part-1']
    p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=2.8)
# ===================================使用基准平面切分===================================
    session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)
    c = p.cells
    d = p.datums
    keys = mdb.models['Model-1'].parts['Part-1'].datums.keys()
    pickedCells = c.findAt(((200.0, 66.66667, 2), ))
    p.PartitionCellByDatumPlane(datumPlane=d[keys[1]], cells=pickedCells)
    pickedCells = c.findAt(((200.0, 66.66667, 1.86667), ))
    p.PartitionCellByDatumPlane(datumPlane=d[keys[0]], cells=pickedCells)
# ===================================划分网格===================================
# ===================================为边布种===================================
    e = p.edges
    pickedEdges = e.findAt(((0.0, 0.0, 2.725), ), ((0.0, 0.0, 0.675), ), ((0.0, 0.0, 2.85), ))
    p.seedEdgeByNumber(edges=pickedEdges, number=1, constraint=FINER)
    pickedEdges = e.findAt(((50.0, 0.0, 2.7), ), ((150.0, 100.0, 2.7), ), ((150.0, 100.0, 2.8), ), ((150.0, 0.0, 0.0), ), ((50.0, 0.0, 2.8), ), ((50.0, 100.0, 3.0), ), ((50.0, 100.0, 0.0), ), ((150.0, 0.0, 3.0), ))
    p.seedEdgeByNumber(edges=pickedEdges, number=200, constraint=FINER)
    pickedEdges = e.findAt(((0.0, 75.0, 2.7), ), ((200.0, 25.0, 2.7), ), ((200.0, 75.0, 0.0), ), ((0.0, 75.0, 2.8), ), ((200.0, 25.0, 2.8), ), ((200.0, 75.0, 3.0), ), ((0.0, 25.0, 0.0), ), ((0.0, 25.0, 3.0), ))
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
    pickedCellszhong = c.findAt(((200.0, 33.333333, 2.733333), ))
    p.assignStackDirection(referenceRegion=f.findAt(coordinates=(66.666667, 33.333333, 2.8)), cells=pickedCellszhong)
    pickedCellsdown = c.findAt(((200.0, 66.666667, 1.8), ))
    p.assignStackDirection(referenceRegion=f.findAt(coordinates=(66.666667, 33.333333, 2.7)), cells=pickedCellsdown)
#==================================创建节点集合===============================
    nodesm = p.nodes
    nodes_list = []
    nodes_list = [node for node in nodesm if 40 <= node.coordinates[0] <= 190 and node.coordinates[2] == 3 and node.coordinates[1] in range(5, 100, 5)]
    nl = []
    NodeList = []
    for n in range(len(nodes_list)):
        nl.append(nodes_list[n].label)
        NodeList.append(nodesm[nl[n]-1:nl[n]])
        
    nodelist_set = p.Set(nodes=NodeList, name='nodelist')
# ===================================选择单元集合===================================
    em = p.elements
    def distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
    def random_quadrilateral():
        while True:
            width = random.uniform(10, 31)
            height = 400 / width
            x1, y1 = random.uniform(40, 161), random.uniform(10, 61)
            x2, y2 = x1 + random.uniform(10, 31), y1 + random.uniform(10, 31)
            x4, y4 = x1 + width, y1 + height
            x3, y3 = x4 + random.uniform(-30, -11), y4 + random.uniform(-30, -11)
            x1, y1, x2, y2, x3, y3, x4, y4 = [round(float(i), 10) for i in [x1, y1, x2, y2, x3, y3, x4, y4]]
            dist12 = distance(x1, y1, x2, y2)
            dist13 = distance(x1, y1, x3, y3)
            dist14 = distance(x1, y1, x4, y4)
            dist23 = distance(x2, y2, x3, y3)
            dist24 = distance(x3, y3, x4, y4)
            if abs(width * height - 400) < 1:
                if height >= 10 and min(y1, y2, y3, y4) >= 0 and max(y1, y2, y3, y4) <= 100 and min(x1, x2, x3, x4) >= 40 and max(x1, x2, x3, x4) <= 190 and all(dist >= 10 for dist in [dist12, dist13, dist14, dist23, dist24]):
                # 语句块:
                    break
        return x1, y1, x2, y2, x3, y3, x4, y4
        
    x1, y1, x2, y2, x3, y3, x4, y4 = random_quadrilateral()
    print(x1, y1, x2, y2, x3, y3 , x4, y4)
    mdb.Model(name='Model-2', modelType=STANDARD_EXPLICIT)
    while True:
        points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        try:
            # 创建草图对象
            sc = mdb.models['Model-2'].ConstrainedSketch(name='random_sketch', sheetSize=200.0)
            gr, vr, dr, cr = sc.geometry, sc.vertices, sc.dimensions, sc.constraints
            sc.setPrimaryObject(option=STANDALONE)
            sc.rectangle(point1=(0.0, 0.0), point2=(200.0, 100.0))
            # 将相邻的点依次连接起来
            random.shuffle(points)
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
        return (cross1 >= 0 and cross2 >= 0 and cross3 >= 0) or (cross1 <= 0 and cross2 <= 0 and cross3 <= 0) or (cross1 == 0) or (cross2 == 0) or (cross3 == 0)
        
    def is_point_in_quadrilateral(x, y, x1, y1, x2, y2, x3, y3, x4, y4):
        # Check if the point is within the four triangles formed by the four edges of the quadrilateral
        return is_point_in_triangle(x, y, x1, y1, x2, y2, x3, y3) or is_point_in_triangle(x, y, x1, y1, x4, y4, x3, y3) or is_point_in_triangle(x, y, x1, y1, x4, y4, x2, y2) or is_point_in_triangle(x, y, x2, y2, x3, y3, x4, y4)
        
    # Determine the bounding box of the quadrilateral
    min_x = min(x1, x2, x3, x4)
    max_x = max(x1, x2, x3, x4)
    min_y = min(y1, y2, y3, y4)
    max_y = max(y1, y2, y3, y4)
    def generate_points_in_quadrilateral(x1, y1, x2, y2, x3, y3, x4, y4):
        # Generate a list of points within the bounding box
        points = []
        for x in np.concatenate((np.arange(min_x, max_x + 0.5, 0.5), np.arange(max_x, min_x - 0.5, - 0.5))):
            for y in np.concatenate((np.arange(min_y, max_y + 0.5, 0.5), np.arange(max_y, min_y - 0.5, - 0.5))):
                # Check if the point is within the quadrilateral
                if is_point_in_quadrilateral(x, y, x1, y1, x2, y2, x3, y3, x4, y4):
                    points.append((x, y))
        return points
        
    quadrilateral_points = generate_points_in_quadrilateral(x1, y1, x2, y2, x3, y3, x4, y4)
    elements_in_range = []
    elements_outxia_of_range = []
    elements_outshang_of_range = []
    elements_out1_range = []
    for element in em:
        node_coords = [node.coordinates for node in element.getNodes()]
        centroid = [sum(coords)/len(coords) for coords in zip(*node_coords)]
        minx = min([coord[0] for coord in node_coords])
        maxx = max([coord[0] for coord in node_coords])
        miny = min([coord[1] for coord in node_coords])
        maxy = max([coord[1] for coord in node_coords])
        if any((2.8 <= centroid[2]) for quadrilateral_point in quadrilateral_points):
            elements_outshang_of_range.append(element)
        elif any((centroid[2] <= 2.7) for quadrilateral_point in quadrilateral_points):
            elements_outxia_of_range.append(element)
        elif any((2.7<=centroid[2]<=2.8 and minx <= quadrilateral_point[0] <= maxx and miny <= quadrilateral_point[1] <= maxy) for quadrilateral_point in quadrilateral_points):
            elements_in_range.append(element)
        elif any((2.7<=centroid[2]<=2.8 and not (minx <= quadrilateral_point[0] <= maxx and miny <= quadrilateral_point[1] <= maxy)) for quadrilateral_point in quadrilateral_points):
            elements_out1_range.append(element)
            
    Ls=[]
    elements_in_rangeset=[]
    for i in range(len(elements_in_range)):
        Ls.append(elements_in_range[i].label)
        elements_in_rangeset.append(em[Ls[i]-1:Ls[i]])
        
    sunshang_set = p.Set(elements=elements_in_rangeset, name='Set-sunshang')
    Lfs=[]
    elements_outshang_of_rangeset=[]
    for j in range(len(elements_outshang_of_range)):
        Lfs.append(elements_outshang_of_range[j].label)
        elements_outshang_of_rangeset.append(em[Lfs[j]-1:Lfs[j]])
        
    fucaishang_set = p.Set(elements=elements_outshang_of_rangeset, name='Set-fucaishang')
    Lfx=[]
    elements_outxia_of_rangeset=[]
    for jj in range(len(elements_outxia_of_range)):
        Lfx.append(elements_outxia_of_range[jj].label)
        elements_outxia_of_rangeset.append(em[Lfx[jj]-1:Lfx[jj]])
        
    fucaixia_set = p.Set(elements=elements_outxia_of_rangeset, name='Set-fucaixia')
    Lf1=[]
    elements_out1_rangeset=[]
    for jjj in range(len(elements_out1_range)):
        Lf1.append(elements_out1_range[jjj].label)
        elements_out1_rangeset.append(em[Lf1[jjj]-1:Lf1[jjj]])
        
    fucai1_set = p.Set(elements=elements_out1_rangeset, name='Set-fucai1')
    #检查
    print(x1, y1, x2, y2, x3, y3 , x4, y4)
    print(quadrilateral_points)
    #检查
    is_point_in_triangle(x1, y1, x1, y1, x2, y2, x3, y3)
# ===================================定义材料===================================
# ===================================从材料库中导入材料===================================
    from material import createMaterialFromDataString
    createMaterialFromDataString('Model-1', 'CFRP-T300', '2020', """{'name': 'CFRP-T300', 'materialIdentifier': '', 'description': '', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((144000.0, 9300.0, 9300.0, 0.312, 0.312, 0.32, 4680.0, 4680.0, 4000.0),), 'type': ENGINEERING_CONSTANTS}, 'density': {'temperatureDependency': OFF, 'table': ((1.75,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}}""")
    from material import createMaterialFromDataString
    createMaterialFromDataString('Model-1', 'my-sunshang', '2020', """{'name': 'my-sunshang', 'materialIdentifier': '', 'description': '', 'elastic': {'temperatureDependency': OFF, 'moduli': LONG_TERM, 'noCompression': OFF, 'noTension': OFF, 'dependencies': 0, 'table': ((1.0, 1.0, 1.0, 0.312, 0.312, 0.32, 1.0, 1.0, 1.0),), 'type': ENGINEERING_CONSTANTS}, 'density': {'temperatureDependency': OFF, 'table': ((1.75,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}}""")
# ===================================为剩余完整30层单元集合赋予T300材料属性===================================
# =================================在编辑复合层界面中创建直角坐标系==================================
    vp, ep = p.vertices, p.edges
    p.DatumCsysByThreePoints(origin=vp.findAt(coordinates=(0.0, 0.0, 0.0)), name='Datum csys-1', coordSysType=CARTESIAN, point1=p.InterestingPoint(edge=ep.findAt(coordinates=(150.0, 0.0, 0.0)), rule=MIDDLE), point2=p.InterestingPoint(edge=e.findAt(coordinates=(0.0, 25, 0.0)), rule=MIDDLE))
# ===================================编辑复合层===================================
# ===================================上2层===================================
    key=mdb.models['Model-1'].parts['Part-1'].datums.keys()
    layupOrientation = mdb.models['Model-1'].parts['Part-1'].datums[key[2]]
    region1=p.sets['Set-fucaishang']
    region2=p.sets['Set-fucaishang']
    compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(name='CompositeLayup-1', description='', elementType=SOLID, symmetric=False, thicknessAssignment=FROM_SECTION)
    compositeLayup.ReferenceOrientation(orientationType=SYSTEM, localCsys=layupOrientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3)
    compositeLayup.CompositePly(suppressed=False, plyName='层-29', region=region1, material='CFRP-T300', thicknessType=SPECIFY_THICKNESS, thickness=1.0, orientationType=SPECIFY_ORIENT, orientationValue=0.0, additionalRotationType=ROTATION_NONE, additionalRotationField='', axis=AXIS_3, angle=0.0, numIntPoints=1)
    compositeLayup.CompositePly(suppressed=False, plyName='层-30', region=region2, material='CFRP-T300', thicknessType=SPECIFY_THICKNESS, thickness=1.0, orientationType=SPECIFY_ORIENT, orientationValue=90.0, additionalRotationType=ROTATION_NONE, additionalRotationField='', axis=AXIS_3, angle=0.0, numIntPoints=1)
# ===================================中1层===================================
    region3=p.sets['Set-fucai1']
    compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(name='CompositeLayup-2', description='', elementType=SOLID,symmetric=False, thicknessAssignment=FROM_SECTION)
    compositeLayup.ReferenceOrientation(orientationType=SYSTEM, localCsys=layupOrientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3)
    compositeLayup.CompositePly(suppressed=False, plyName='层-28', region=region3, material='CFRP-T300', thicknessType=SPECIFY_THICKNESS, thickness=1.0, orientationType=SPECIFY_ORIENT, orientationValue=90.0, additionalRotationType=ROTATION_NONE, additionalRotationField='', axis=AXIS_3, angle=0.0, numIntPoints=1)
# ===================================中损伤层===================================
    region4=p.sets['Set-sunshang']
    compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(name='CompositeLayup-3', description='', elementType=SOLID, symmetric=False, thicknessAssignment=FROM_SECTION)
    compositeLayup.ReferenceOrientation(orientationType=SYSTEM, localCsys=layupOrientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3)
    compositeLayup.CompositePly(suppressed=False, plyName='层-28', region=region4, material='my-sunshang', thicknessType=SPECIFY_THICKNESS, thickness=1.0, orientationType=SPECIFY_ORIENT, orientationValue=90.0, additionalRotationType=ROTATION_NONE, additionalRotationField='', axis=AXIS_3, angle=0.0, numIntPoints=1)
# ===================================下27层===================================
    compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(name='CompositeLayup-4', description='', elementType=SOLID, symmetric=False, thicknessAssignment=FROM_SECTION)
    compositeLayup.ReferenceOrientation(orientationType=SYSTEM, localCsys=layupOrientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3)
    #法一
    for i in range(1, 28):
        region5 = p.sets['Set-fucaixia']
        plyName = '层-' + str(i)
        orientationValue = 0.0 if i % 2 == 1 else 90.0
        compositeLayup.CompositePly(suppressed=False, plyName=plyName, region=region5,material='CFRP-T300', thicknessType=SPECIFY_THICKNESS, thickness=1.0,orientationType=SPECIFY_ORIENT, orientationValue=orientationValue,additionalRotationType=ROTATION_NONE, additionalRotationField='',axis=AXIS_3, angle=0.0, numIntPoints=1)
        
# ==================================创建装配体==================================
    a = mdb.models['Model-1'].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    a.Instance(name='Part-1-1', part=p, dependent=ON)
# ==================================创建分析步==================================
    mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
    mdb.models['Model-1'].FieldOutputRequest(name='F-Output-1', createStepName='Step-1', variables=('E', ), layupNames=('Part-1-1.CompositeLayup-1', ), layupLocationMethod=SPECIFIED, outputAtPlyTop=False, outputAtPlyMid=True, outputAtPlyBottom=False, rebar=EXCLUDE)
    mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2', createStepName='Step-1', variables=('E', ), layupNames=('Part-1-1.CompositeLayup-2', ), layupLocationMethod=SPECIFIED, outputAtPlyTop=False, outputAtPlyMid=True, outputAtPlyBottom=False, rebar=EXCLUDE)
    mdb.models['Model-1'].FieldOutputRequest(name='F-Output-3', createStepName='Step-1', variables=('E', ), layupNames=('Part-1-1.CompositeLayup-3', ), layupLocationMethod=SPECIFIED, outputAtPlyTop=False, outputAtPlyMid=True, outputAtPlyBottom=False, rebar=EXCLUDE)
    mdb.models['Model-1'].FieldOutputRequest(name='F-Output-4', createStepName='Step-1', variables=('E', ), layupNames=('Part-1-1.CompositeLayup-4', ), layupLocationMethod=SPECIFIED, outputAtPlyTop=False, outputAtPlyMid=True, outputAtPlyBottom=False, rebar=EXCLUDE)
# =================================定义边界条件=================================
    f1 = a.instances['Part-1-1'].faces
    facesg = f1.findAt(((0.0, 66.66667, 2.73333), ), ((0.0, 33.33333, 1.8), ), ((0.0, 66.66667, 2.86667), ))
    regiong = regionToolset.Region(faces=facesg)
    mdb.models['Model-1'].EncastreBC(name='BC-1', createStepName='Step-1', region=regiong, localCsys=None)
    facesz = f1.findAt(((200.0, 66.66667, 1.8), ), ((200.0, 33.33333, 2.86667), ), ((200.0, 33.33333, 2.73333), ))
    regionz = regionToolset.Region(faces=facesz)
    for zh in range(2):
        u =(zh+1)
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1', region=regionz, u1=UNSET, u2=UNSET, u3=-u, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
        #a.regenerate()
# ==============================创建作业并提交分析==============================
        jobName = "Job-" + str(u)
        mdb.Job(name=jobName, model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=6, numDomains=6, numGPUs=0)
        mdb.jobs[jobName].submit(consistencyChecking=OFF)
        mdb.jobs[jobName].waitForCompletion()
        
        #==================================进入后处理模块===============================
        
        odb = session.openOdb(name=current_workpath + "\\" + jobName + ".odb")
        session.viewports['Viewport: 1'].setValues(displayedObject=odb)
        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='E', outputPosition=INTEGRATION_POINT, refinement=(COMPONENT, 'E11'), )
#==================================获取节点label===============================
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
        nodeLabels = find_node_labels(coordinatePositions, 'Model-1', 'Part-1')
        print("nodeLabel:", nodeLabels)
        session.Path(name='Path-1', type=NODE_LIST, expression=(('PART-1-1', (nodeLabels[0], nodeLabels[1], nodeLabels[2], 
        nodeLabels[3], nodeLabels[4], nodeLabels[5], nodeLabels[6], nodeLabels[7], nodeLabels[8], nodeLabels[9], nodeLabels[10], 
        nodeLabels[11], nodeLabels[12], nodeLabels[13], nodeLabels[14], nodeLabels[15], nodeLabels[16], nodeLabels[17], nodeLabels[18], 
        nodeLabels[19], nodeLabels[20], nodeLabels[21], nodeLabels[22], nodeLabels[23], nodeLabels[24], nodeLabels[25], nodeLabels[26], 
        nodeLabels[27], nodeLabels[28], nodeLabels[29], nodeLabels[30], nodeLabels[31], nodeLabels[32], nodeLabels[33], nodeLabels[34], 
        nodeLabels[35], nodeLabels[36], nodeLabels[37], )), ))
        pth = session.paths['Path-1']
        session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=True, projectOntoMesh=False, pathStyle=PATH_POINTS, numIntervals=10, projectionTolerance=0, shape=UNDEFORMED, labelType=X_COORDINATE, removeDuplicateXYPairs=True, includeAllElements=False)
        
#==================================数据保存至txt or rpt===============================
        x0 = session.xyDataObjects['XYData-1']
        session.xyReportOptions.setValues(numDigits=8)
        Fm = current_workpath + "\\结果文件" + "\\abaqus" + str(u) + ".rpt"
        session.writeXYReport(fileName=Fm, xyData=(x0, ))
#==================================保存模型===============================
    mdb.saveAs(pathName=current_workpath + "\\test" + str(i1+1))


