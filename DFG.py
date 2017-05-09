DEBUG_LEVEL=1

Keys = [(0,0),(1,0),(0,1),(1,1)]

dicProd = { (0,0):
    {(0,0): (0,0), (1,0): (0,0), (0,1): (0,0), (1,1): (0,0)},
        (1,0):
            {(0,0): (0,0), (1,0): (1,0), (0,1): (0,1), (1,1): (1,1)},
            (0,1):
                {(0,0): (0,0), (1,0): (0,1), (0,1): (0,1), (1,1): (0,1)},
            (1,1):
                {(0,0): (0,0), (1,0): (1,1), (0,1): (0,1), (1,1): (1,1)}
}

dicSum = { (0,0):
    {(0,0): (0,0), (1,0): (1,0), (0,1): (0,1), (1,1): (1,1)},
        (1,0):
            {(0,0): (1,0), (1,0): (1,0), (0,1): (1,1), (1,1): (1,1)},
            (0,1):
                {(0,0): (0,1), (1,0): (1,1), (0,1): (0,1), (1,1): (1,1)},
            (1,1):
                {(0,0): (1,1), (1,0): (1,1), (0,1): (1,1), (1,1): (1,1)}
}

def Prod(a,b):
    return dicProd[a][b]

def Sum(a,b):
    return dicSum[a][b]

Zero = (0,0)

Unit = (1,0)



def MatProd(M1,M2,prod=Prod,sum=Sum,zero=Zero):
    res=[]
    for i in range(len(M1)):
        res.append([])
        for j in range(len(M2)):
            new = zero
            for k in range(len(M1)):
                new = sum(new,prod(M1[i][k],M2[k][j]))
            res[i].append(new)
    return res

def MatSum(M1,M2,sum=Sum):
    res=[]
    for i in range(len(M1)):
        res.append([])
        for j in range(len(M1)):
            res[i].append(sum(M1[i][j],M2[i][j]))
    return res

def initMatrix(len,zero=Zero):
    res = []
    for i in range(len):
        res.append([])
        for j in range(len):
            res[i].append(zero)
    return res

def extendMatrix(Mat,range_ext,zero=Zero,unit=Unit):
    res = []
    for i in range(range_ext):
        res.append([])
        for j in range(range_ext):
            if i<len(Mat) and j<len(Mat):
                res[i].append(Mat[i][j])
            else:
                if i==j:
                    res[i].append(unit)
                else:
                    res[i].append(zero)
    return res


def printMatrix(Mat):
    for i in range(len(Mat)):
        line = ""
        for j in range(len(Mat)):
            line = line+"   "+str(Mat[i][j])
        print(line)
    return 0

def printRel(Rel):
    if DEBUG_LEVEL>=2:
        print("DEBUG_LEVEL Information, printRel.")
        print(Rel[0])
        print(Rel[1])
    for i in range(len(Rel[1])):
        line = str(Rel[0][i])+"   |   "
        for j in range(len(Rel[1])):
            line = line+"   "+str(Rel[1][i][j])
        print(line)
    return 0

def is_empty(Rel):
    if Rel[0]==[]:
        return True
    if Rel[1]==[]:
        return True
    return False

def homogeneisation(R1,R2,zero=Zero,unit=Unit): # Relations are tuples (v,M) of a list of variables and a matrix
    var_indices = []
    var2 = []
    if is_empty(R1):
        empty=Relation(R2[0])
        empty.identity()
        return((empty.variables,empty.matrix),R2)
    if is_empty(R2):
        empty=Relation(R1[0])
        empty.identity()
        return(R1,(empty.variables,empty.matrix))
    if DEBUG_LEVEL>=2:
        print("DEBUG_LEVEL info for Homogeneisation. Inputs.")
        printRel(R1)
        printRel(R2)
    for v in R2[0]:
        var2.append(v)
    for v in R1[0]:
        found = False
        for j in range(len(R2[0])):
            if R2[0][j]==v:
                var_indices.append(j)
                found = True
                var2.remove(v)
        if not found:
            var_indices.append(-1)
    for v in var2:
        var_indices.append(R2[0].index(v))
    var_extended=R1[0]+var2
    M1_extended=extendMatrix(R1[1],len(var_extended))
    M2_extended = []
    for i in range(len(var_extended)):
        M2_extended.append([])
        i_in = var_indices[i]!=-1
        for j in range(len(var_extended)):
            if not i_in and i==j:
                M2_extended[i].append(unit)
            elif i_in and var_indices[j]!=-1:
                M2_extended[i].append(R2[1][var_indices[i]][var_indices[j]])
            else:
                M2_extended[i].append(zero)
    if DEBUG_LEVEL>=2:
        print("DEBUG_LEVEL info for Homogeneisation. Result.")
        printRel(R1)
        printRel(R2)
        printRel((var_extended,M1_extended))
        printRel((var_extended,M2_extended))
    return ((var_extended,M1_extended),(var_extended,M2_extended))


def compositionRelations(R1,R2):
    (eR1,eR2)=homogeneisation(R1,R2)
    Result=(eR1[0],MatProd(eR1[1],eR2[1]))
    if DEBUG_LEVEL>=2:
        print("DEBUG_LEVEL info for compositionRelations. Inputs.")
        printRel(R1)
        printRel(R2)
        print("DEBUG_LEVEL info for compositionRelations. Outputs.")
        printRel(Result)
    return Result

