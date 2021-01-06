DEBUG_LEVEL = 1

Keys = [(0, 0), (1, 0), (0, 1), (1, 1)]

dicProd = {(0, 0):
               {(0, 0): (0, 0), (1, 0): (0, 0), (0, 1): (0, 0), (1, 1): (0, 0)},
           (1, 0):
               {(0, 0): (0, 0), (1, 0): (1, 0), (0, 1): (0, 1), (1, 1): (1, 1)},
           (0, 1):
               {(0, 0): (0, 0), (1, 0): (0, 1), (0, 1): (0, 1), (1, 1): (0, 1)},
           (1, 1):
               {(0, 0): (0, 0), (1, 0): (1, 1), (0, 1): (0, 1), (1, 1): (1, 1)}
           }

dicSum = {(0, 0):
              {(0, 0): (0, 0), (1, 0): (1, 0), (0, 1): (0, 1), (1, 1): (1, 1)},
          (1, 0):
              {(0, 0): (1, 0), (1, 0): (1, 0), (0, 1): (1, 1), (1, 1): (1, 1)},
          (0, 1):
              {(0, 0): (0, 1), (1, 0): (1, 1), (0, 1): (0, 1), (1, 1): (1, 1)},
          (1, 1):
              {(0, 0): (1, 1), (1, 0): (1, 1), (0, 1): (1, 1), (1, 1): (1, 1)}
          }


def Prod(a, b):
    return dicProd[a][b]


def Sum(a, b):
    return dicSum[a][b]


Zero = (0, 0)

Unit = (1, 0)


def MatProd(M1, M2, prod=Prod, sum=Sum, zero=Zero):
    res = []
    for i in range(len(M1)):
        res.append([])
        for j in range(len(M2)):
            new = zero
            for k in range(len(M1)):
                new = sum(new, prod(M1[i][k], M2[k][j]))
            res[i].append(new)
    return res


def MatSum(M1, M2, sum=Sum):
    res = []
    for i in range(len(M1)):
        res.append([])
        for j in range(len(M1)):
            res[i].append(sum(M1[i][j], M2[i][j]))
    return res


def initMatrix(len, zero=Zero):
    res = []
    for i in range(len):
        res.append([])
        for j in range(len):
            res[i].append(zero)
    return res


def extendMatrix(Mat, range_ext, zero=Zero, unit=Unit):
    res = []
    for i in range(range_ext):
        res.append([])
        for j in range(range_ext):
            if i < len(Mat) and j < len(Mat):
                res[i].append(Mat[i][j])
            else:
                if i == j:
                    res[i].append(unit)
                else:
                    res[i].append(zero)
    return res


def printMatrix(Mat):
    for i in range(len(Mat)):
        line = ""
        for j in range(len(Mat)):
            line = line + "   " + str(Mat[i][j])
        print(line)
    return 0


def printRel(Rel):
    if DEBUG_LEVEL >= 2:
        print("DEBUG_LEVEL Information, printRel.")
        print(Rel[0])
        print(Rel[1])
    for i in range(len(Rel[1])):
        line = str(Rel[0][i]) + "   |   "
        for j in range(len(Rel[1])):
            line = line + "   " + str(Rel[1][i][j])
        print(line)
    return 0


def is_empty(relation):
    if not relation[0]:
        return True
    if not relation[1]:
        return True
    return False


def homogeneisation(relation_1, relation_2, zero=Zero, unit=Unit):
    """
    :param relation_1: Tuple (v,M) of a list of variables and a matrix
    :param relation_2: Tuple (v,M) of a list of variables and a matrix
    :param zero:
    :param unit:
    :return:
    """
    var_indices = []
    var2 = []
    if is_empty(relation_1):
        empty = Relation(relation_2[0])
        empty.identity()
        return (empty.variables, empty.matrix), relation_2
    if is_empty(relation_2):
        empty = Relation(relation_1[0])
        empty.identity()
        return relation_1, (empty.variables, empty.matrix)
    if DEBUG_LEVEL >= 2:
        print("DEBUG_LEVEL info for Homogeneisation. Inputs.")
        printRel(relation_1)
        printRel(relation_2)
    for v in relation_2[0]:
        var2.append(v)
    for v in relation_1[0]:
        found = False
        for j in range(len(relation_2[0])):
            if relation_2[0][j] == v:
                var_indices.append(j)
                found = True
                var2.remove(v)
        if not found:
            var_indices.append(-1)
    for v in var2:
        var_indices.append(relation_2[0].index(v))
    var_extended = relation_1[0] + var2
    m1_extended = extendMatrix(relation_1[1], len(var_extended))
    m2_extended = []
    for i in range(len(var_extended)):
        m2_extended.append([])
        i_in = var_indices[i] != -1
        for j in range(len(var_extended)):
            if not i_in and i == j:
                m2_extended[i].append(unit)
            elif i_in and var_indices[j] != -1:
                m2_extended[i].append(relation_2[1][var_indices[i]][var_indices[j]])
            else:
                m2_extended[i].append(zero)
    if DEBUG_LEVEL >= 2:
        print("DEBUG_LEVEL info for Homogeneisation. Result.")
        printRel(relation_1)
        printRel(relation_2)
        printRel((var_extended, m1_extended))
        printRel((var_extended, m2_extended))
    return (var_extended, m1_extended), (var_extended, m2_extended)


