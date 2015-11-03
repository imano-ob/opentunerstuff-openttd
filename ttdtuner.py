
# -*- coding: UTF-8 -*-

import adddeps

import opentuner

from opentuner import MeasurementInterface
from opentuner import ConfigurationManipulator
from opentuner import IntegerParameter
from opentuner import SwitchParameter
from opentuner import Result

import time
import random
import threading
#import argparse
import os

import ttdhandler
import aibuilder

class TTDTuner(MeasurementInterface):

    def __init__(self, *pargs, **kwargs):
        super(TTDTuner, self).__init__(*pargs, **kwargs)

        restype = args.restype
        years = args.years
        self.number_ais = args.numberais
        
        self.parallel_compile = True
        self.handler = ttdhandler.TTDHandler(self.number_ais)
        self.handler.start()

        
        self.builder = aibuilder.AIBuilder(restype, years)
        
        #Might be useful in the future, who knows
        #It already has been
        self.dbglock = threading.Lock()
        self.idlock = threading.Lock()
        self.cur_id = 0

        i = 0
        logname = "logtuner{}.log".format(i) 
        while os.path.exists(logname):
            i += 1
            logname = "logtuner{}.log".format(i) 
        self.logfile = open(logname, "w")


##############################################
# manipulator
##############################################
        
    def manipulator(self):
        manipulator = ConfigurationManipulator()

        manipulator.add_parameter(IntegerParameter('MAX_COST',
                                                   5000000,
                                                   20000000))
        manipulator.add_parameter(IntegerParameter('COST_TILE',
                                                   50,
                                                   200))
        manipulator.add_parameter(IntegerParameter('COST_DIAGONAL',
                                                   35,
                                                   140))
        manipulator.add_parameter(IntegerParameter('COST_TURN',
                                                   25,
                                                   100))
        manipulator.add_parameter(IntegerParameter('COST_TURN',
                                                   25,
                                                   100))
        manipulator.add_parameter(IntegerParameter('COST_SLOPE',
                                                   50,
                                                   200))
        manipulator.add_parameter(IntegerParameter('COST_BRIDGE',
                                                   75,
                                                   300))
        manipulator.add_parameter(IntegerParameter('COST_TUNNEL',
                                                   60,
                                                   240))
        manipulator.add_parameter(IntegerParameter('COST_COAST',
                                                   10,
                                                   40))
        manipulator.add_parameter(IntegerParameter('COST_NO_ADJ_RAIL',
                                                   0,
                                                   100))
        manipulator.add_parameter(IntegerParameter('COST_ADJ_OBST',
                                                   0,
                                                   100))
        manipulator.add_parameter(IntegerParameter('MAX_BRIDGE_LEN',
                                                   3,
                                                   20))
        manipulator.add_parameter(IntegerParameter('MAX_TUNNEL_LEN',
                                                   3,
                                                   20))
       
        return manipulator

#TODO: gerar nome de AI para ser unico de acordo com cfg e usar compile?
#ou não vale o esforço?
    
#    def compile(self, cfg, result_id):
#        self.handler.start_ai(self.ais[cfg['AI']], result_id)
#        return 0
    
#    def run_precompiled(self, desired_result, input, limit, compile_result,
#                        result_id):
#        res = self.handler.result(result_id)
#        return Result(time = -res)

##############################################
# run
##############################################


    def run(self, desired_result, input, limit = 10800):
        self.idlock.acquire()
        result_id = self.cur_id
        self.cur_id += 1
        self.idlock.release()
        print('run: resetting server')
        self.handler.reset_server()
        cfg = desired_result.configuration.data
        ai_name = self.builder.build(cfg, result_id)
        print('ai name ->' + ai_name)
        self.handler.start_ai(ai_name, result_id, self.number_ais)
        res = self.handler.result(result_id)
        mean = float(sum(res))/len(res)
        self.builder.destroy(result_id)
        logstr = "id = {}, result = {}".format(result_id, mean)
        for k in cfg.keys():
            logstr += ", {} = {}".format(k, cfg[k])
        logstr += "\n"
        self.logfile.write(logstr)
        return Result(time = -mean)

##############################################
# save final config
##############################################

    def save_final_config(self, configuration):
        self.handler.shutdown()
        self.logfile.close()
        self.manipulator().save_to_file(configuration.data,
                                        'ttd_final_config.json')

    
if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  argparser.add_argument("--res-type",
                         dest = 'restype',
                         choices = ['money', 'value', 'profit'],
                         default = 'value')
  argparser.add_argument("--years",
                         type = int,
                         default = 10)
  argparser.add_argument("--number-ais",
                         dest='numberais',
                         default = 1,
                         type = int,
                         choices = range(1, 14))
  args = argparser.parse_args()
  TTDTuner.main(args)
