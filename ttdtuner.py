
import adddeps

import opentuner

from opentuner import MeasurementInterface
from opentuner import ConfigurationManipulator
from opentuner import IntegerParameter
from opentuner import Result

import time
#import subprocess
#import threading
#import argparser

import ttdtest

class TTDTest(MeasurementInterface):

    def __init__(self, *pargs, **kwargs):
        super(TTDTest, self).__init__(*pargs, **kwargs)
        self.parallel_compile = True
    
    def manipulator(self):
        manipulator = ConfigurationManipulator()
        manipulator.add_parameter(IntegerParameter('POINTLESS', 0, 100))
        self.handler = ttdtest.TTDHandler()
        self.handler.start()
        time.sleep(1)
        return manipulator

    def compile(self, cfg, od):
        print "aeho"
        self.handler.add_ai('derp')
        time.sleep(100)
        return 10
    
    def save_final_config(self, configuration):
        self.handler.shutdown()

    def run_precompiled(self, desired_result, input, limit, compile_result,
                        result_id):
        return Result(time = 10)
        
    def run(self, desired_result, input, limit):
 #       print "derasd"
        pass
        
if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  args = argparser.parse_args()
  TTDTest.main(args)
