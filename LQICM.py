# -*- coding: UTF-8 -*-
#
# -----------------------------------------------------------------
# LQICM_On_C_Toy_Parser: LQICM.py
#
# This file implement the transforming pass which computes an
# invariant degree for each statement of loops and peel this loop.
#
#-----------------------------------------------------------------
from __future__ import print_function
import sys

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])

from pycparser import parse_file, c_parser, c_ast, c_generator

DEBUG = True

text = r"""
int main(){
    int i=0,y=0;
    int x=100;
    int x2=0;
    int z;
    int k=10;
    while(i<100){
        z=y*y;
        use(z);
        y=x+x;
        use(y);
        i=i+1;
        while(j<100){
            t = x * x;
            x = k;
            use(j);
            j=j+1;
        }
    }
    return 42;
}
"""

# Create the parser and ask to parse the text. parse() will throw
# a ParseError if there's an error in the code
#
parser = c_parser.CParser()
filename=sys.argv[1]
# ast = parser.parse(text, filename='<None>')
ast = parse_file(filename, use_cpp=True)
# ast.ext[0].show()
# print(ast.ext[0])

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
			for k in range(len(M1))
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

def extendMatrix(Mat,range,zero=Zero,unit=Unit):
	res = []
	for i in range(range):
		res.append([])
		for j in range(range):
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
	print("")
	for i in range(len(Rel[1])):
		line = str(Rel[0][i])+"   |   "
		for j in range(len(Mat)):
			line = line+"   "+str(Mat[i][j])
		print(line)
	return 0	

def homogeneisation(R1,R2,zero=Zero,unit=Unit): # Relations are tuples (v,M) of a list of variables and a matrix
	var_indices = []
	var2 = []
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
	M1_extended=extendMatrix(R1[1],len(var2))
	var_extended=R1[0]+var2
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
	if DEBUG:
		printRel((R1))
		printRel((R2))
		printRel((var_extended,M1_extended))
		printRel((var_extended,M2_extended))
	return ((var_extended,M1_extended),(var_extended,M2_extended))
			

def compositionRelations(R1,R2):
	(eR1,eR2)=homogeneisation(R1,R2)
        return (eR1[0],MatProd(eR1[1],eR2[1]))

def sumRelations(R1,R2): 
	(eR1,eR2)=homogeneisation(R1,R2)
        return (eR1[0],MatSum(eR1[1],eR2[1]))

def Out_Rel(R,zero=Zero,unit=Unit):
	out_tab=[]
	for i in range(len(R[1])):
		empty=True
		j=0
		while empty and j<len(R[1]):
			if R[1][j][i]!=zero:
				empty=False
			if R[1][j][i]!=unit:
				out_tab(R[0][i])
			j=j+1
		if empty:
			out_tab(R[0][i])
	return out_tab

def In_Rel(R,zero=Zero):
	in_tab=[]
	for i in range(len(R[1])):
		empty=True
		j=0
		while empty and j<len(R[1]):
			if R[1][i][j]!=zero:
				empty=False
				in_tab.append(R[0][i])
			j=j+1
	return in_tab

def In_Out_Rel(R,zero=Zero,unit=Unit):
	return (In(R,zero),Out(R,zero,unit))


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
	for i in len(var):
		Id.append([])
		for j in len(var):
			if i==j:
				Id[i][j]=unit
			else:
				Id[i][j]=zero
	return (var,Id)

class Relation():
    def __init__(self,variables):
        self.variables = variables
        self.matrix = InitMatrix(len(variables))

    def ajoutPropag(self,v,w): # v,w indices of variables
        self.matrix[v][w]=Sum(self.matrix[v][w],(1,0))

    def ajoutVar(self,x):
        if x not in self.variables:
		self.variables.append(x)
		extendMatrix(self.matrix,1)

    def ajoutDep(self,v,w): # v,w indices of variables
        self.matrix[v][w]=Sum(self.matrix[v][w],(0,1))

    def ajoutInit(self,v): # v indice of variable
	for w in range(len(variables)):
		self.matrix[v][w]=Prod(self.matrix[v][w],(0,0))

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

    def in(self):
	return In_Rel((self.variables,self.matrix))

    def in_out(self):
	return In_Out_Rel((self.variables,self.matrix))

    def equal(self,Rel):
	return isequalRel((self.variables,self.matrix),(Rel.variables,Rel.matrix))

    def fixpoint(self):
	end = True
	(v,M) = identityRel(self.variables)
	Fix = Relation(v)
	Current = Relation(v)
	Fix.matrix=M
	Current.matrix=M
	while not True:
		Current = Current.composition(self)
		Fix = Fix.sumRel(Current)
	return Fix

class MyWhile():
    def __init__(self, node_while, parent, isOpt, subWhiles):
        self.node_while = node_while
        self.parent = parent
        self.isOpt = isOpt
        self.subWhiles = subWhiles

    def show(self, indent=''):
        indice = self.parent[1]
        opt = self.isOpt
        # print(indent+"while - "+str(indice)+" est opt:"+str(opt))
        for l in self.subWhiles:
            l.show('\t')



class varVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.values = []

    def visit_ID(self, node):
        self.values.append(node.name)

class ChangeNameVisitor(c_ast.NodeVisitor):
    def __init__(self,var,deg):
        self.var = var
        self.deg = deg

    def visit_ID(self, node):
        if(node.name in self.var):
            if(self.deg!=-1):
                node.name=node.name+'_'+str(self.deg)

class WhileVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.values = []

    def visit(self, node, parent=None, i=-1):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, parent, i)

    def visit_While(self, node, parent,i):
        wv = WhileVisitor()
        wv.visit(node.stmt)
        myWhile = MyWhile(node,(parent,i),False,wv.values)
        # mywhile = c_ast.While(node.cond,node.stmt)
        self.values.append(myWhile)

    def generic_visit(self, node, parent,i):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        i = 0
        for c_name, c in node.children():
            self.visit(c,node,i)
            i +=1

def get_first_while(current_node):
    """Return the next while node after current_node
        OK
    """
    wv = WhileVisitor()
    wv.visit(current_node)
    return wv.values[0]

def exist_rel(vars1,vars2):
    for v in vars1:
        if v in vars2:
            return True
    return False

def iscond(node):
    if(isinstance(node,c_ast.While)):
	return True
    if(isinstance(node,c_ast.If)):
	return True
    return False

def new_list_dep(while_stmt,command,i):
    """Return a list of dep
        for the given command
    """
    depList = []
#   ind=0
    relsC=compute_rel(command)
    (InC,OutC) = relsC.in_out()
    # print("inC="+str(InC))
    # FIXME TO optimize	
    tabcomm=[]
    tabInOut=[]
    for n in while_stmt.block_items:
        relsN=compute_rel(n)
        InOut = relsN.in_out()
        tabcomm.append(n)
	tabInOut.append(InOut)
    tabInOutOrdered=[]
    for j in range(len(tabInOut)):
	if j<i:
		k=i-1-j
	else:
		k=len(tabInOut)+i-1-j
	tabInOutOrdered.append(tabInOut[k])
    for var in InC:
	found=False
	k=0
	while k<len(tabInOutOrdered) and not found:
		if var in tabInOutOrdered[k][1]:
			if k<i:
				ind=i-1-k
			else:
				ind=len(tabInOutOrdered)+i-1-k
			if not iscond(tabcomm[ind]):
				found=True
			depList.append(ind)
		k=k+1
    return depList

def list_list_dep(node_while):
    """Return a list of list of dep
        for each command (order of block_items in the while_stmt
    """
    listList = []
    i=0
    for n in node_while.stmt.block_items:
        listList.append(new_list_dep(node_while.stmt,n,i))
        i=i+1
    if DEBUG:
        print("Dependencies:")
        print(listList)
    return listList

def init_tabDeg(while_stmt):
    tabDeg = []
    for i in range(0,len(while_stmt.block_items)):
        node = while_stmt.block_items[i]
        if(isinstance(node,c_ast.FuncCall)):
            tabDeg.append(-1)
        else: tabDeg.append(0)
    return tabDeg

def max_deg_of_list(tabDeg):
    deg=-1
    for i in range(0,len(tabDeg)):
        if(tabDeg[i]>=deg):
            deg=tabDeg[i]
    return deg

def comput_deg(tabDeg,i,lldep):
    if tabDeg[i]!=0: return tabDeg[i]
    else:
        tabDeg[i]=-1
        if(len(lldep[i])==0):
            tabDeg[i]=1
            return 1
        else:
            deg=-1
            infinite = False
            for l in lldep[i]:
                tabDeg[l] = comput_deg(tabDeg,l,lldep)
                if tabDeg[l]==-1:
                    return -1
                if (tabDeg[l]>deg) and l<i:
                    deg=tabDeg[l]
                if (tabDeg[l]>=deg) and l>i:
                    deg=tabDeg[l]+1
            tabDeg[i]=deg
            return deg

def rename_node(node,k,j,deg):
    to_be_renamed=node.stmt.block_items[k]
    to_be_removed=node.stmt.block_items[j]
    rel=compute_rel(to_be_removed)
    (In,Out) = rel.in_out()
    cnVisitor = ChangeNameVisitor(Out,deg)
    cnVisitor.visit(to_be_renamed)

def create_if_from_deg(while_node,hoisted_list,rm_list,deg):
    new_list=hoisted_list
    for j in rm_list:
        for k in hoisted_list:
            if(k<j):
                rename_node(while_node,k,j,deg)
    ifList=[]
    for k in hoisted_list:
        if (k not in rm_list):
            ifList.append(k)
    return [ifList,build_If(ifList,while_node)]

def get_list_node_deg(deg,tabDeg):
    listId = []
    rm = []
    for i in range(0,len(tabDeg)):
        if(tabDeg[i]>=deg or tabDeg[i]==-1):
            listId.append(i)
            if(tabDeg[i]==deg and deg!=-1):
                rm.append(i)
    return [listId,rm]

def build_If(listId,while_node):
    nodelist = []
    for i in listId:
        nodelist.append(while_node.stmt.block_items[i])
    return c_ast.If(while_node.cond,c_ast.Compound(nodelist),None)

