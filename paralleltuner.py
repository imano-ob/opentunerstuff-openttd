
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
#import subprocess
import threading
#import argparser
import os

import ttdhandler
import aibuilder

class TTDTuner(MeasurementInterface):

    def __init__(self, *pargs, **kwargs):
        super(TTDTuner, self).__init__(*pargs, **kwargs)
        self.parallel_compile = True
#        self.handler = ttdhandler.TTDHandler()
#        self.handler.start()

#        self.builder = aibuilder.AIBuilder()
        
        #Might be useful in the future, who knows
        #It already has been
        self.dbglock = threading.Lock()
        self.idlock = threading.Lock()
        self.cur_id = 0
        
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
    
    def compile(self, cfg, result_id):
#        cfg = desired_result.configuration.data
        print "before -> ", threading.active_count()
        self.build_args_file(cfg, result_id)
        return 0
    
    def run_precompiled(self, desired_result, input, limit, compile_result,
                        result_id):
        self.idlock.acquire()
        cur_id = self.cur_id
        self.cur_id += 1
        self.idlock.release()
        print "after -> ", threading.active_count()
        arg_file_name = "args{}.py".format(result_id)
        results = self.call_program(["python2",
                                     "ttd_conn.py",
                                     arg_file_name,
                                     str(cur_id)])
        final_res = int(results['stdout'])
        return Result(time = -final_res)

    def run(self, desired_result, input, limit):
        pass
#        print "before -> ", threading.active_count()
#        
#        print "after -> ", threading.active_count()
        
        #ai_name = self.builder.build(cfg, result_id)
        #print('ai name ->' + ai_name)
        #self.handler.start_ai(ai_name, result_id)
        #res = self.handler.result(result_id)
        #self.builder.destroy(result_id)
        #return Result(time = -res)
    
    def save_final_config(self, configuration):
        self.handler.shutdown()
        self.manipulator().save_to_file(configuration.data,
                                        'ttd_final_config.json')

    def build_args_file(self, args, ai_id):
        arg_file_name = "args{}.py".format(ai_id)
        arg_file = open(arg_file_name, "w")
        arg_file.write("args = {\n")
        for k in args.keys():
            arg_file.write("    {}:{}\n".format(k, args[k]))
        arg_file.write("}\n")
        arg_file.close()
        
if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  args = argparser.parse_args()
  TTDTuner.main(args)