def sumRelations(R1,R2):
    (eR1,eR2)=homogeneisation(R1,R2)
    return (eR1[0],MatSum(eR1[1],eR2[1]))

def Out_Rel(R,zero=Zero,unit=Unit):
    out_tab=[]
    for i in range(len(R[1])):
        empty=True
        ended=False
        j=0
        while (not ended) and j<len(R[1]):
            if R[1][j][i]!=zero:
                empty=False
            if R[1][j][i]!=unit and R[1][j][i]!=zero:
                out_tab.append(R[0][i])
                ended=True
            if DEBUG_LEVEL>=2:
                print("Out_rel")
                printRel(R)
                print(i,j,"coef.",R[1][j][i],"ended",ended,"empty",empty)
            j=j+1
        if empty and not ended:
            out_tab.append(R[0][i])
    if DEBUG_LEVEL>=2:
        print(out_tab)
        print("==========")
    return out_tab

def In_Rel(R,zero=Zero,unit=Unit):
    in_tab=[]
    for i in range(len(R[1])):
        empty=True
        j=0
        while empty and j<len(R[1]):
            if R[1][i][j]!=zero and R[1][i][j]!=unit:
                empty=False
                in_tab.append(R[0][i])
            j=j+1
    return in_tab

def In_Out_Rel(R,zero=Zero,unit=Unit):
    return (In_Rel(R,zero),Out_Rel(R,zero,unit))


def isequalRel(R1,R2):
    if set(R1[0])!=set(R2[0]):
        return False
    (eR1,eR2)=homogeneisation(R1,R2)
    for i in range(len(eR1[1])):
        for j in range(len(eR1[1])):
            if eR1[1][i][j]!=eR2[1][i][j]:
                return False
    return True

def identityRel(var,unit=Unit,zero=Zero):
    Id=[]
    for i in range(len(var)):
        Id.append([])
        for j in range(len(var)):
            if i==j:
                Id[i].append(unit)
            else:
                Id[i].append(zero)
    return (var,Id)

def algebraicRel(Rel,list,zero=Zero,strongDep=(0,1)):
    (Var,Mat)=Rel
    out = Var.index(list[0][0])
    Mat[out][out]=zero
    for var in list[1]:
        in_ind=Var.index(var)
        Mat[in_ind][out]=strongDep
    return (Var,Mat)

def conditionRel(condvar,outvar,zero=Zero,strongDep=(0,1)):
    Var=list(set(condvar)|set(outvar))
    Mat=[]
    for i in range(len(Var)):
        Mat.append([])
        for j in range(len(Var)):
            Mat[i].append(zero)
    for i in range(len(Var)):
        for j in range(len(Var)):
            if Var[i] in condvar and Var[j] in outvar:
                Mat[i][j]=strongDep
    return (Var,Mat)

class Relation():
    def __init__(self,variables):
        self.variables = variables
        self.matrix = initMatrix(len(variables))
    
    def algebraic(self,list): # list contains two list with left-hand and right-hand side variables respectively; they are supposed to be
        # contained in self.variables already.
        (Var,Mat)=algebraicRel((self.variables,self.matrix),list)
        self.matrix = Mat
        return self
    
    def identity(self):
        (Var,Mat)=identityRel(self.variables)
        self.matrix=Mat
        return self
    
    def conditionRel(self,list_var):
        (Var,Mat)=conditionRel(list_var,self.out())
        (V,M)=sumRelations((self.variables,self.matrix),(Var,Mat))
        cond = Relation(V)
        cond.matrix = M
        return cond
    
    def composition(self,Rel):
        (var,Mat)=compositionRelations((self.variables,self.matrix),(Rel.variables,Rel.matrix))
        compo = Relation(var)
        compo.matrix = Mat
        return compo
    
    def sumRel(self,Rel):
        (var,Mat)=sumRelations((self.variables,self.matrix),(Rel.variables,Rel.matrix))
        result = Relation(var)
        result.matrix = Mat
        return result
    
    def show(self):
        printRel((self.variables,self.matrix))
    
    def out(self):
        return Out_Rel((self.variables,self.matrix))
    
    def In(self):
        return In_Rel((self.variables,self.matrix))
    
    def in_out(self):
        return In_Out_Rel((self.variables,self.matrix))
    
    def equal(self,Rel):
        return isequalRel((self.variables,self.matrix),(Rel.variables,Rel.matrix))
    
    def fixpoint(self):
        end = False
        (v,M) = identityRel(self.variables)
        Fix = Relation(v)
        PreviousFix = Relation(v)
        Current = Relation(v)
        Fix.matrix=M
        PreviousFix.matrix=M
        Current.matrix=M
        while not end:
            PreviousFix.matrix=Fix.matrix
            Current = Current.composition(self)
            Fix = Fix.sumRel(Current)
            if Fix.equal(PreviousFix):
                end=True
            if DEBUG_LEVEL>=2:
                print("DEBUG. Fixpoint.")
                print("DEBUG. Fixpoint.")
                self.show()
                Fix.show()
        return Fix