def final_while(listId,while_node):
    nodelist = []
    for i in listId:
        nodelist.append(while_node.stmt.block_items[i])
    return c_ast.While(while_node.cond,c_ast.Compound(nodelist))

def optimize(tabDeg,myWhile):
    maxdeg = max_deg_of_list(tabDeg)
    for deg in range(0,maxdeg):
        [ld,rm]= get_list_node_deg(deg,tabDeg)
        if(len(ld)!=0):
            [next_list,node_if] = create_if_from_deg(myWhile.node_while,ld,rm,deg)
            # myWhile.node_while=while_node
            # Add the new if before de while
            myWhile.parent[0].block_items.insert(myWhile.parent[1],node_if)
            myWhile.parent=(myWhile.parent[0],myWhile.parent[1]+1)
    # Replace the while
    [listId,rm] = get_list_node_deg(maxdeg,tabDeg)
    [next_list,node_if] = create_if_from_deg(myWhile.node_while,listId,rm,maxdeg)
    # myWhile.node_while=while_node
    myWhile.parent[0].block_items.pop(myWhile.parent[1])
    if len(next_list)!=0:
        node_while=final_while(next_list,myWhile.node_while)
        myWhile.parent[0].block_items.insert(myWhile.parent[1],node_while)
    myWhile.isOpt=True

def optimizable(myWhile):
    for subWhile in myWhile.subWhiles:
        if not subWhile.isOpt:
            return False
    return True

def comput_tabDeg(myWhile):
    ll = list_list_dep(myWhile.node_while)
    tabDeg = init_tabDeg(myWhile.node_while.stmt)
    for i in range(0,len(myWhile.node_while.stmt.block_items)):
        comput_deg(tabDeg,i,ll)
    if DEBUG:
        print("Dependence degrees:")
        print(tabDeg)
    return tabDeg

def opt(myWhile):
    if not optimizable(myWhile):
        for subWhile in myWhile.subWhiles:
            if not subWhile.isOpt:
                opt(subWhile)
    tabDeg = comput_tabDeg(myWhile)
    optimize(tabDeg,myWhile)

def equalList(l1,l2):
    remain = l2[:]
    for i in l1:
        if i not in remain:
            return False
        remain.remove(i)
    for i in remain:
        if i not in l1:
            return False
    return True

def list_var(node):
    vv = varVisitor()
    vv.visit(node)
    return vv.values

def fixpoint(rel):
    r=Relation([])
    nextR=rel
    while not r.equal(nextR):
        r=nextR
        nextR=r.composition(rel).sumRel(rel)
    return r

def compute_rel(node): #FIXME faire les opérations unaires et constantes
    generator = c_generator.CGenerator()

    if(isinstance(node,c_ast.Assignment)):
        x = node.lvalue.name
        rest = Relation([])
        rest.ajoutPropag(x)
        if(isinstance(node.rvalue,c_ast.BinaryOp)): #x=y+z
            if(not isinstance(node.rvalue.left,c_ast.Constant)):
                y=node.rvalue.left.name
                rest.ajoutPropag(y)
                rest.ajoutDep(y,x)
            if(not isinstance(node.rvalue.right,c_ast.Constant)):
                z=node.rvalue.right.name
                rest.ajoutPropag(z)
                rest.ajoutDep(z,x)
            return rest
        if(isinstance(node.rvalue,c_ast.Constant)): #x=exp(…) TODO
            rest.ajoutInit(x) # keep an eye on init
            return rest
        if(isinstance(node.rvalue,c_ast.UnaryOp)): #x=exp(…) TODO
            listVar=list_var(exp)
            rels = Relation(listVar)
            rels.ajoutInit(x) # keep an eye on init
            for v in listVar:
                rels.ajoutDep(v,x)
            return rels
    if(isinstance(node,c_ast.If)): #if cond then … else …
        relT= Relation([])
        for child in node.iftrue.block_items:
            relT = relT.composition(compute_rel(child))
        relF= Relation([])
        if(node.iffalse != None):
            for child in node.iffalse.block_items:
                relF = relF.composition(compute_rel(child))
        rels=relF.sumRel(relT)
        return rels.extendRel(node.cond)
    if(isinstance(node,c_ast.While)):
        rels= Relation([])
        for child in node.stmt.block_items:
            rels=rels.composition(compute_rel(child))
            # print("composition")
            # rels.show()
        rels=fixpoint(rels)
        rels = rels.extendRel(node.cond)
        # Et si on retirait des out les variables de boucle?
        # vs = list_var(node.cond)
        # rels.rm_out(vs)
        # print("les out du while:")
        # print(rels.in_out()[1])
        # Mauvaise idée…
        # Ou
        rels.rm_fix_dep()
        return rels
    return Relation([])


#################### TEST ####################

wv = WhileVisitor()
wv.visit(ast)
myWhile = wv.values[0]

# ast.show()
opt(myWhile)

# print("*********** FINAL CODE ****************")
generator = c_generator.CGenerator()
print(generator.visit(ast))
