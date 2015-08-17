
import shutil
import config

class AIBuilder:
    def __init__(self):
        self.base_dir = config.base_dir #./base_ai
        self.target_dir = config.target_dir #~/.openttd/ai
        #TODO: definir e/ou verificar coisas abaixo
        self.cost_file = 'costs.nut' #base_directory/pathfinder.nut
        self.info_file = 'info.nut' #base_directory/info.nut
        self.main_file = 'main.nut' #base_directory/main.nut
        self.base_name = 'test_ai'
        
    def build(self, args, ai_id):
        #Isso vai copiar inclusive coisas a serem reescritas depois
        #TODO: tratar erros
        try:
            shutil.copytree(self.base_dir, self.target_dir)
        except OSError as e:
            #Error 17: arquivo já existe
            #Não vamos tratar caso seja outro erro
            if e.errno != 17:
                raise
            #TODO: arranjar alguma coisa pra resolver esse caso
            raise
        #TODO: tratar args
        arg_string = self.build_arg_string(args)
        self.substitute(self.cost_file, arg_string)
        
        ai_name = self.base_name + str(ai_id)
        self.substitute(self.info_file, ai_name)
        self.substitute(self.main_file, ai_name)
        
    def substitute(self, target_file, content):
        base_path = self.base_dir + target_file
        target_path = self.target_dir + target_file
        base_file = open(base_path, 'r')
        target_file = open(target_path, 'w')
        line = base_file.readline()
        while line != '':
            #TODO: arranjar uma string menos idiota
            if line.find("changeme") != -1 :
                target_file.write(content + '\n')
            else:
                target_file.write(line)
        base_file.close()
        target_file.close()
        
    def build_arg_string(self, args):
        #too lazy
        pass
