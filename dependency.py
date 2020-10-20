from pycparser import c_ast
from relation import compute_rel

def compute_dependencies(loop_body):
    """Add list of dependencies for each command in the loop """
    graph = []
    tab_in_out = []
    lldep = []
    list_deg = []
    if loop_body is not None:
        if outer_break(loop_body): #if the loop contains an outer break
            for command in loop_body:
                rels_n = compute_rel(command) #compute relation for each command in loop
                if isinstance(command,(c_ast.Break)):
                    tab_in_out.append(rels_n.in_out())
                else:
                    source = [] #remove the soucre dependencies
                    target = rels_n.in_out()[1] #keep the modified variable
                    tab_in_out.append((source,target))
        else:
            for command in loop_body:
                rels_n = compute_rel(command) #compute relation for command in loop
                tab_in_out.append(rels_n.in_out()) #add tuple ([source vars],[target vars])  
        for index in range(len(loop_body)):
            lldep.append(primary_dependency(tab_in_out, index, graph, loop_body))# add list of indicies of the primary dependencies
        list_deg = compute_list_deg(lldep, loop_body) #compute list of invariance degree using dependencies
        graph.sort()
    return (graph, list_deg)

def primary_dependency(tab_in_out, target_index, graph, loop_body):
    """Find the primary dependencies for the command at target_index"""
    list_dep = []
    source_vars = tab_in_out[target_index][0]
    for var in source_vars:  #for each source var in the command
        found = False
        k = 0
        # find the primary dependency for the var
        while k < len(tab_in_out) and not found:
            source_index = target_index - k - 1
            if source_index < 0:
                source_index = len(tab_in_out) + target_index - k - 1
            if var in tab_in_out[source_index][1]: #if var is modified by the command
                if not isinstance(loop_body[source_index], (c_ast.While, c_ast.If)):
                    found = True
                if not( isinstance(loop_body[source_index], c_ast.If) and "Break()" in tab_in_out[source_index][1]): #if the dependency is not an if statement that contains a break
                    graph.append((source_index, target_index, var))#add the dependency to the graph
                    list_dep.append(source_index)# add index of the commands
            k = k + 1
    return list_dep

def compute_list_deg(lldep, loop_body):
    """Compute the invariance degrees for all the commands in a loop"""
    list_deg = init_tab_deg(loop_body)
    for i in range(0, len(loop_body)):
        if list_deg[i] != -1: #if the command can be peeled
            compute_deg(list_deg, i, lldep)  #calculate the degree of the command
    return list_deg

def init_tab_deg(loop_body):
    """" Initilize the list of invariance degrees """
    list_deg = []
    for command in loop_body:
        if isinstance(command, (c_ast.FuncCall)): #if the command cannot be removed set degree to -1
            list_deg.append(-1)
        else:
            list_deg.append(0) #set degree to 0 for all other commands
    return list_deg

def compute_deg(tab_deg, index, lldep):
    """Computes dependency degree of a given command """
    if tab_deg[index] == 0:  # if deg has not been computed
        if len(lldep[index]) == 0: # if the command has no dependencies, set deg to 1
            tab_deg[index] = 1
        else:  # else compute max degree of the commands dependencies
            tab_deg[index] = -1
            deg = -1
            for l in lldep[index]:
                # compute degree of dependency and update tab_degs
                tab_deg[l] = compute_deg(tab_deg, l, lldep)
                if tab_deg[l] == -1:  # if the command is also a dependency of l, then there is a loop
                    return tab_deg[index]
                if tab_deg[l] > deg and l < index:  # if deg(l) is the max  and l precedes the command
                    deg = tab_deg[l]
                if tab_deg[l] >= deg and l > index:  # if deg(l) is the max and l follows the command
                    deg = tab_deg[l] + 1
            tab_deg[index] = deg  # set deg of the command to the max degree
    return tab_deg[index]

def outer_break(loop):
    """Check if the while loop contains a break"""
    for command in loop:
        if isinstance(command, c_ast.Break):
            return True
    return False