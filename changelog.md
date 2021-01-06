# ChangeLog

## [2.0.0](https://github.com/ThomasRuby/LQICM_On_C_Toy_Parser/tree/7e590e400a84ca8d585535c24c06a2b3ef39bf7f) (2020-10-20)

### Added
- handle DoWhile and For Loops
- loops with break/continue
- unary operation (inc/dec)
- assignments consisting of one or more variables
- create relation for declaration commands
- create empty relation to not crash on empty loops
- keep empty loop if all commands are peeled
- peel all loops in a program instead of only the first loop
- relation.py for creating relations from AST nodes
- dependency.py for creating dependency graph and computing invariance degrees 
- peel.py for peeling loops and modifying the AST accordingly
- examples for loops containing breaks
- convert function to transform dowhile and for loops to modified while loops
- peel for loops with no initialization or update
- peel loops that contain breaks not within if statements
- documented source code
- created examples for different test cases 
- different options for testing programs (either as command line argument or through doctest)

## Changed
- store commands as a list of tuples containing the AST node and index
- improve computing invariance degrees
- changed 'captures' method, instead of recomputing the relation for each command in a loop, use the existing dependency graph and current index to find the used variables
- handling break commands by removing dependencies to the previous commands in a sequence
- ignore dependency if the source is an if statement containing a break

## Removed
- unused classes (ChangeNameVisitor)
- unused functions (get_first_while, exist_rel, create_if_from_deg )
- case for dowhile/for loops when peeling


## [1.0.0](https://github.com/ThomasRuby/LQICM_On_C_Toy_Parser/tree/69276fc9d80b3d2d2fdff74375c5714aead23c15) (2017-05-09)

Initial release