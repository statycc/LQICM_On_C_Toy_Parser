from pycparser import c_ast
from DFG import Relation


class VarVisitor(c_ast.NodeVisitor):
    """This class finds all the variables in a command """

    def __init__(self):
        self.values = []  # list of variable names used in command

    def visit_ID(self, command):
        """Add variable name to list of values"""
        self.values.append(command.name)


def compute_rel(command, cond_var=[]):
    """Compose and create Relation depending on the type of command """
    if isinstance(command, c_ast.Assignment):
        if isinstance(command.lvalue, c_ast.ArrayRef):
            rel = compute_command(list_var(command.lvalue.name), command.rvalue, cond_var, list_var(command.lvalue.subscript))
        else:
            rel = compute_command(command.lvalue.name, command.rvalue, cond_var)
    elif isinstance(command, c_ast.Decl):
        if command.init is None:
            rel = compute_command(command.type.declname, [], cond_var)
        else:
            rel = compute_command(command.type.declname, command.init, cond_var)
    elif isinstance(command, c_ast.UnaryOp):
        var = list_var(command)
        rel = strong_dep_rel(var, var, var)
    elif isinstance(command, c_ast.If):
        cond_var = list_var(command.cond)  # get the variable in the conditional expression
        rel_true = compute_branch(command.iftrue, cond_var)  # compute the Relation of the 'then' and 'else' branch
        rel_false = compute_branch(command.iffalse, cond_var)
        rel = rel_false.sumRel(rel_true)
        rel = rel.conditionRel(cond_var)  # add conditional dependency
    elif isinstance(command, (c_ast.DoWhile, c_ast.While, c_ast.For)):
        rel = compute_loop(command)
    elif isinstance(command, c_ast.Break):
        target_var = [str(command)]
        # set a strong dependency between the source (and possible vars in the condition) to the target variable
        rel = strong_dep_rel(cond_var + target_var, target_var, cond_var)
    else:
        rel = Relation([])
    return rel


def compute_command(target, sources, cond_var, sub_var = []):
    target_var = list(target)  # variable being assigned to
    source_vars = list(set(list_var(sources)+ sub_var))
    lvars = list(set(target_var) | set(source_vars) | set(cond_var))  # remove repeat variable names
    # set a strong dependency between the source (and possible vars in the condition) to the target variable
    return strong_dep_rel(lvars, target_var, source_vars + cond_var)


def compute_branch(branch_command, cond_var):
    """ Creates Relation for branch commands (iftrue/iffalse)"""
    rel = Relation([])
    # check if the command exists and if the body is not empty
    if branch_command is not None and branch_command.block_items is not None:
        rel = compose_rel(branch_command, cond_var)  # compose the Relation for each command in the body
    return rel


def compute_loop(command):
    cond_var = list_var(command.cond)
    if command.stmt.block_items is None or command.stmt.block_items == []:
        rel = Relation([""])
    else:
        rel = compose_rel(command.stmt, cond_var)  # compose the Relations for each command in the body
        rel = rel.fixpoint()
    rel = rel.conditionRel(cond_var)
    return rel


def compose_rel(command, cond_var):
    """ Creates Relation for a sequence of commands"""
    rel = Relation([])
    for child in command.block_items:
        if isinstance(child, c_ast.Break):
            rel = rel.composition(compute_rel(child, cond_var))
            return rel  # stop computing the sequence once a break is reached
        elif isinstance(child, c_ast.Continue):
            rel_c = Relation([child]).identity()
            return rel.composition(rel_c)
        else:
            rel = rel.composition(compute_rel(child, cond_var))  # compute and compose the Relation for the child
    return rel


def list_var(command):
    """Return list of variable name in a command """
    var_visit = VarVisitor()
    var_visit.visit(command)
    return var_visit.values


def strong_dep_rel(var, target_vars, source_vars):
    """Create a Relation and add strong dependencies between source and target variables"""
    rel = Relation(var)
    rel.identity()
    return rel.algebraic([target_vars, source_vars])
