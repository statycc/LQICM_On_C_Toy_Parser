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

class Relation():
    def __init__(self,variables):
        self.variables = variables
        self.propag = variables[:]
        self.dep = []
        self.init = []

    def ajoutPropag(self,v):
        self.propag.append(v)
        self.ajoutVar(v)

    def ajoutVar(self,x):
        if x not in self.variables:
            self.variables.append(x)

    def ajoutDep(self,x,y):
        if (x,y) not in self.dep:
            self.dep.append((x,y))
            self.ajoutVar(x)
            self.ajoutVar(y)
            if y in self.propag:
                self.propag.remove(y)

    def ajoutInit(self,x):
        if x not in self.init:
            self.init.append(x)
            self.ajoutVar(x)
            if x in self.propag:
                self.propag.remove(x)

    def removeDep(self,x,y):
        self.dep.remove((x,y))

    def show(self):
        print("Variables:")
        print(self.variables)
        print("Dépendences:")
        print(self.dep)
        print("Propagations:")
        print(self.propag)

    def composition(self,r2):
        if len(self.variables) == 0:
            return r2
        if len(r2.variables) == 0:
            return self
        listVar = list(set(self.variables + r2.variables))
        comp = Relation(listVar)
        for (x2,y2) in r2.dep:
            if x2 not in self.variables:
                comp.ajoutDep(x2,y2)
            elif x2 in self.propag:
                comp.ajoutDep(x2,y2)
            for (x1,y1) in self.dep:
                if y1 == x2:
                    comp.ajoutDep(x1,y2)
                if y1 not in r2.variables:
                    comp.ajoutDep(x1,y1)
                elif y1 in r2.propag:
                    comp.ajoutDep(x1,y1)
        return comp

    def sumRel(self,r2): # Revoir la sum plus tard…
        listVar = list(set(self.variables + r2.variables))
        sumRel = Relation([])
        sumRel.variables = listVar
        sumRel.propag = list(set(self.propag + r2.propag))
        sumRel.dep = list(set(self.dep + r2.dep))
        # sumRel.init = list(set(self.init + r2.init))
        return sumRel

    def out(self):
        out = []
        for (x,y) in self.dep:
            if y not in out:
                out.append(y)
        return out

    def in_out(self):
        out = self.init[:]
        in_ = []
        for (x,y) in self.dep:
            if y not in out:
                out.append(y)
            if x not in in_:
                in_.append(x)
        return (in_,out)

    def rm_out(self,vars_to_rm):
        for (x,y) in self.dep:
            if y in vars_to_rm:
                self.removeDep(x,y)

    def rm_fix_dep(self):
        for (x,y) in self.dep:
            if x == y:
                self.dep.remove((x,y))

    def extendRel(self,cond):
        vs = list_var(cond)
        extendRel = self
        # print("self.out ="+str(self.out()))
        for v in vs:
            extendRel.ajoutPropag(v)
            for y in self.out():
                extendRel.ajoutDep(v,y)
        return extendRel

    def equal(self,r2):
        if not equalList(self.dep,r2.dep):
            return False
        if not equalList(self.propag,r2.propag):
            return False
        return True

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

def new_list_dep(while_stmt,command):
    """Return a list of dep
        for the given command
    """
    depList = []
    ind=0
    relsC=compute_rel(command)
    (InC,OutC) = relsC.in_out()
    # print("inC="+str(InC))
    # FIXME TO optimize
    for n in while_stmt.block_items:
        relsN=compute_rel(n)
        (InN,OutN) = relsN.in_out()
        # print("OutN="+str(OutN))
        if exist_rel(InC,OutN):
            # print("exist rel with "+str(ind))
            depList.append(ind)
        ind+=1
    return depList

def list_list_dep(node_while):
    """Return a list of list of dep
        for each command (order of block_items in the while_stmt
    """
    listList = []
    for n in node_while.stmt.block_items:
        listList.append(new_list_dep(node_while.stmt,n))
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
            ind=1
            deg=-1
            for l in lldep[i]:
                tabDeg[l] = comput_deg(tabDeg,l,lldep)
                if(tabDeg[l]>=deg):
                    deg=tabDeg[l]
                    ind=l
            # [ind,deg] = max_deg_of_list(lldep[i])
            if deg!=-1 and ind>i:
                tabDeg[i]=deg+1
            else: tabDeg[i]=deg
            return tabDeg[i]

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
