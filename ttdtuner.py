
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

class TTDTuner(MeasurementInterface):

    def __init__(self, *pargs, **kwargs):
        super(TTDTuner, self).__init__(*pargs, **kwargs)
        self.parallel_compile = True
        self.handler = ttdhandler.TTDHandler()
        self.handler.start()
        time.sleep(3)

        #Might be useful in the future, who knows
        #It already has been
        self.dbglock = threading.Lock()
        
    def manipulator(self):
        manipulator = ConfigurationManipulator()
        
        manipulator.add_parameter(SwitchParameter('AI', 3))

        self.set_ais()
        
        return manipulator

    def set_ais(self):
        self.ais = ['AIAI', 'Convoy', 'CivilAI']
    
    def compile(self, cfg, result_id):
        self.handler.start_ai(self.ais[cfg['AI']], result_id)
        print "hurp {}".format(self.ais[cfg['AI']])
        return 0
    
    def run_precompiled(self, desired_result, input, limit, compile_result,
                        result_id):
        res = self.handler.result(result_id)
        print "hu3"
        return Result(time = -res)
        
    def run(self, desired_result, input, limit):
        pass

    def save_final_config(self, configuration):
        self.handler.shutdown()


    
if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  args = argparser.parse_args()
  TTDTuner.main(args)
