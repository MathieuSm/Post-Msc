# 00 Initialization
import os
import numpy as np
import pandas as pd
import SimpleITK as sitk
import matplotlib
matplotlib.use('WebAgg')
import matplotlib.pyplot as plt

desired_width = 500
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', desired_width)
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width,suppress=True,formatter={'float_kind':'{:3}'.format})


## Define function
def GetFabricInfos(FabricFile):
    FabricFile = open(FabricFile, 'r')
    FabricText = FabricFile.read()
    FabricLines = FabricText.split('\n')

    for Index in range(len(FabricLines)):

        if 'BV/TV' in FabricLines[Index]:
            BVTV = np.float(FabricLines[Index].split()[-1])

        if 'Eigen values' in FabricLines[Index]:
            m1 = np.float(FabricLines[Index].split()[5])
            m2 = np.float(FabricLines[Index].split()[6])
            m3 = np.float(FabricLines[Index].split()[7])

            DA = np.round(max(m1,m2,m3)/min(m1,m2,m3),3)

        if 'Eigen vector 1' in FabricLines[Index]:
            m1Vector = np.array([np.float(FabricLines[Index].split()[6]),
                                 np.float(FabricLines[Index].split()[7]),
                                 np.float(FabricLines[Index].split()[8])])

        if 'Eigen vector 2' in FabricLines[Index]:
            m2Vector = np.array([np.float(FabricLines[Index].split()[6]),
                                 np.float(FabricLines[Index].split()[7]),
                                 np.float(FabricLines[Index].split()[8])])

        if 'Eigen vector 3' in FabricLines[Index]:
            m3Vector = np.array([np.float(FabricLines[Index].split()[6]),
                                 np.float(FabricLines[Index].split()[7]),
                                 np.float(FabricLines[Index].split()[8])])

    FabricInfosData = pd.DataFrame()

    FabricInfos = {'BVTV':BVTV,'m1':m1,'m2':m2,'m3':m3,'DA':DA,
                   'm11':m1Vector[0],'m21':m1Vector[1],'m31':m1Vector[2],
                   'm12':m2Vector[0],'m22':m2Vector[1],'m32':m2Vector[2],
                   'm13':m3Vector[0],'m23':m3Vector[1],'m33':m3Vector[2]}

    FabricInfosData = FabricInfosData.append(FabricInfos,ignore_index=True)

    return FabricInfosData
def SortFabric(FabricData):

    ## Sort eigenvalues
    m1 = np.min(FabricData[['m1', 'm2', 'm3']].values)
    m2 = np.median(FabricData[['m1', 'm2', 'm3']].values)
    m3 = np.max(FabricData[['m1', 'm2', 'm3']].values)
    m = [m1, m2, m3]

    ## Sort eigenvectors according to the eigenvalues
    if m1 == FabricData['m1'].values[0]:
        m1v = FabricData[['m11', 'm21', 'm31']].values[0]
    elif m1 == FabricData['m2'].values[0]:
        m1v = FabricData[['m12', 'm22', 'm32']].values[0]
    elif m1 == FabricData['m3'].values[0]:
        m1v = FabricData[['m13', 'm23', 'm33']].values[0]

    if m2 == FabricData['m1'].values[0]:
        m2v = FabricData[['m11', 'm21', 'm31']].values[0]
    elif m2 == FabricData['m2'].values[0]:
        m2v = FabricData[['m12', 'm22', 'm32']].values[0]
    elif m2 == FabricData['m3'].values[0]:
        m2v = FabricData[['m13', 'm23', 'm33']].values[0]

    if m3 == FabricData['m1'].values[0]:
        m3v = FabricData[['m11', 'm21', 'm31']].values[0]
    elif m3 == FabricData['m2'].values[0]:
        m3v = FabricData[['m12', 'm22', 'm32']].values[0]
    elif m3 == FabricData['m3'].values[0]:
        m3v = FabricData[['m13', 'm23', 'm33']].values[0]

    mv = [m1v, m2v, m3v]

    return m, mv
def GetComplianceMatrix(FUAnalyzedFile):

    File  = open(FUAnalyzedFile, 'r')
    Text  = File.read()
    Lines = Text.split('\n')

    Index = 0
    while 'COMPLIANCE Matrix' not in Lines[Index]:
        Index += 1

    SymmetrizationFactor = np.float(Lines[Index+2][0])

    ComplianceMatrix = np.zeros((6,6))

    for i in range(6):
        for j in range(6):
            ComplianceMatrix[i,j] = np.float(Lines[Index + 4 + i].split()[j])

    return ComplianceMatrix

    # Compute the missing constants
    Nu21 = Nu12 * E2 / E1
    Nu31 = Nu13 * E3 / E1
    Nu32 = Nu23 * E3 / E2
    Mu21 = Mu12
    Mu31 = Mu13
    Mu32 = Mu23

    EngineeringConstants = {'E1': E1, 'E2': E2, 'E3': E3,
                            'Mu23': Mu23, 'Mu31': Mu31, 'Mu12': Mu12,
                            'Nu23': Nu23, 'Nu31': Nu31, 'Nu12': Nu12,
                            'Nu32': Nu32, 'Nu13': Nu13, 'Nu21': Nu21}

    return EngineeringConstants
