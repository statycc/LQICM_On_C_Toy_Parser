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

from DFG import *

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])

from pycparser import parse_file, c_parser, c_ast, c_generator

DEBUG_LEVEL = 1
NVIND = -1

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


def DepGraph(node_while):
	graph = []
	lldep = []
	i=0
	for node in node_while.stmt.block_items:
		lldep.append(add_dep_node(node,i,node_while.stmt,graph))
		i=i+1
	if DEBUG_LEVEL>=1:
		print("Dependence Graph:")
		print(graph)
        print("List of List of Dependencies:")
        print(lldep)
	return (graph,lldep)

def add_dep_node(command,i,while_stmt,graph):
    """Adds dependencies for a given command
    """
    listDep = []
    relsC=compute_rel(command)
    (InC,OutC) = relsC.in_out()
    tabcomm=[]
    tabInOut=[]
    for n in while_stmt.block_items:
        relsN = compute_rel(n)
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
                graph.append((ind,i,var))
                listDep.append(ind)
            k=k+1
    return listDep


def init_tabDeg(while_stmt):
    tabDeg = []
    for i in range(0,len(while_stmt.block_items)):
        node = while_stmt.block_items[i]
        if(isinstance(node,c_ast.FuncCall)):
            tabDeg.append(-1)
        else:
            tabDeg.append(0)
    return tabDeg

def max_deg_of_list(tabDeg):
    deg=-1
    for i in range(0,len(tabDeg)):
        if(tabDeg[i]>=deg):
            deg=tabDeg[i]
    return deg

def comput_deg(tabDeg,i,lldep):
    if DEBUG_LEVEL>=2:
        print("DEBUG tabDeg.")
        print(tabDeg)
    if tabDeg[i]!=0:
        return tabDeg[i]
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

def create_if_from_deg(while_node,hoisted_list,rm_list,deg,graph):
    ifList=[]
    for k in hoisted_list:
        ifList.append(k)
        if (k not in rm_list):
            ifList.append(k)
    return [ifList,build_If(ifList,rm_list,while_node,graph)]

def get_list_node_deg(deg,tabDeg):
    listId = []
    rm = []
    for i in range(0,len(tabDeg)):
        if(tabDeg[i]>=deg or tabDeg[i]==-1):
            listId.append(i)
            if(tabDeg[i]==deg and deg!=-1):
                rm.append(i)
    return [listId,rm]

def new_var():
    global NVIND
    NVIND=NVIND+1
    return "å"+str(NVIND)

def is_used(var,i,tabDeg,graph):
    deg_max=0
    bool=False
    greater=False
    for (x,y,z) in graph:
        if x==i and z==var:
            bool=True
            greater=y>x
            if greater and tabDeg[y]>deg_max and deg_max!=-1:
                deg_max=tabDeg[y]
            if not greater and tabDeg[y]-1>deg_max and deg_max!=-1:
                deg_max=tabDeg[y]-1
            if tabDeg[y]==-1:
                deg_max=-1
    return (bool,deg_max)


def create_capture_node(new_vars,var,i,while_node):
    tab=[]
    tab.append(c_ast.Assignment("=",c_ast.ID(new_vars[0]),c_ast.ID(var)))
    if iscond(while_node.stmt.block_items[i]):
        tab.append(c_ast.Assignment("=",c_ast.ID(new_vars[1]),while_node.stmt.block_items[i].cond))
    tab.reverse()
    return tab

def create_recover_node(new_vars,var,i,while_node):
    new_node = c_ast.Assignment("=",c_ast.ID(var),c_ast.ID(new_vars[0]))
    if iscond(while_node.stmt.block_items[i]):
        new_node=c_ast.If(c_ast.ID(new_vars[1]),c_ast.Compound([new_node]),None)
    return new_node

def captures(i,while_node,tabDeg,graph):
    Rel=compute_rel(while_node.stmt.block_items[i])
    capture_tab=[]
    recover_tab=[]
    for var in Rel.out():
        IsUsed=is_used(var,i,tabDeg,graph)
        if IsUsed[0]:
            newVars=[new_var(),new_var()]
            capture_tab.append((create_capture_node(newVars,var,i,while_node),IsUsed[1]))
            recover_tab.append((create_recover_node(newVars,var,i,while_node),IsUsed[1]))
    return (capture_tab,recover_tab)

