# -*- coding: UTF-8 -*-
from pycparser import c_ast

NVIND = -1


def new_var():
    global NVIND
    NVIND = NVIND + 1
    return "å" + str(NVIND)


def loop_peel(graph, list_deg, loop):
    """Peel the loop based on the maximum invariance degree"""
    peeling_deg = max_deg_of_list(list_deg) + 1
    if peeling_deg != 0:  # if loop can be peeled
        loop_node = loop.loop_node
        parent_index = loop.parent[1]  # index in the AST of the original loop
        loop.parent[0].block_items.pop(parent_index)  # remove the orignal loop from AST
        commands = init_commands(peeling_deg,
                                 loop_node.stmt.block_items)  # initialize all the commands in the body of the loop
        peel = []  # list of AST nodes for each peel
        for i in range(peeling_deg):
            peel_body = []  # list of commands for current peel
            for (node, ind) in commands[i]:
                # if the command can be peeled and has reached its peeling degree
                if ind != -1 and list_deg[ind] == i + 1:
                    (capture_tab, recover_tab) = captures(ind, loop_node.stmt.block_items, list_deg, graph)
                    add_new_vars(commands, i, node, ind, peeling_deg, capture_tab, recover_tab)
                peel_body.append(node)

            # if its the last peel, add the body to a while statement with the same cond exp as the original while loop
            if i == peeling_deg - 1:
                peel.append(c_ast.While(loop_node.cond, c_ast.Compound(peel_body)))
            else:  # if not last peel, add the body to an if statement with the same cond exp as the original while loop
                peel.append(c_ast.If(loop_node.cond, c_ast.Compound(peel_body), None))

        # if the loop contains a break/contiue, wrap the entire peeled loop inside of a while loop with the same cond
        # exp as the original
        if check_break(loop_node.stmt):
            peel = c_ast.While(loop_node.cond, c_ast.Compound(peel + [c_ast.Break()]), None)
            loop.parent[0].block_items.insert(parent_index, peel)
        else:
            for i in peel:  # add each peel to the modified AST
                loop.parent[0].block_items.insert(parent_index, i)
                parent_index = parent_index + 1

    loop.isOpt = True


def add_new_vars(commands, i, node, ind, peeling_deg, capture_tab, recover_tab):
    """Add capture and recover nodes and remove the command from all future peels """
    new_ind = commands[i].index((node, ind))
    for (new_node, deg) in capture_tab:
        if deg == -1 or deg > i + 1:
            for k in range(len(new_node)):
                commands[i].insert(new_ind + 1, (new_node[k], -1))

    for j in range(i + 1, peeling_deg):
        new_ind = commands[j].index((node, ind))
        for (new_node, deg) in recover_tab:
            if deg == -1 or deg > j:
                commands[j].insert(new_ind + 1, (new_node[0], -1))
        commands[j].pop(new_ind)


def captures(index, while_body, list_deg, graph):
    """Check if the command being peeled is a source and creates new nodes to store the variables value"""
    capture_tab = []
    recover_tab = []
    var_out = is_source(index, graph, list_deg)
    for (var, deg_max) in var_out:
        new_vars = [new_var(), new_var()]  # create two unique variable names
        capture_tab.append((create_capture_node(new_vars, var, index, while_body), deg_max))
        recover_tab.append((create_recover_node(new_vars, var, index, while_body), deg_max))
    return (capture_tab, recover_tab)


def is_source(cur_ind, graph, list_deg):
    """Check if the variable modified in the current command is used as a source for any other command in the loop """
    used = False
    var_out = []
    deg_max = 0
    for (source_ind, target_ind, used_var) in graph:
        if source_ind == cur_ind and not used:
            used = True
            if list_deg[target_ind] == -1:
                deg_max = -1
            else:
                if target_ind > source_ind and list_deg[target_ind] > deg_max:
                    deg_max = list_deg[target_ind]
                if not target_ind > source_ind and list_deg[target_ind] - 1 > deg_max:
                    deg_max = list_deg[target_ind] - 1
            var_out.append((used_var, deg_max))
    return var_out


def create_capture_node(new_vars, var, index, while_body):
    """Create an assignment capture node (new_vars = var)"""
    tab = []
    if isinstance(while_body[index], (c_ast.While, c_ast.If)):
        tab.append(c_ast.Assignment("=", c_ast.ID(new_vars[1]), while_body[index].cond))
    tab.append(c_ast.Assignment("=", c_ast.ID(new_vars[0]), c_ast.ID(var)))
    return tab


def create_recover_node(new_vars, var, index, while_body):
    """Create an assignment recovery node (var = new_var) """
    new_node = c_ast.Assignment("=", c_ast.ID(var), c_ast.ID(new_vars[0]))
    if isinstance(while_body[index], (c_ast.While, c_ast.If)):
        new_node = c_ast.If(c_ast.ID(new_vars[1]), c_ast.Compound([new_node]), None)
    return [new_node]


def check_break(node):
    """Check if the while loop comtains a break or continue """
    if node is not None and node.block_items is not None:
        for command in node.block_items:
            if isinstance(command, c_ast.Continue) or isinstance(command, c_ast.Break):
                return True
            if isinstance(command, c_ast.If):
                if check_break(command.iftrue) or check_break(command.iffalse):
                    return True
    return False


def max_deg_of_list(list_deg):
    """Compute max invariance degree of all the commands """
    deg = -1
    for com_deg in list_deg:
        if com_deg >= deg:
            deg = com_deg
    return deg


def init_commands(peeling_deg, block_items):
    """ Initialize the commands in the body of the loop
      commands: list of list of tuples
          each list in the list corresponds to a 'peel' in a loop
          each tuple (node,i) contains the AST node and the corresponding ind """
    commands = []
    index = 0
    for i in range(peeling_deg):
        commands.append([])  # each list added corresponds to a 'peel' in a loop
    if block_items is not None:
        for node in block_items:
            for i in range(peeling_deg):
                commands[i].append(
                    (node, index))  # each tuple (node,i) contains the AST node and the corresponding index
            index = index + 1
    return commands
