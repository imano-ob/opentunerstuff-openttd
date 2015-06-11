
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

    def manipulator(self):
        manipulator = ConfigurationManipulator()
        manipulator.add_parameter(IntegerParameter('POINTLESS', 0, 100))
        self.handler = ttdtest.TTDHandler()
        self.handler.start()
        time.sleep(1)
        return manipulator

    def run(self, desired_result, input, limit):
        print "aeho"
        self.handler.add_ai('derp')
        time.sleep(100)
        res = Result(time = 10)
        return res
    
    def save_final_config(self, configuration):
        self.handler.shutdown()

if __name__ == '__main__':
  argparser = opentuner.default_argparser()
  TTDTest.main(argparser.parse_args())
