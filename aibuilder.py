
class AIBuilder:
    def __init__(self):
        self.base_ai_directory = None #./base_ai
        self.destiny_ai_directory = None #~/.openttd/ai
        self.cost_file = None #base_directory/pathfinder.nut
        self.info_file = None #base_directory/info.nut
        self.main_file = None #base_directory/main.nut
        
    def build(self, args, ai_id):
        #Isso vai copiar coisas a serem reescritas depois
        #filesystem.copy(from base, to ai dir, lotsastuff)
        #TODO: tratar args
        arg_string = self.build_arg_string(args)
        self.substitute(self.cost_file, arg_string)
        #TODO: geram ai_name
        self.substitute(self.info_file, ai_name)
        self.substitute(self.main_file, ai_name)
        
    def substitute(self, target_file, content):
        #TODO: caminhos
        in_file = open(base/target, 'r')
        out_file = open(destiny/target, 'w')
        while line = in_file.readline() != '':
            #TODO: arranjar uma string menos idiota
            if line.find("changeme") != -1 :
                out_file.write(content + '\n')
            else:
                out_file.write(line)
        in_file.close()
        out_file.close()
        
    def build_arg_string(self, args):
        #too lazy
        pass
