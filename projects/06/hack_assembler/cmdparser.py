"""
the parser object that splits a C command into its components
"""


class Parser(object):
    def __init__(self, cmd_str):
        if ';' in cmd_str:
            parts = cmd_str.split(';')
            self.jump_str = parts[1]
            rem = parts[0]
            if '=' in rem:
                rem_parts = rem.split('=')
                self.dest_str = rem_parts[0]
                self.comp_str = rem_parts[1]
            else:
                self.dest_str = ''
                self.comp_str = rem
        else:
            self.jump_str = ''
            if '=' in cmd_str:
                parts = cmd_str.split('=')
                self.dest_str = parts[0]
                self.comp_str = parts[1]
            else:
                self.dest_str = ''
                self.comp_str = cmd_str

    def dest(self):
        return self.dest_str

    def comp(self):
        return self.comp_str

    def jump(self):
        return self.jump_str