def CheckMinorSymmetry(A):
    MinorSymmetry = True
    for i in range(3):
        for j in range(3):
            PartialTensor = A[:,:, i, j]
            if PartialTensor[1, 0] == PartialTensor[0, 1] and PartialTensor[2, 0] == PartialTensor[0, 2] and PartialTensor[1, 2] == PartialTensor[2, 1]:
                MinorSymmetry = True
            else:
                MinorSymmetry = False
                break

    if MinorSymmetry == True:
        for i in range(3):
            for j in range(3):
                PartialTensor = np.squeeze(A[i, j,:,:])
                if PartialTensor[1, 0] == PartialTensor[0, 1] and PartialTensor[2, 0] == PartialTensor[0, 2] and PartialTensor[1, 2] == PartialTensor[2, 1]:
                    MinorSymmetry = True
                else:
                    MinorSymmetry = False
                    break

    return MinorSymmetry
def IsoMorphism3333_66(A):

    if CheckMinorSymmetry == False:
        print('Tensor does not present minor symmetry')
    else:

        if isinstance(A[0, 0, 0, 0], np.float):
            B = np.zeros((6,6))
        else:
            B = sp.zeros(6)

        B[0, 0] = A[0, 0, 0, 0]
        B[0, 1] = A[0, 0, 1, 1]
        B[0, 2] = A[0, 0, 2, 2]
        B[0, 3] = np.sqrt(2) * A[0, 0, 1, 2]
        B[0, 4] = np.sqrt(2) * A[0, 0, 2, 0]
        B[0, 5] = np.sqrt(2) * A[0, 0, 0, 1]

        B[1, 0] = A[1, 1, 0, 0]
        B[1, 1] = A[1, 1, 1, 1]
        B[1, 2] = A[1, 1, 2, 2]
        B[1, 3] = np.sqrt(2) * A[1, 1, 1, 2]
        B[1, 4] = np.sqrt(2) * A[1, 1, 2, 0]
        B[1, 5] = np.sqrt(2) * A[1, 1, 0, 1]

        B[2, 0] = A[2, 2, 0, 0]
        B[2, 1] = A[2, 2, 1, 1]
        B[2, 2] = A[2, 2, 2, 2]
        B[2, 3] = np.sqrt(2) * A[2, 2, 1, 2]
        B[2, 4] = np.sqrt(2) * A[2, 2, 2, 0]
        B[2, 5] = np.sqrt(2) * A[2, 2, 0, 1]

        B[3, 0] = np.sqrt(2) * A[1, 2, 0, 0]
        B[3, 1] = np.sqrt(2) * A[1, 2, 1, 1]
        B[3, 2] = np.sqrt(2) * A[1, 2, 2, 2]
        B[3, 3] = 2 * A[1, 2, 1, 2]
        B[3, 4] = 2 * A[1, 2, 2, 0]
        B[3, 5] = 2 * A[1, 2, 0, 1]

        B[4, 0] = np.sqrt(2) * A[2, 0, 0, 0]
        B[4, 1] = np.sqrt(2) * A[2, 0, 1, 1]
        B[4, 2] = np.sqrt(2) * A[2, 0, 2, 2]
        B[4, 3] = 2 * A[2, 0, 1, 2]
        B[4, 4] = 2 * A[2, 0, 2, 0]
        B[4, 5] = 2 * A[2, 0, 0, 1]

        B[5, 0] = np.sqrt(2) * A[0, 1, 0, 0]
        B[5, 1] = np.sqrt(2) * A[0, 1, 1, 1]
        B[5, 2] = np.sqrt(2) * A[0, 1, 2, 2]
        B[5, 3] = 2 * A[0, 1, 1, 2]
        B[5, 4] = 2 * A[0, 1, 2, 0]
        B[5, 5] = 2 * A[0, 1, 0, 1]

        return B
