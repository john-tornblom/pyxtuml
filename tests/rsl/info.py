# encoding: utf-8
# Copyright (C) 2014 John Törnblom

from tests.rsl.utils import RSLTestCase
from tests.rsl.utils import evaluate

import datetime
import os

import xtuml.version

class TestInfo(RSLTestCase):

    @evaluate
    def testDate(self, rc):
        '.exit "${info.date}"'
        now = datetime.datetime.now()
        now = datetime.datetime.ctime(now)
        now = str(now)
        self.assertEqual(now, rc)

    @evaluate
    def testUserId(self, rc):
        '.exit "${info.user_id}"'
        self.assertEqual(os.getlogin(), rc)

    @evaluate
    def testUUID(self, rc):
        '.exit "${info.unique_num}"'
        self.assertEqual("1", rc)
        
    @evaluate
    def testArchFileName(self, rc):
        '.exit "${info.arch_file_name}"'
        self.assertEqual("tests.rsl.info.testArchFileName", rc)
        
    @evaluate
    def testArchFileLine(self, rc):
        '''
        .// No comment
        .exit "${info.arch_file_line}"
        '''
        self.assertEqual("3", rc)

    @evaluate
    def testVersion(self, rc):
        '.exit "${info.interpreter_version}"'
        self.assertEqual(xtuml.version.complete_string, rc)

    @evaluate
    def testPlatform(self, rc):
        '.exit "${info.interpreter_platform}"'
        self.assertEqual(os.name, rc)
        


