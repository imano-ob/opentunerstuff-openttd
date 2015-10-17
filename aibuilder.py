
# -*- coding: UTF-8 -*-

import shutil
import config
import os

class AIBuilder:
    def __init__(self, restype, years):
        self.base_dir = config.base_dir #./base_ai
        self.target_dir = config.target_dir #~/.openttd/ai
        #TODO: definir e/ou verificar coisas abaixo
        self.cost_file = 'pathfinder.nut' #base_directory/pathfinder.nut
        self.info_file = 'info.nut' #base_directory/info.nut
        self.main_file = 'main.nut' #base_directory/main.nut
        self.base_name = 'test_ai'
        self.restype = restype
        self.years = years

###########################################
# build
###########################################

    def build(self, args, ai_id):
        #Isso vai copiar inclusive coisas a serem reescritas depois
        #TODO: tratar erros
        ai_name = self.base_name + str(ai_id)
        target_dir = os.path.join(self.target_dir,ai_name)
        try:
            shutil.copytree(self.base_dir, target_dir)
        except OSError as e:
            #Error 17: arquivo já existe
            #Não vamos tratar caso seja outro erro
            if e.errno != 17:
                raise
            #TODO: arranjar alguma coisa pra resolver esse caso
            shutil.rmtree(target_dir)
            shutil.copytree(self.base_dir, target_dir)
        finally:

            #
            #Costs
            #
            
            arg_string = self.build_arg_string(args)
            replacement_dict = {'changeme': arg_string}
            self.substitute(target_dir, self.cost_file, replacement_dict)

            #
            #Info
            #
            
            aux = '	function GetName() {return "%s";}\n' % (ai_name)
            aux +=' function CreateInstance() {return "%s";} \n' % (ai_name)
            class_name = 'class %s extends AIInfo {' % (ai_name)
            register_line = 'RegisterAI(%s());' % (ai_name)
            replacement_dict = {'changeme': aux,
                                'tune-classname':class_name,
                                'tune-registerai':register_line}
            self.substitute(target_dir, self.info_file, replacement_dict)

            #
            #Main
            #

            if self.restype == 'money':
                func = 'AICompany.GetBankBalance(AICompany.COMPANY_SELF)'

            if self.restype == 'value':
                func = 'AICompany.GetQuarterlyCompanyValue(AICompany.COMPANY_SELF, AICompany.CURRENT_QUARTER)'

            if self.restype == 'profit':
                func = 'AICompany.GetQuarterlyIncome(AICompany.COMPANY_SELF, AICompany.CURRENT_QUARTER) - AICompany.GetQuarterlyExpenses(AICompany.COMPANY_SELF, AICompany.CURRENT_QUARTER)'


            out =  'AILog.Info("[tuner][" + ai_id + "][" + {} + "]");'.format(func)

            aux = 'AICompany.SetName("{}");\n'.format(ai_name)
            aux += 'local ai_id = {};\n'.format(ai_id)
            class_declaration = 'class %s extends AIController{' % (ai_name)
            years = "if (curDate - beginDate >= %s){" % (self.years * 365)
            
            replacement_dict = {'changeme': aux,
                                'tune-mainclassname':class_declaration,
                                'tuneryears':years,
                                'tuneroutput':out}
            self.substitute(target_dir, self.main_file, replacement_dict)
            return ai_name

###########################################
# destroy
###########################################        
        
    def destroy(self, ai_id):
        ai_name = self.base_name + str(ai_id)
        target_dir = os.path.join(self.target_dir,ai_name)
        shutil.rmtree(target_dir)

###########################################
# substitute
###########################################
        
    def substitute(self, target_dir, target_file, replacement_dict):
        base_path = os.path.join(self.base_dir, target_file)
        target_path = os.path.join(target_dir, target_file)
        base_file = open(base_path, 'r')
        target_file = open(target_path, 'w')
        line = base_file.readline()
        while line != '':
            #TODO: arranjar uma string menos idiota
            found = False
            for k in replacement_dict.keys():
                if k in line :
                    target_file.write(replacement_dict[k] + '\n')
                    found = True
            if not found:
                target_file.write(line)
            line = base_file.readline()
        base_file.close()
        target_file.close()

###########################################
# build arg string
###########################################
        
    def build_arg_string(self, args):
        str = ""
        str += "this._max_cost = {};\n".format(args['MAX_COST'])
        str += "this._cost_tile = {};\n".format(args['COST_TILE'])
	str += "this._cost_diagonal_tile = {};\n".format(args['COST_DIAGONAL'])
	str += "this._cost_turn = {};\n".format(args['COST_TURN'])
	str += "this._cost_slope = {};\n".format(args['COST_SLOPE'])
	str += "this._cost_bridge_per_tile = {};\n".format(args['COST_BRIDGE'])
	str += "this._cost_tunnel_per_tile = {};\n".format(args['COST_TUNNEL'])
	str += "this._cost_coast = {};\n".format(args['COST_COAST'])
	str += "this._cost_no_adj_rail = {};\n".format(args['COST_NO_ADJ_RAIL'])
	str += "this._cost_adj_obstacle = {};\n".format(args['COST_ADJ_OBST'])
	str += "this._max_bridge_length = {};\n".format(args['MAX_BRIDGE_LEN'])
        str += "this._max_tunnel_length = {};\n".format(args['MAX_TUNNEL_LEN'])
        return str