def IsoMorphism66_3333(A):

    # Check symmetry
    Symmetry = True
    for i in range(6):
        for j in range(6):
            if not A[i,j] == A[j,i]:
                Symmetry = False
                break
    if Symmetry == False:
        print('Matrix is not symmetric!')
        return



    if isinstance(A[0, 0], np.float):
        B = np.zeros((3,3,3,3))
    else:
        B = sp.zeros((3,3,3,3))

    # Build 4th tensor
    B[0, 0, 0, 0] = A[0, 0]
    B[1, 1, 0, 0] = A[1, 0]
    B[2, 2, 0, 0] = A[2, 0]
    B[1, 2, 0, 0] = A[3, 0] / np.sqrt(2)
    B[2, 0, 0, 0] = A[4, 0] / np.sqrt(2)
    B[0, 1, 0, 0] = A[5, 0] / np.sqrt(2)

    B[0, 0, 1, 1] = A[0, 1]
    B[1, 1, 1, 1] = A[1, 1]
    B[2, 2, 1, 1] = A[2, 1]
    B[1, 2, 1, 1] = A[3, 1] / np.sqrt(2)
    B[2, 0, 2, 1] = A[4, 1] / np.sqrt(2)
    B[0, 1, 2, 1] = A[5, 1] / np.sqrt(2)

    B[0, 0, 2, 2] = A[0, 2]
    B[1, 1, 2, 2] = A[1, 2]
    B[2, 2, 2, 2] = A[2, 2]
    B[1, 2, 2, 2] = A[3, 2] / np.sqrt(2)
    B[2, 0, 2, 2] = A[4, 2] / np.sqrt(2)
    B[0, 1, 2, 2] = A[5, 2] / np.sqrt(2)

    B[0, 0, 1, 2] = A[0, 3] / np.sqrt(2)
    B[1, 1, 1, 2] = A[1, 3] / np.sqrt(2)
    B[2, 2, 1, 2] = A[2, 3] / np.sqrt(2)
    B[1, 2, 1, 2] = A[3, 3] / 2
    B[2, 0, 1, 2] = A[4, 3] / 2
    B[0, 1, 1, 2] = A[5, 3] / 2

    B[0, 0, 2, 0] = A[0, 4] / np.sqrt(2)
    B[1, 1, 2, 0] = A[1, 4] / np.sqrt(2)
    B[2, 2, 2, 0] = A[2, 4] / np.sqrt(2)
    B[1, 2, 2, 0] = A[3, 4] / 2
    B[2, 0, 2, 0] = A[4, 4] / 2
    B[0, 1, 2, 0] = A[5, 4] / 2

    B[0, 0, 0, 1] = A[0, 5] / np.sqrt(2)
    B[1, 1, 0, 1] = A[1, 5] / np.sqrt(2)
    B[2, 2, 0, 1] = A[2, 5] / np.sqrt(2)
    B[1, 2, 0, 1] = A[3, 5] / 2
    B[2, 0, 0, 1] = A[4, 5] / 2
    B[0, 1, 0, 1] = A[5, 5] / 2



    # Add minor symmetries ijkl = ijlk and ijkl = jikl

    B[0, 0, 0, 0] = B[0, 0, 0, 0]
    B[0, 0, 0, 0] = B[0, 0, 0, 0]

    B[0, 0, 1, 0] = B[0, 0, 0, 1]
    B[0, 0, 0, 1] = B[0, 0, 0, 1]

    B[0, 0, 1, 1] = B[0, 0, 1, 1]
    B[0, 0, 1, 1] = B[0, 0, 1, 1]

    B[0, 0, 2, 1] = B[0, 0, 1, 2]
    B[0, 0, 1, 2] = B[0, 0, 1, 2]

    B[0, 0, 2, 2] = B[0, 0, 2, 2]
    B[0, 0, 2, 2] = B[0, 0, 2, 2]

    B[0, 0, 0, 2] = B[0, 0, 2, 0]
    B[0, 0, 2, 0] = B[0, 0, 2, 0]



    B[0, 1, 0, 0] = B[0, 1, 0, 0]
    B[1, 0, 0, 0] = B[0, 1, 0, 0]

    B[0, 1, 1, 0] = B[0, 1, 0, 1]
    B[1, 0, 0, 1] = B[0, 1, 0, 1]

    B[0, 1, 1, 1] = B[0, 1, 1, 1]
    B[1, 0, 1, 1] = B[0, 1, 1, 1]

    B[0, 1, 2, 1] = B[0, 1, 1, 2]
    B[1, 0, 1, 2] = B[0, 1, 1, 2]

    B[0, 1, 2, 2] = B[0, 1, 2, 2]
    B[1, 0, 2, 2] = B[0, 1, 2, 2]

    B[0, 1, 0, 2] = B[0, 1, 2, 0]
    B[1, 0, 2, 0] = B[0, 1, 2, 0]



    B[1, 1, 0, 0] = B[1, 1, 0, 0]
    B[1, 1, 0, 0] = B[1, 1, 0, 0]

    B[1, 1, 1, 0] = B[1, 1, 0, 1]
    B[1, 1, 0, 1] = B[1, 1, 0, 1]

    B[1, 1, 1, 1] = B[1, 1, 1, 1]
    B[1, 1, 1, 1] = B[1, 1, 1, 1]

    B[1, 1, 2, 1] = B[1, 1, 1, 2]
    B[1, 1, 1, 2] = B[1, 1, 1, 2]

    B[1, 1, 2, 2] = B[1, 1, 2, 2]
    B[1, 1, 2, 2] = B[1, 1, 2, 2]

    B[1, 1, 0, 2] = B[1, 1, 2, 0]
    B[1, 1, 2, 0] = B[1, 1, 2, 0]



    B[1, 2, 0, 0] = B[1, 2, 0, 0]
    B[2, 1, 0, 0] = B[1, 2, 0, 0]

    B[1, 2, 1, 0] = B[1, 2, 0, 1]
    B[2, 1, 0, 1] = B[1, 2, 0, 1]

    B[1, 2, 1, 1] = B[1, 2, 1, 1]
    B[2, 1, 1, 1] = B[1, 2, 1, 1]

    B[1, 2, 2, 1] = B[1, 2, 1, 2]
    B[2, 1, 1, 2] = B[1, 2, 1, 2]

    B[1, 2, 2, 2] = B[1, 2, 2, 2]
    B[2, 1, 2, 2] = B[1, 2, 2, 2]

    B[1, 2, 0, 2] = B[1, 2, 2, 0]
    B[2, 1, 2, 0] = B[1, 2, 2, 0]



    B[2, 2, 0, 0] = B[2, 2, 0, 0]
    B[2, 2, 0, 0] = B[2, 2, 0, 0]

    B[2, 2, 1, 0] = B[2, 2, 0, 1]
    B[2, 2, 0, 1] = B[2, 2, 0, 1]

    B[2, 2, 1, 1] = B[2, 2, 1, 1]
    B[2, 2, 1, 1] = B[2, 2, 1, 1]

    B[2, 2, 2, 1] = B[2, 2, 1, 2]
    B[2, 2, 1, 2] = B[2, 2, 1, 2]

    B[2, 2, 2, 2] = B[2, 2, 2, 2]
    B[2, 2, 2, 2] = B[2, 2, 2, 2]

    B[2, 2, 0, 2] = B[2, 2, 2, 0]
    B[2, 2, 2, 0] = B[2, 2, 2, 0]



    B[2, 0, 0, 0] = B[2, 0, 0, 0]
    B[0, 2, 0, 0] = B[2, 0, 0, 0]

    B[2, 0, 1, 0] = B[2, 0, 0, 1]
    B[0, 2, 0, 1] = B[2, 0, 0, 1]

    B[2, 0, 1, 1] = B[2, 0, 1, 1]
    B[0, 2, 1, 1] = B[2, 0, 1, 1]

    B[2, 0, 2, 1] = B[2, 0, 1, 2]
    B[0, 2, 1, 2] = B[2, 0, 1, 2]

    B[2, 0, 2, 2] = B[2, 0, 2, 2]
    B[0, 2, 2, 2] = B[2, 0, 2, 2]

    B[2, 0, 0, 2] = B[2, 0, 2, 0]
    B[0, 2, 2, 0] = B[2, 0, 2, 0]


    # Complete minor symmetries
    B[0, 2, 1, 0] = B[0, 2, 0, 1]
    B[0, 2, 0, 2] = B[0, 2, 2, 0]
    B[0, 2, 2, 1] = B[0, 2, 1, 2]

    B[1, 0, 1, 0] = B[1, 0, 0, 1]
    B[1, 0, 0, 2] = B[1, 0, 2, 0]
    B[1, 0, 2, 1] = B[1, 0, 1, 2]

    B[2, 1, 1, 0] = B[2, 1, 0, 1]
    B[2, 1, 0, 2] = B[2, 1, 2, 0]
    B[2, 1, 2, 1] = B[2, 1, 1, 2]


    # Add major symmetries ijkl = klij
    B[0, 1, 1, 1] = B[1, 1, 0, 1]
    B[1, 0, 1, 1] = B[1, 1, 1, 0]

    B[0, 2, 1, 1] = B[1, 1, 0, 2]
    B[2, 0, 1, 1] = B[1, 1, 2, 0]


    return B
