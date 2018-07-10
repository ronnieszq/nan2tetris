import os


def write_arithmetic(arg, count):
    univar = '@SP\nA=M-1\n'
    bivar = '@SP\nAM=M-1\nD=M\nA=A-1\n'
    if arg == 'add':
        asm_cmds = bivar + 'M=D+M\n'
    elif arg == 'sub':
        asm_cmds = bivar + 'M=M-D\n'
    elif arg == 'neg':
        asm_cmds = univar + 'M=-M\n'
    elif arg == 'eq':
        asm_cmds = bivar + 'D=M-D\n'
        asm_cmds += '@RET_ADDRESS_EQ.{}\n'.format(count)
        asm_cmds += 'D;JEQ\n@SP\nA=M-1\nM=0\n'
        asm_cmds += '@END_EQ\n0;JMP\n'
        asm_cmds += '(RET_ADDRESS_EQ.{})\n'.format(count)
        asm_cmds += '@SP\nA=M-1\nM=-1\n'
        asm_cmds += '(END_EQ)\n'
        count += 1
    elif arg == 'gt':
        asm_cmds = bivar + 'D=M-D\n'
        asm_cmds += '@RET_ADDRESS_GT.{}\n'.format(count)
        asm_cmds += 'D;JGT\n@SP\nA=M-1\nM=0\n'
        asm_cmds += '@END_GT\n0;JMP\n'
        asm_cmds += '(RET_ADDRESS_GT.{})\n'.format(count)
        asm_cmds += '@SP\nA=M-1\nM=-1\n'
        asm_cmds += '(END_GT)\n'
        count += 1
    elif arg == 'lt':
        asm_cmds = bivar + 'D=M-D\n'
        asm_cmds += '@RET_ADDRESS_LT.{}\n'.format(count)
        asm_cmds += 'D;JLT\n@SP\nA=M-1\nM=0\n'
        asm_cmds += '@END_LT\n0;JMP\n'
        asm_cmds += '(RET_ADDRESS_LT.{})\n'.format(count)
        asm_cmds += '@SP\nA=M-1\nM=-1\n'
        asm_cmds += '(END_LT)\n'
        count += 1
    elif arg == 'and':
        asm_cmds = bivar + 'M=D&M\n'
    elif arg == 'or':
        asm_cmds = bivar + 'M=D|M\n'
    else:
        asm_cmds = univar + 'M=!M\n'
    return asm_cmds, count


def write_push(arg1, arg2, bname):
    stack_push = '@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    # get value to push to the stack into D
    if arg1 == 'static':
        asm_cmds = '@{0}.{1}\nD=M\n'.format(bname, arg2)
    else:
        memory_map = {'local': 'LCL', 'argument': 'ARG',
                      'this': 'THIS', 'that': 'THAT', 'temp': '5'}
        if arg1 == 'pointer':
            if arg2 == 0:
                asm_cmds = '@THIS\nD=M\n'
            else:
                asm_cmds = '@THAT\nD=M\n'
        else:
            asm_cmds = '@{}\nD=A\n'.format(arg2)
            if arg1 in memory_map:
                asm_cmds += '@{}\nA=D+M\nD=M\n'.format(memory_map[arg1])
    asm_cmds += stack_push
    return asm_cmds


def write_pop(arg1, arg2, bname):
    stack_pop = '@SP\nM=M-1\nA=M\nD=M\n'
    # assign the value in D to the memory segment
    if arg1 == 'static':
        asm_cmds = stack_pop + '@{0}.{1}\nM=D\n'.format(bname, arg2)
    else:
        memory_map = {'local': 'LCL', 'argument': 'ARG',
                      'this': 'THIS', 'that': 'THAT', 'temp': '5'}
        if arg1 == 'pointer':
            if arg2 == 0:
                asm_cmds = stack_pop + '@THIS\nM=D\n'
            else:
                asm_cmds = stack_pop + '@THAT\nM=D\n'
        else:
            asm_cmds = '@{0}\nD=A\n@{1}\nD=D+M\n@R13\nM=D\n'.format(arg2, memory_map[arg1])
            asm_cmds += stack_pop
            asm_cmds += '@R13\nA=M\nM=D\n'
    return asm_cmds


def write_label(arg):
    return '(' + arg + ')\n'


def write_goto(arg):
    return '@{}\n0;JMP\n'.format(arg)


def write_if(arg):
    return '@{}\nM+1;JEQ\n'.format(arg)


