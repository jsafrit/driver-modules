#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      jlsafrit
#
# Created:     21/04/2014
# Copyright:   (c) jlsafrit 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from bs4 import BeautifulSoup
import requests

class Chamber:
    """Chamber object:
    Holds all status regarding functions of the Temperature Chamber.

      params:
        ip  -   IP address of Temperature Chamber (defaults to 10.210.6.102)
    """
    def __init__(self, ip = None):

        if not ip:
            self.ip = '10.210.6.102'
        else:
            self.ip = ip

        self.url = 'http://' + self.ip + '/ezt.html'

        #get the page into bs4
        #populate the status fields
        self.refreshStats()

    def __str__(self):
        str = ''
        if self.TempPV:
            str += 'Current Temperature:\t %.1fC' % self.TempPV
        if self.TempSP:
            str += '\nTarget Temperature: \t %.1fC' % self.TempSP
        if self.HumidityPV:
            str += '\nCurrent Humidity:\t %.1f%%' % self.HumidityPV
        if self.HumiditySP:
            str += '\nTarget Humidity: \t %.1f%%' % self.HumiditySP
        if self.ProfileStatus:
            str += '\nProfile Status: \t ' + self.ProfileStatus
        if self.CurrentStep:
            str += '\nProfile Step:   \t ' + self.CurrentStep
        if self.TimeLeft:
            str += '\nProfile Time Left: \t ' + self.TimeLeft

        if not len(str):
            str = 'No Status Available'

        return str

    def parseTd(self, tag):
        """Return float type value from tag with 'PV = value' format."""
        return float(tag.string.strip().split('=')[1])

    def populateFields(self):
        """Update all chamber fields from webpage."""
        td_l = self.soup('td')
##        ilist=range(32)
##        for i in ilist:
##            print i,td_l[i].string.strip()
        if td_l:
            self.TempPV = self.parseTd(td_l[1])
            self.TempSP = self.parseTd(td_l[2])
            self.HumidityPV = self.parseTd(td_l[5])
            self.HumiditySP = self.parseTd(td_l[6])
            self.ProfileStatus = td_l[13].string.strip()
            self.CurrentStep = td_l[19].string.strip()
            self.TimeLeft = td_l[21].string.strip()
        else:
            self.TempPV = None
            self.TempSP = None
            self.HumidityPV = None
            self.HumiditySP = None
            self.ProfileStatus = None
            self.CurrentStep = None
            self.TimeLeft = None

    def refreshStats(self):
        """Refresh chamber status from internal webserver."""
        r  = requests.get(self.url)
        data = r.text
        #get the page into bs4 and repop fields
        self.soup = BeautifulSoup(data)
        self.populateFields()


def main():
    cs2 = Chamber()
    print cs2

    for i in range(3):
        print '-' * 40
        cs2.refreshStats()
        print 'Current Temperature:\t', cs2.TempPV
        print 'Current Humidity:\t', cs2.HumidityPV

if __name__ == '__main__':
    main()