def optimize_new(graph,tabDeg,myWhile):
    maxdeg = max_deg_of_list(tabDeg)
    while_node=myWhile.node_while
    peeling_deg=maxdeg+1
    if peeling_deg==0:
        myWhile.isOpt=True
        return 0
    initial_indices = []
    tabDegs=[]
    nodelists=[]
    listIf=[]
    for i in range(peeling_deg):
        nodelists.append([])
        tabDegs.append([])
        initial_indices.append([])
    for i in range(len(tabDeg)):
        for j in range(len(initial_indices)):
            initial_indices[j].append(i)
    for deg in tabDeg:
        for i in range(len(tabDegs)):
            tabDegs[i].append(deg)
    for node in while_node.stmt.block_items:
        for i in range(peeling_deg):
            nodelists[i].append(node)
    for i in range(maxdeg):
        tbrm=[]
        for init_ind in initial_indices[i]:
            if init_ind!=-1:
                if tabDeg[init_ind]==i+1:
                    tbrm.append(init_ind)
        for init_ind in tbrm:
            curr_ind=initial_indices[i].index(init_ind)
            (capture_tab,recover_tab)=captures(init_ind,myWhile.node_while,tabDeg,graph)
            for capture in capture_tab:
                if capture[1]==-1 or capture[1]>i+1:
                    for k in range(len(capture[0])):
                        nodelists[i].insert(curr_ind+1,capture[0][k])
                        initial_indices[i].insert(curr_ind+1,-1)
            for j in range(i+1,peeling_deg):
                curr_ind=initial_indices[j].index(init_ind)
                for (recover,deg) in recover_tab:
                    if deg==-1 or deg>j:
                        nodelists[j].insert(curr_ind+1,recover)
                        initial_indices[j].insert(curr_ind+1,-1)
                nodelists[j].pop(curr_ind)
                initial_indices[j].pop(curr_ind)
        if DEBUG_LEVEL>=3:
            print(maxdeg,nodelists,initial_indices)
        listIf.append(c_ast.If(while_node.cond,c_ast.Compound(nodelists[i]),None))
    listIf.append(c_ast.While(while_node.cond,c_ast.Compound(nodelists[maxdeg]),None))
    myWhile.parent[0].block_items.pop(myWhile.parent[1])
    listIf.reverse()
    for node in listIf:
        myWhile.parent[0].block_items.insert(myWhile.parent[1],node)
    myWhile.show()
    myWhile.isOpt=True


def optimizable(myWhile):
    for subWhile in myWhile.subWhiles:
        if not subWhile.isOpt:
            return False
    return True

def comput_tabDeg(myWhile):
    (graph,lldep) = DepGraph(myWhile.node_while)
    tabDeg = init_tabDeg(myWhile.node_while.stmt)
    for i in range(0,len(myWhile.node_while.stmt.block_items)):
        comput_deg(tabDeg,i,lldep)
    if DEBUG_LEVEL>=1:
        print("Dependence degrees:")
        print(tabDeg)
    return (graph,tabDeg)

def opt(myWhile):
    if not optimizable(myWhile):
        for subWhile in myWhile.subWhiles:
            if not subWhile.isOpt:
                opt(subWhile)
    (graph,tabDeg) = comput_tabDeg(myWhile)
    optimize_new(graph,tabDeg,myWhile)

def list_var(node):
    vv = varVisitor()
    vv.visit(node)
    return vv.values

def compute_rel(node): #FIXME faire les opérations unaires et constantes
    generator = c_generator.CGenerator()

    if(isinstance(node,c_ast.Assignment)):
        x = node.lvalue.name
        dblist=[[x],[]]
        if(isinstance(node.rvalue,c_ast.BinaryOp)): #x=y+z
            if(not isinstance(node.rvalue.left,c_ast.Constant)):
                y=node.rvalue.left.name
                dblist[1].append(y)
            if(not isinstance(node.rvalue.right,c_ast.Constant)):
                z=node.rvalue.right.name
                dblist[1].append(z)
            listvar=list(set(dblist[0])|set(dblist[1]))
            rest=Relation(listvar)
            rest.identity()
            rest.algebraic(dblist)
            if DEBUG_LEVEL>=2:
                print("DEBUG_LEVEL: Computing Relation (first case)")
                node.show()
                rest.show()
            return rest
        if(isinstance(node.rvalue,c_ast.Constant)): #x=exp(…) TODO
            rest=Relation([x])
            if DEBUG_LEVEL>=2:
                print("DEBUG_LEVEL: Computing Relation (second case)")
                node.show()
                rest.show()
            return rest
        if(isinstance(node.rvalue,c_ast.UnaryOp)): #x=exp(…) TODO
            listVar=list_var(exp)
            rels = Relation([x]+listVar)
            rels.identity()
            rels.algebraic([[x],listVar])
            if DEBUG_LEVEL>=2:
                print("DEBUG: Computing Relation  (third case)")
                node.show()
                rels.show()
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
        rels=rels.conditionRel(list_var(node.cond))
        if DEBUG_LEVEL>=2:
            print("DEBUG_LEVEL: Computing Relation (conditional case)")
            node.show()
            rels.show()
        return rels
    if(isinstance(node,c_ast.While)):
        rels= Relation([])
        for child in node.stmt.block_items:
            rels=rels.composition(compute_rel(child))
        rels = rels.fixpoint()
        rels = rels.conditionRel(list_var(node.cond))
        if DEBUG_LEVEL>=2:
            print("DEBUG_LEVEL: Computing Relation (loop case)")
            node.show()
            rels.show()
        return rels
    return Relation([])


#################### TEST ####################

wv = WhileVisitor()
wv.visit(ast)
myWhile = wv.values[0]

# ast.show()
opt(myWhile)

# print("*********** FINAL CODE ****************")
if DEBUG_LEVEL>=3:
    ast.show()
generator = c_generator.CGenerator()
print(generator.visit(ast))