def compositionRelations(R1, R2):
    (eR1, eR2) = homogeneisation(R1, R2)
    result = (eR1[0], MatProd(eR1[1], eR2[1]))
    if DEBUG_LEVEL >= 2:
        print("DEBUG_LEVEL info for compositionRelations. Inputs.")
        printRel(R1)
        printRel(R2)
        print("DEBUG_LEVEL info for compositionRelations. Outputs.")
        printRel(result)
    return result


def sumRelations(R1, R2):
    (eR1, eR2) = homogeneisation(R1, R2)
    return eR1[0], MatSum(eR1[1], eR2[1])


def Out_Rel(R, zero=Zero, unit=Unit):
    out_tab = []
    for i in range(len(R[1])):
        empty = True
        ended = False
        j = 0
        while (not ended) and j < len(R[1]):
            if R[1][j][i] != zero:
                empty = False
            if R[1][j][i] != unit and R[1][j][i] != zero:
                out_tab.append(R[0][i])
                ended = True
            if DEBUG_LEVEL >= 2:
                print("Out_rel")
                printRel(R)
                print(i, j, "coef.", R[1][j][i], "ended", ended, "empty", empty)
            j = j + 1
        if empty and not ended:
            out_tab.append(R[0][i])
    if DEBUG_LEVEL >= 2:
        print(out_tab)
        print("==========")
    return out_tab


def In_Rel(R, zero=Zero, unit=Unit):
    in_tab = []
    for i in range(len(R[1])):
        empty = True
        j = 0
        while empty and j < len(R[1]):
            if R[1][i][j] != zero and R[1][i][j] != unit:
                empty = False
                in_tab.append(R[0][i])
            j = j + 1
    return in_tab


def In_Out_Rel(R, zero=Zero, unit=Unit):
    return In_Rel(R, zero), Out_Rel(R, zero, unit)


def isequalRel(R1, R2):
    if set(R1[0]) != set(R2[0]):
        return False
    (eR1, eR2) = homogeneisation(R1, R2)
    for i in range(len(eR1[1])):
        for j in range(len(eR1[1])):
            if eR1[1][i][j] != eR2[1][i][j]:
                return False
    return True


def identityRel(var, unit=Unit, zero=Zero):
    Id = []
    for i in range(len(var)):
        Id.append([])
        for j in range(len(var)):
            if i == j:
                Id[i].append(unit)
            else:
                Id[i].append(zero)
    return var, Id


def algebraicRel(relation, list, zero=Zero, strongDep=(0, 1)):
    (Var, Mat) = relation
    out = Var.index(list[0][0])
    Mat[out][out] = zero
    for var in list[1]:
        in_ind = Var.index(var)
        Mat[in_ind][out] = strongDep
    return Var, Mat


def conditionRel(condvar, outvar, zero=Zero, strongDep=(0, 1)):
    var = list(set(condvar) | set(outvar))
    matrix = []
    for i in range(len(var)):
        matrix.append([])
        for j in range(len(var)):
            matrix[i].append(zero)
    for i in range(len(var)):
        for j in range(len(var)):
            if var[i] in condvar and var[j] in outvar:
                matrix[i][j] = strongDep
    return var, matrix


class Relation():
    def __init__(self, variables):
        self.variables = variables
        self.matrix = initMatrix(len(variables))

    def algebraic(self, list):
        """
        :param list: list contains two list with left-hand and right-hand side variables respectively;
            they are supposed to be contained in self.variables already.
        """

        (Var, Mat) = algebraicRel((self.variables, self.matrix), list)
        self.matrix = Mat
        return self

    def identity(self):
        (Var, Mat) = identityRel(self.variables)
        self.matrix = Mat
        return self

    def conditionRel(self, list_var):
        (Var, Mat) = conditionRel(list_var, self.out())
        (V, M) = sumRelations((self.variables, self.matrix), (Var, Mat))
        cond = Relation(V)
        cond.matrix = M
        return cond

    def composition(self, rel):
        (var, Mat) = compositionRelations((self.variables, self.matrix), (rel.variables, rel.matrix))
        compo = Relation(var)
        compo.matrix = Mat
        return compo

    def sumRel(self, rel):
        (var, Mat) = sumRelations((self.variables, self.matrix), (rel.variables, rel.matrix))
        result = Relation(var)
        result.matrix = Mat
        return result

    def show(self):
        printRel((self.variables, self.matrix))

    def out(self):
        return Out_Rel((self.variables, self.matrix))

    def In(self):
        return In_Rel((self.variables, self.matrix))

    def in_out(self):
        return In_Out_Rel((self.variables, self.matrix))

    def equal(self, rel):
        return isequalRel((self.variables, self.matrix), (rel.variables, rel.matrix))

    def fixpoint(self):
        end = False
        (v, M) = identityRel(self.variables)
        fix = Relation(v)
        previous_fix = Relation(v)
        current = Relation(v)
        fix.matrix = M
        previous_fix.matrix = M
        current.matrix = M
        while not end:
            previous_fix.matrix = fix.matrix
            current = current.composition(self)
            fix = fix.sumRel(current)
            if fix.equal(previous_fix):
                end = True
            if DEBUG_LEVEL >= 2:
                print("DEBUG. Fixpoint.")
                print("DEBUG. Fixpoint.")
                self.show()
                fix.show()
        return fix
