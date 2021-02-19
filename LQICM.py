from __future__ import print_function
import sys
import os
from pycparser import parse_file, c_generator, c_ast
from peel import loop_peel
from dependency import compute_dependencies

sys.path.extend([".", ".."])


class Loop:
    """This class defines a Loop object """

    def __init__(self, loop_node, parent, is_opt, inner_loops):
        """ Initialize attributes for Loop """
        self.loop_node = loop_node  # the AST node of the loop being optimized
        self.parent = parent  # tuple(node of parent, index of the command)
        self.is_opt = is_opt  # whether loop is optimized or not
        self.inner_loops = inner_loops  # list of nested loops


class LoopVisitor:
    """This class is used for visiting c_ast nodes to find and store Loops"""

    def __init__(self):
        self.values = []

    def visit(self, node, parent=None, i=-1):
        if isinstance(node, (c_ast.DoWhile, c_ast.While, c_ast.For)):
            self.loop(node, parent, i)
        else:
            for (j, (_, child)) in enumerate(node.children()):
                self.visit(child, node, j)

    def loop(self, node, parent, i):
        loop_visit = LoopVisitor()
        loop_visit.visit(node.stmt)
        loop = Loop(node, (parent, i), False, loop_visit.values)
        self.values.append(loop)
        if isinstance(node, (c_ast.DoWhile, c_ast.For)):
            convert(loop)


def convert(node):
    loop_node = node.loop_node
    parent_index = node.parent[1]  # index in the AST of the original loop
    node.parent[0].block_items.pop(parent_index)  # remove the original loop from AST
    body = []  # list of new AST nodes for each peel
    original_body = []
    if loop_node.stmt.block_items is not None:
        original_body = loop_node.stmt.block_items
    if isinstance(loop_node, c_ast.For):
        if loop_node.init is not None:
            body.append(loop_node.init.decls[0])  # add the initialization of the loop var before the loop
        if loop_node.next is not None:
            loop_node.stmt = c_ast.Compound(
                original_body + [loop_node.next])  # add the inc/dec of the loop var at the end of the body
        body.append(c_ast.While(loop_node.cond, loop_node.stmt))
    if isinstance(loop_node,
                  c_ast.DoWhile):  # if loop is a DoWhile, add the commands of the first peel outside of the loop
        for i in original_body:  # add each command to the modified AST
            body.append(i)
        body.append(c_ast.While(loop_node.cond, c_ast.Compound(original_body)))
    for i in body:  # add new nodes to the modified AST
        node.parent[0].block_items.insert(parent_index, i)
        parent_index = parent_index + 1
    node.parent = (node.parent[0], parent_index - 1)  # update the parent


def opt(loop):
    """Finds the inner-most loop that can be optimized and peels it """
    for inner_loop in loop.inner_loops:
        if not inner_loop.is_opt:
            opt(inner_loop)  # optimize the inner loop if it has not been opimized yet
    (graph, list_deg) = compute_dependencies(loop.loop_node.stmt.block_items)  # compute the dependencies of the loop
    loop_peel(graph, list_deg, loop)  # peel the loop based on its dependencies
    return graph, list_deg


def visit_ast(ast):
    """Creates a LoopVisitor object to find the loops in a program """
    loop_visit = LoopVisitor()
    loop_visit.visit(ast)
    return loop_visit.values  # list of all the outer-most loops in a program


def optimize(filename):
    """ Parses the file and modifies the AST"""
    ast = parse_file(filename, use_cpp=True, cpp_path="gcc", cpp_args=['-E'])  # replace cpp with gcc to remove comments
    loops = visit_ast(ast)
    deps = []
    for i in range(len(loops)):
        deps.append(opt(loops[i]))
        loops = visit_ast(ast)
    generator = c_generator.CGenerator()
    newast = generator.visit(ast)
    with open(os.path.join('./output/', "opt_" + os.path.basename(filename)), "w")  as text_file:
        print(format(newast), file=text_file)
    return deps


if __name__ == "__main__":
    if len(sys.argv) > 1:
        optimize(sys.argv[1])
    else:
        import doctest
        doctest.testfile("test_examples.txt")