def PlotFabricTensor(EigenValues, EigenVectors, NPoints):

    ## New coordinate system
    Q = np.array(EigenVectors)

    ## Build data for fabric plotting
    u = np.arange(0, 2 * np.pi + 2 * np.pi / NPoints, 2 * np.pi / NPoints)
    v = np.arange(0, np.pi + np.pi / NPoints, np.pi / NPoints)
    X = EigenValues[0] * np.outer(np.cos(u), np.sin(v))
    Y = EigenValues[1] * np.outer(np.sin(u), np.sin(v))
    Z = EigenValues[2] * np.outer(np.ones_like(u), np.cos(v))
    nNorm = np.zeros(X.shape)

    for i in range(len(X)):
        for j in range(len(X)):
            [X[i, j], Y[i, j], Z[i, j]] = np.dot([X[i, j], Y[i, j], Z[i, j]], Q)
            n = np.array([X[i, j], Y[i, j], Z[i, j]])
            nNorm[i, j] = np.linalg.norm(n)

    NormedColor = nNorm - nNorm.min()
    NormedColor = NormedColor / NormedColor.max()

    Figure = plt.figure(figsize=(5.5, 4))
    Axe = Figure.add_subplot(111, projection='3d')
    Axe.plot_surface(X, Y, Z, facecolors=plt.cm.jet(NormedColor), rstride=1, cstride=1, alpha=0.2, shade=False)
    Axe.plot_wireframe(X, Y, Z, color='k', rstride=1, cstride=1, linewidth=0.1)
    # scaling hack
    Bbox_min = np.min([X, Y, Z])
    Bbox_max = np.max([X, Y, Z])
    Axe.auto_scale_xyz([Bbox_min, Bbox_max], [Bbox_min, Bbox_max], [Bbox_min, Bbox_max])
    # make the panes transparent
    Axe.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    Axe.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    Axe.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    # make the grid lines transparent
    Axe.xaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    Axe.yaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    Axe.zaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    # modify ticks
    MinX, MaxX = -1, 1
    MinY, MaxY = -1, 1
    MinZ, MaxZ = -1, 1
    Axe.set_xticks([MinX, 0, MaxX])
    Axe.set_yticks([MinY, 0, MaxY])
    Axe.set_zticks([MinZ, 0, MaxZ])
    Axe.xaxis.set_ticklabels([MinX, 0, MaxX])
    Axe.yaxis.set_ticklabels([MinY, 0, MaxY])
    Axe.zaxis.set_ticklabels([MinZ, 0, MaxZ])

    Axe.set_xlabel('X')
    Axe.set_ylabel('Y')
    Axe.set_zlabel('Z')

    Axe.set_title('Fabric tensor')

    ColorMap = plt.cm.ScalarMappable(cmap=plt.cm.jet)
    ColorMap.set_array(nNorm)
    if not NormedColor.max() == 1:
        ColorBar = plt.colorbar(ColorMap, ticks=[int(Color.mean() - 1), int(Color.mean()), int(Color.mean() + 1)])
        plt.cm.ScalarMappable.set_clim(self=ColorMap, vmin=int(Color.mean() - 1), vmax=int(Color.mean() + 1))
    ColorBar = plt.colorbar(ColorMap)
    ColorBar.set_label('Vector norm (-)')

    plt.tight_layout()
    plt.show()
    plt.close(Figure)


    return
