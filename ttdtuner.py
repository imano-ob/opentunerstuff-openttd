
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

import ttdhandler
import aibuilder

class TTDTuner(MeasurementInterface):

    def __init__(self, *pargs, **kwargs):
        super(TTDTuner, self).__init__(*pargs, **kwargs)
        self.parallel_compile = True
        self.handler = ttdhandler.TTDHandler()
        self.handler.start()
#        time.sleep(3)

        self.builder = aibuilder.AIBuilder()
        
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
    
#    def compile(self, cfg, result_id):
#        self.handler.start_ai(self.ais[cfg['AI']], result_id)
#        return 0
    
#    def run_precompiled(self, desired_result, input, limit, compile_result,
#                        result_id):
#        res = self.handler.result(result_id)
#        return Result(time = -res)
        
    def run(self, desired_result, input, limit):
        self.idlock.acquire()
        result_id = self.cur_id
        self.cur_id += 1
        self.idlock.release()
        cfg = desired_result.configuration.data
        ai_name = self.builder.build(cfg, result_id)
        print('ai name ->' + ai_name)
        self.handler.start_ai(ai_name, result_id)
        res = self.handler.result(result_id)
        return Result(time = -res)
    
    def save_final_config(self, configuration):
        self.handler.shutdown()
        self.manipulator().save_to_file(configuration.data,
                                        'ttd_final_config.json')

    
if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  args = argparser.parse_args()
  TTDTuner.main(args)
