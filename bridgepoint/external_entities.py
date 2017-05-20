import datetime
import sys


class LOG(object):
    
    @staticmethod
    def LogInteger(message):
        print('LogInteger: %d' % message)
        
    @staticmethod
    def LogInfo(message):
        print('LogInfo: %s' % message)
        
    @staticmethod
    def LogFailure(message):
        print('LogFailure: %s' % message)
        
    @staticmethod
    def LogSuccess(message):
        print('LogSuccess: %s' % message)
        

class TIM(object):
    
    @staticmethod
    def create_date(day, hour, minute, month, second, year):
        return datetime.datetime(year, month, day, hour, minute, second)
    
    @staticmethod
    def get_day(date):
        return date.day
    
    @staticmethod
    def get_month(date):
        return date.month
    
    @staticmethod
    def get_hour(date):
        return date.hour

    
class ARCH(object):
    
    @staticmethod
    def shutdown():
        sys.exit()
        

class PERSIST(object):
    
    @staticmethod
    def commit():
        return 0
    

class NVS(object):
    
    @staticmethod
    def format():
        return 0
    
    @staticmethod
    def version(first, second):
        return 0
    
    @staticmethod
    def checksum(first, second):
        return 0
        