def Load_Itk(Filename):

    # Reads the image using SimpleITK
    Itkimage = sitk.ReadImage(Filename)

    # Convert the image to a  numpy array first and then shuffle the dimensions to get axis in the order z,y,x
    CT_Scan = sitk.GetArrayFromImage(Itkimage)

    # Read the origin of the ct_scan, will be used to convert the coordinates from world to voxel and vice versa.
    Origin = np.array(list(reversed(Itkimage.GetOrigin())))

    # Read the spacing along each dimension
    Spacing = np.array(list(reversed(Itkimage.GetSpacing())))

    # Read the dimension of the CT scan (in voxel)
    Size = np.array(list(reversed(Itkimage.GetSize())))

    return CT_Scan, Origin, Spacing, Size
def WriteFabricVTK(EigenValues, EigenVectors, NPoints, Scale, Origin, Directory):

    ## New coordinate system
    Q = np.array(EigenVectors)

    ## Build data for fabric plotting
    u = np.arange(0, 2 * np.pi + 2 * np.pi / NPoints, 2 * np.pi / NPoints)
    v = np.arange(0, np.pi + np.pi / NPoints, np.pi / NPoints)
    X = EigenValues[0] * np.outer(np.cos(u), np.sin(v))
    Y = EigenValues[1] * np.outer(np.sin(u), np.sin(v))
    Z = EigenValues[2] * np.outer(np.ones_like(u), np.cos(v))
    nNorm = np.zeros(X.shape)

    for i in range(len(X)):
        for j in range(len(X)):
            [X[i, j], Y[i, j], Z[i, j]] = np.dot([X[i, j], Y[i, j], Z[i, j]], Q)
            n = np.array([X[i, j], Y[i, j], Z[i, j]])
            nNorm[i, j] = np.linalg.norm(n)

    # Scale the arrays
    X = Scale/2 * X
    Y = Scale/2 * Y
    Z = Scale/2 * Z

    # Translate origin to the center of ROI
    X = Origin[2] + X + Scale/2
    Y = Origin[1] + Y + Scale/2
    Z = Origin[0] + Z + Scale/2

    # Write VTK file
    VTKFile = open(Directory + 'Fabric.vtk', 'w')

    # Write header
    VTKFile.write('# vtk DataFile Version 4.2\n')
    VTKFile.write('VTK from Python\n')
    VTKFile.write('ASCII\n')
    VTKFile.write('DATASET UNSTRUCTURED_GRID\n')

    # Write points coordinates
    Points = int(X.shape[0] * X.shape[1])
    VTKFile.write('\nPOINTS ' + str(Points) + ' floats\n')
    for i in range(Points):
        VTKFile.write(str(X.reshape(Points)[i].round(3)))
        VTKFile.write(' ')
        VTKFile.write(str(Y.reshape(Points)[i].round(3)))
        VTKFile.write(' ')
        VTKFile.write(str(Z.reshape(Points)[i].round(3)))
        VTKFile.write('\n')

    # Write cells connectivity
    Cells = int(NPoints**2)
    ListSize = int(Cells*5)
    VTKFile.write('\nCELLS ' + str(Cells) + ' ' + str(ListSize) + '\n')

    ## Add connectivity of each cell
    Connectivity = np.array([0, 1])
    Connectivity = np.append(Connectivity,[NPoints+2,NPoints+1])

    for i in range(Cells):
        VTKFile.write('4')

        if i > 0 and np.mod(i,NPoints) == 0:
            Connectivity = Connectivity + 1

        for j in Connectivity:
            VTKFile.write(' ' + str(j))
        VTKFile.write('\n')

        ## Update connectivity
        Connectivity = Connectivity+1

    # Write cell types
    VTKFile.write('\nCELL_TYPES ' + str(Cells) + '\n')
    for i in range(Cells):
        VTKFile.write('9\n')

    # Write MIL values
    VTKFile.write('\nPOINT_DATA ' + str(Points) + '\n')
    VTKFile.write('SCALARS MIL float\n')
    VTKFile.write('LOOKUP_TABLE default\n')

    for i in range(NPoints+1):
        for j in range(NPoints+1):
            VTKFile.write(str(nNorm.reshape(Points)[j + i * (NPoints+1)].round(3)))
            VTKFile.write(' ')
        VTKFile.write('\n')
    VTKFile.close()

    return
def Engineering2MandelNotation(A):

    if isinstance(A[0, 0], np.float):
        B = np.zeros((6,6))
    else:
        B = sp.zeros(6)


    for i in range(6):
        for j in range(6):

            if i < 3 and j >= 3:
                B[i,j] = A[i,j] * np.sqrt(2)

            elif i >= 3 and j < 3:
                B[i,j] = A[i,j] * np.sqrt(2)

            elif i >= 3 and j >= 3:
                B[i,j] = A[i,j] * 2

            else:
                B[i, j] = A[i, j]

    return B
