
# -*- coding: UTF-8 -*-

import shutil
import config

class AIBuilder:
    def __init__(self):
        self.base_dir = config.base_dir #./base_ai
        self.target_dir = config.target_dir #~/.openttd/ai
        #TODO: definir e/ou verificar coisas abaixo
        self.cost_file = 'pathfinder.nut' #base_directory/pathfinder.nut
        self.info_file = 'info.nut' #base_directory/info.nut
        self.main_file = 'main.nut' #base_directory/main.nut
        self.base_name = 'test_ai'
        
    def build(self, args, ai_id):
        #Isso vai copiar inclusive coisas a serem reescritas depois
        #TODO: tratar erros
        ai_name = self.base_name + str(ai_id)
        target_dir = self.target_dir + "/" + ai_name
        print target_dir
        try:
            shutil.copytree(self.base_dir, target_dir)
        except OSError as e:
            #Error 17: arquivo já existe
            #Não vamos tratar caso seja outro erro
            if e.errno != 17:
                raise
            #TODO: arranjar alguma coisa pra resolver esse caso
            shutil.rmtree(target_dir)
        #TODO: tratar args
        arg_string = self.build_arg_string(args)
        self.substitute(self.cost_file, arg_string)
        
        aux = '	function GetName() {return "%s"}\n\tfunction CreateInstance() {return "%s"}"; }' % (ai_name, ai_name)
        self.substitute(self.info_file, aux)
        aux = 'AICompany.SetName("{}");'.format(ai_name)
        self.substitute(self.main_file, aux)
        
    def substitute(self, target_file, content):
        base_path = self.base_dir + '/' + target_file
        target_path = self.target_dir+ '/' + target_file
        base_file = open(base_path, 'r')
        target_file = open(target_path, 'w')
        line = base_file.readline()
        while line != '':
            print line
            #TODO: arranjar uma string menos idiota
            if line.find("changeme") != -1 :
                target_file.write(content + '\n')
            else:
                target_file.write(line)
            line = base_file.readline()
        print ': )'
        base_file.close()
        target_file.close()
        
    def build_arg_string(self, args):
        str = ""
        #temp
        return ""
        str += "this._max_cost = {};".format(args['MAX_COST'])
        str += "this._cost_tile = {};".format(args['COST_TILE'])
	str += "this._cost_diagonal_tile = {};".format(args['COST_DIAGONAL'])
	str += "this._cost_turn = {};".format(args['COST_TURN'])
	str += "this._cost_slope = {};".format(args['COST_SLOPE'])
	str += "this._cost_bridge_per_tile = {};".format(args['COST_BRIDGE'])
	str += "this._cost_tunnel_per_tile = {};".format(args['COST_TUNNEL'])
	str += "this._cost_coast = {};".format(args['COST_COAST'])
	str += "this._cost_no_adj_rail = {};".format(args['COST_NO_ADJ_RAIL'])
	str += "this._cost_adj_obstacle = {};".format(args['COST_ADJ_OBST'])
	str += "this._max_bridge_length = {};".format(args['MAX_BRIDGE_LEN'])
        str += "this._max_tunnel_length = {};".format(args['MAX_TUNNEL_LEN'])
        return str