def write_function(arg1, arg2):
    asm_cmds = '(' + arg1 + ')\n'
    asm_cmds += '@SP\nM=M+1\nA=M-1\nM=0\n' * arg2
    return asm_cmds


def write_call(arg1, arg2, count):
    """
    arg1: name of the callee function
    arg2: number of local variables of the function
    count: used for generating unique return labels
    """
    # push the function call return label
    asm_cmds = '@RET_ADDRESS_CALL.{}\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'.format(count)
    asm_cmds += '@LCL\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'  # save LCL
    asm_cmds += '@ARG\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'  # save ARG
    asm_cmds += '@THIS\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'  # save THIS
    asm_cmds += '@THAT\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'  # save THAT
    asm_cmds += '@{}\nD=A\n@R5\nD=D+A\n'.format(arg2)
    asm_cmds += '@SP\nD=M-D\n@ARG\nM=D\n'  # ARG = SP-5-nArgs
    asm_cmds += '@SP\nD=M\n@LCL\nM=D\n'  # LCL = SP
    asm_cmds += write_goto(arg1)
    asm_cmds += write_label('RET_ADDRESS_CALL.{}'.format(count))
    count += 1
    return asm_cmds


def write_return(bname, count):
    asm_cmds = '@LCL\nD=M\n@R14\M=D\n'  # save endFrame into a temporary variable
    asm_cmds += '@R5\nD=A\n@R14\nD=M-D\nA=D\nD=M\n'  # value in (endFrame-5)
    ret_addr_lbl = '{}$ret.{}'.format(bname, count)
    asm_cmds += '@{}\nM=D\n'.format(ret_addr_lbl)
    asm_cmds += '@SP\nAM=M-1\nD=M\n@ARG\nM=D\n'  # reposition the return value
    asm_cmds += '@SP\nM=D+1\n'  # reposition the SP of the caller
    asm_cmds += '@R14\nD=M-1\nA=D\nD=M\n@THAT\nM=D\n'  # restore THAT
    asm_cmds += '@R2\nD=A\n@R14\nD=M-D\nA=D\nD=M\n@THAT\nM=D\n'  # restore THIS
    asm_cmds += '@R3\nD=A\n@R14\nD=M-D\nA=D\nD=M\n@ARG\nM=D\n'  # restore ARG
    asm_cmds += '@R4\nD=A\n@R14\nD=M-D\nA=D\nD=M\n@LCL\nM=D\n'  # restore LCL
    asm_cmds += write_goto(ret_addr_lbl)
    count += 1
    return asm_cmds


def write_init():
    return '@256\nD=A\n@SP\nM=D\n' + write_call('sys.init', 0, 0)


input_file = r'/home/ronnie/Documents/nand2tetris/projects/07/MemoryAccess/StaticTest/StaticTest.vm'
output_file = input_file.split('.')[0] + '.asm'
fname = os.path.basename(input_file).split('.')[0]
with open(input_file, 'r') as f:
    lines = f.readlines()
cmds = ''
count = 1
for line in lines:
    if line.strip().split('//')[0]:
        comp = line.split()
        if comp[0] == 'push':
            arg1 = comp[1]
            arg2 = int(comp[2])
            cmds += '// ' + line
            cmds += write_push(arg1, arg2, fname)
        elif comp[0] == 'pop':
            arg1 = comp[1]
            arg2 = int(comp[2])
            cmds += '// ' + line
            cmds += write_pop(arg1, arg2, fname)
        elif comp[0] == 'label':
            arg = comp[1]
            cmds += '// ' + line
            cmds += write_label(arg)
        elif comp[0] == 'goto':
            arg = comp[1]
            cmds += '// ' + line
            cmds += write_goto(arg)
        elif comp[0] == 'if-goto':
            arg = comp[1]
            cmds += '// ' + line
            cmds += write_if(arg)
        elif comp[0] == 'function':
            arg1 = comp[1]
            arg2 = int(comp[2])
            cmds += '// ' + line
            cmds += write_function(arg1, arg2)
        elif comp[0] == 'call':
            arg1 = comp[1]
            arg2 = int(comp[2])
            cmds += '// ' + line
            cmds += write_call(arg1, arg2, count)
        elif comp[0] == 'return':
            cmds += '// ' + line
            cmds += write_return(fname, count)
        else:
            arg = comp[0]
            cmds += '// ' + line
            result = write_arithmetic(arg, count)
            cmds += result[0]
            count = result[1]
with open(output_file, 'w') as o:
    o.write(cmds)