def Transform(A,B):

    if A.size == 9 and B.size == 3:

        if isinstance(A[0,0], np.float):
            c = np.zeros(3)
        else:
            c = sp.Matrix([0,0,0])

        for i in range(3):
            for j in range(3):
                c[i] += A[i,j] * B[j]

        if not isinstance(A[0,0], np.float):
            c = np.array(c)

        return c

    elif A.size == 27 and B.size == 9:

        if isinstance(A[0,0,0], np.float):
            c = np.zeros(3)
        else:
            c = sp.Matrix([0,0,0])

        for i in range(3):
            for j in range(3):
                for k in range(3):
                    c[i] += A[i,j,k] * B[j,k]

        if not isinstance(A[0,0,0], np.float):
            c = np.array(c)

        return c

    elif A.size == 81 and B.size == 9:

        if isinstance(A[0,0,0,0], np.float):
            C = np.zeros((3,3))
        else:
            C = sp.zeros(3)

        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        C[i,j] += A[i,j,k,l] * B[k,l]

        if not isinstance(A[0,0,0,0], np.float):
            C = np.array(C)

        return C

    else:
        print('Matrices sizes mismatch')
def FrobeniusProduct(A,B):

    s = 0

    if A.size == 9 and B.size == 9:
        for i in range(3):
            for j in range(3):
                s += A[i, j] * B[i, j]

    elif A.size == 36 and B.size == 36:
        for i in range(6):
            for j in range(6):
                s = s + A[i, j] * B[i, j]

    elif A.shape == (9,9) and B.shape == (9,9):
        for i in range(9):
            for j in range(9):
                s = s + A[i, j] * B[i, j]

    elif A.shape == (3,3,3,3) and B.shape == (3,3,3,3):
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        s = s + A[i, j, k, l] * B[i, j, k, l]

    else:
        print('Matrices sizes mismatch')

    return s
def DyadicProduct(A,B):

    if A.size == 3:

        if isinstance(A[0], np.float):
            C = np.zeros((3,3))
        else:
            C = sp.zeros(3)

        for i in range(3):
            for j in range(3):
                C[i,j] = A[i]*B[j]

        if not isinstance(A[0], np.float):
            C = np.array(C)

    elif A.size == 9:

        if isinstance(A[0,0], np.float):
            C = np.zeros((3,3,3,3))
        else:
            C = sp.zeros(9)

        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        if isinstance(A[0, 0], np.float):
                            C[i,j,k,l] = A[i,j] * B[k,l]
                        else:
                            C[3*i+j,3*k+l] = A[i,j] * B[k,l]

        if not isinstance(A[0,0], np.float):
            C = IsoMorphism99_3333(C)

    else:
        print('Matrices sizes mismatch')

    return C
def PlotStiffnessTensor(S4, NPoints):

    I = np.eye(3)

    ## Build data for plotting tensor
    u = np.arange(0, 2 * np.pi + 2 * np.pi / NPoints, 2 * np.pi / NPoints)
    v = np.arange(0, np.pi + np.pi / NPoints, np.pi / NPoints)
    X = np.outer(np.cos(u), np.sin(v))
    Y = np.outer(np.sin(u), np.sin(v))
    Z = np.outer(np.ones_like(u), np.cos(v))
    Color = np.zeros(X.shape)
    for i in range(len(X)):
        for j in range(len(X)):
            n = np.array([X[i, j], Y[i, j], Z[i, j]])
            N = DyadicProduct(n, n)

            Elongation = FrobeniusProduct(N, Transform(S4, N))
            X[i, j], Y[i, j], Z[i, j] = np.array([X[i, j], Y[i, j], Z[i, j]]) * Elongation

            BulkModulus = FrobeniusProduct(I, Transform(S4, N))
            Color[i, j] = BulkModulus

    MinX, MaxX = int(X.min()), int(X.max())
    MinY, MaxY = int(Y.min()), int(Y.max())
    MinZ, MaxZ = int(Z.min()), int(Z.max())

    if Color.max() - Color.min() > 1:
        NormedColor = Color - Color.min()
        NormedColor = NormedColor / NormedColor.max()
    else:
        NormedColor = np.round(Color / Color.max()) / 2

    ## Plot tensor in image coordinate system
    Figure = plt.figure(figsize=(5.5, 4))
    Axe = Figure.add_subplot(111, projection='3d')
    Axe.plot_surface(X, Y, Z, facecolors=plt.cm.jet(NormedColor), rstride=1, cstride=1, alpha=0.2, shade=False)
    Axe.plot_wireframe(X, Y, Z, color='k', rstride=1, cstride=1, linewidth=0.2)
    # scaling hack
    Bbox_min = np.min([X, Y, Z])
    Bbox_max = np.max([X, Y, Z])
    Axe.auto_scale_xyz([Bbox_min, Bbox_max], [Bbox_min, Bbox_max], [Bbox_min, Bbox_max])
    # make the panes transparent
    Axe.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    Axe.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    Axe.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    # make the grid lines transparent
    Axe.xaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    Axe.yaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    Axe.zaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    # modify ticks
    Axe.set_xticks([MinX, 0, MaxX])
    Axe.set_yticks([MinY, 0, MaxY])
    Axe.set_zticks([MinZ, 0, MaxZ])
    Axe.xaxis.set_ticklabels([MinX, 0, MaxX])
    Axe.yaxis.set_ticklabels([MinY, 0, MaxY])
    Axe.zaxis.set_ticklabels([MinZ, 0, MaxZ])

    Axe.xaxis.set_rotate_label(False)
    Axe.set_xlabel('X (MPa)', rotation=0)
    Axe.yaxis.set_rotate_label(False)
    Axe.set_ylabel('Y (MPa)', rotation=0)
    Axe.zaxis.set_rotate_label(False)
    Axe.set_zlabel('Z (MPa)', rotation=90)

    Axe.set_title('Elasticity tensor')

    ColorMap = plt.cm.ScalarMappable(cmap=plt.cm.jet)
    ColorMap.set_array(Color)
    if not NormedColor.max() == 1:
        ColorBar = plt.colorbar(ColorMap, ticks=[int(Color.mean() - 1), int(Color.mean()), int(Color.mean() + 1)])
        plt.cm.ScalarMappable.set_clim(self=ColorMap, vmin=int(Color.mean() - 1), vmax=int(Color.mean() + 1))
    else:
        ColorBar = plt.colorbar(ColorMap)
    ColorBar.set_label('Bulk modulus (MPa)')
    plt.tight_layout()
    plt.show()
    plt.close(Figure)

    return
def WriteStiffnessVTK(S4, NPoints, Directory):

    I = np.eye(3)

    ## Build data for plotting tensor
    u = np.arange(0, 2 * np.pi + 2 * np.pi / NPoints, 2 * np.pi / NPoints)
    v = np.arange(0, np.pi + np.pi / NPoints, np.pi / NPoints)
    X = np.outer(np.cos(u), np.sin(v))
    Y = np.outer(np.sin(u), np.sin(v))
    Z = np.outer(np.ones_like(u), np.cos(v))
    Color = np.zeros(X.shape)
    for i in range(len(X)):
        for j in range(len(X)):
            n = np.array([X[i, j], Y[i, j], Z[i, j]])
            N = DyadicProduct(n, n)

            Elongation = FrobeniusProduct(N, Transform(S4, N))
            X[i, j], Y[i, j], Z[i, j] = np.array([X[i, j], Y[i, j], Z[i, j]]) * Elongation

            BulkModulus = FrobeniusProduct(I, Transform(S4, N))
            Color[i, j] = BulkModulus

    MinX, MaxX = int(X.min()), int(X.max())
    MinY, MaxY = int(Y.min()), int(Y.max())
    MinZ, MaxZ = int(Z.min()), int(Z.max())

    # Write VTK file
    VTKFile = open(Directory + 'Stiffness.vtk', 'w')

    # Write header
    VTKFile.write('# vtk DataFile Version 4.2\n')
    VTKFile.write('VTK from Python\n')
    VTKFile.write('ASCII\n')
    VTKFile.write('DATASET UNSTRUCTURED_GRID\n')

    # Write points coordinates
    Points = int(X.shape[0] * X.shape[1])
    VTKFile.write('\nPOINTS ' + str(Points) + ' floats\n')
    for i in range(Points):
        VTKFile.write(str(X.reshape(Points)[i].round(3)))
        VTKFile.write(' ')
        VTKFile.write(str(Y.reshape(Points)[i].round(3)))
        VTKFile.write(' ')
        VTKFile.write(str(Z.reshape(Points)[i].round(3)))
        VTKFile.write('\n')

    # Write cells connectivity
    Cells = int(NPoints**2)
    ListSize = int(Cells*5)
    VTKFile.write('\nCELLS ' + str(Cells) + ' ' + str(ListSize) + '\n')

    ## Add connectivity of each cell
    Connectivity = np.array([0, 1])
    Connectivity = np.append(Connectivity,[NPoints+2,NPoints+1])

    for i in range(Cells):
        VTKFile.write('4')

        if i > 0 and np.mod(i,NPoints) == 0:
            Connectivity = Connectivity + 1

        for j in Connectivity:
            VTKFile.write(' ' + str(j))
        VTKFile.write('\n')

        ## Update connectivity
        Connectivity = Connectivity+1

    # Write cell types
    VTKFile.write('\nCELL_TYPES ' + str(Cells) + '\n')
    for i in range(Cells):
        VTKFile.write('9\n')

    # Write MIL values
    VTKFile.write('\nPOINT_DATA ' + str(Points) + '\n')
    VTKFile.write('SCALARS Bulk_modulus float\n')
    VTKFile.write('LOOKUP_TABLE default\n')

    for i in range(NPoints+1):
        for j in range(NPoints+1):
            VTKFile.write(str(Color.reshape(Points)[j + i * (NPoints+1)].round(3)))
            VTKFile.write(' ')
        VTKFile.write('\n')
    VTKFile.close()

    return
def TransformTensor(A,OriginalBasis,NewBasis):

    # Build change of coordinate matrix
    O = OriginalBasis
    N = NewBasis

    Q = np.zeros((3,3))
    for i in range(3):
        for j in range(3):
            Q[i,j] = np.dot(O[i,:],N[j,:])

    if A.size == 36:
        A4 = IsoMorphism66_3333(A)

    elif A.size == 81 and A.shape == (3,3,3,3):
        A4 = A

    TransformedA = np.zeros((3, 3, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    for m in range(3):
                        for n in range(3):
                            for o in range(3):
                                for p in range(3):
                                    TransformedA[i, j, k, l] += Q[m,i]*Q[n,j]*Q[o,k]*Q[p,l] * A4[m, n, o, p]
    if A.size == 36:
        TransformedA = IsoMorphism3333_66(TransformedA)

    return TransformedA
def Mandel2EngineeringNotation(A):

    if isinstance(A[0, 0], np.float):
        B = np.zeros((6,6))
    else:
        B = sp.zeros(6)


    for i in range(6):
        for j in range(6):

            if i < 3 and j >= 3:
                B[i,j] = A[i,j] / np.sqrt(2)

            elif i >= 3 and j < 3:
                B[i,j] = A[i,j] / np.sqrt(2)

            elif i >= 3 and j >= 3:
                B[i,j] = A[i,j] / 2

            else:
                B[i, j] = A[i, j]

    return B

## Set variables
WorkingDirectory = os.getcwd()
ScanFolder = os.path.join(WorkingDirectory,'02_Data')
DataSubFolders = [File for File in os.listdir(ScanFolder) if os.path.isdir(os.path.join(ScanFolder,File))]
DataSubFolders.sort()

Group = 'Healthy'   # Healthy or OI

DataFolder = os.path.join(WorkingDirectory,'04_Results/01_ROI_Analysis/02_'+Group+'_FabricElasticity')
ResultsFolder = os.path.join(WorkingDirectory,'04_Results/01_ROI_Analysis/03_'+Group+'_TransformedTensors/')
ROIPath = os.path.join(WorkingDirectory,'04_Results/01_ROI_Analysis/01_'+Group+'_ROIs/00_Cleaned_ROIs/')


# 01 Load Data
FabricFiles = [File for File in os.listdir(DataFolder) if File.endswith('.fab')]
FabricFiles.sort()

ConstantsFiles = [File for File in os.listdir(DataFolder) if File.endswith('.dat')]
ConstantsFiles.sort()



# 02 Transform tensor into fabric coordinate system and compute engineering constants
TransformedConstants = pd.DataFrame()
Sample = ConstantsFiles[0]
for Sample in ConstantsFiles:

    ROINumber = Sample[0]
    Scan = Sample[2:-4]

    FabricData = GetFabricInfos(os.path.join(DataFolder,Sample[:-4] + '.fab'))
    EigenValues, EigenVectors = SortFabric(FabricData)
    # PlotFabricTensor(EigenValues, EigenVectors, 32)
    ROI_Scan, ROI_Origin, ROI_Spacing, ROI_Size = Load_Itk(ROIPath + Sample[:-4] + '_Cleaned.mhd')
    WriteFabricVTK(EigenValues, EigenVectors, 32, ROI_Size[0]*ROI_Spacing[0], ROI_Origin, ResultsFolder)
    ComplianceMatrix = GetComplianceMatrix(os.path.join(DataFolder,Sample))

    ## Symmetrize the matrix
    ComplianceMatrix = (ComplianceMatrix+ComplianceMatrix.T)/2

    ## Compute stiffness matrix
    StiffnessMatrix = np.linalg.inv(ComplianceMatrix)

    ## Symmetrize the matrix (rounding errors due to inversion)
    StiffnessMatrix = (StiffnessMatrix+StiffnessMatrix.T)/2



    # 02 Stiffness tensor transformation into fabric coordinate system
    MandelStiffness = Engineering2MandelNotation(StiffnessMatrix)
    I = np.eye(3)
    Q = np.array(EigenVectors)
    TS4 = TransformTensor(IsoMorphism66_3333(MandelStiffness), I, Q)
    WriteStiffnessVTK(TS4, 32, ResultsFolder)
    TransformedStiffness = IsoMorphism3333_66(TS4)



    # 03 Project onto orthotropy
    OrthotropicTransformedStiffness = np.zeros(TransformedStiffness.shape)

    for i in range(OrthotropicTransformedStiffness.shape[0]):
        for j in range(OrthotropicTransformedStiffness.shape[1]):
            if i < 3 and j < 3:
                OrthotropicTransformedStiffness[i, j] = TransformedStiffness[i, j]
            elif i == j:
                OrthotropicTransformedStiffness[i, j] = TransformedStiffness[i, j]



    # 04 Get engineering constants in fabric coordinate system
    TransformedCompliance = np.linalg.inv(Mandel2EngineeringNotation(OrthotropicTransformedStiffness))
    TransformedConstants = TransformedConstants.append({
        'Scan':Scan,
        'ROI Number': ROINumber,
        'BVTV': FabricData['BVTV'][0],
        'm1': EigenValues[0],
        'm2': EigenValues[1],
        'm3': EigenValues[2],
        'DA': FabricData['DA'][0],
        'E1': 1 / TransformedCompliance[0, 0],
        'E2': 1 / TransformedCompliance[1, 1],
        'E3': 1 / TransformedCompliance[2, 2],
        'Mu23': 1 / TransformedCompliance[3, 3],
        'Mu31': 1 / TransformedCompliance[4, 4],
        'Mu12': 1 / TransformedCompliance[5, 5],
        'Nu12': -TransformedCompliance[0, 1] / TransformedCompliance[0, 0],
        'Nu13': -TransformedCompliance[0, 2] / TransformedCompliance[0, 0],
        'Nu23': -TransformedCompliance[1, 2] / TransformedCompliance[1, 1]}, ignore_index=True)



# 03 Save results for each individual scan
Scans = TransformedConstants['Scan'].unique()

for Scan in Scans:

    Filter = TransformedConstants['Scan'] == Scan
    ScanConstants = TransformedConstants[Filter]
    ScanConstants.to_csv(os.path.join(ResultsFolder,Scan+'.csv'),index=False)


