#-------------------------------------------------------------------------------
# Name:        byteconverter.py
# Purpose:
#
# Author:      jlsafrit
#
# Created:     20/02/2014
# Copyright:   (c) jlsafrit 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from CRC16 import CRC16
import time
import struct

# seconds adjustment to make 1970 epoch to 1/1/2000 epoch
epoch_adj = 946702800

## See commands.h
cmd_desc = '''
#define CONDUIT_PACKET_COMMAND	0x0002
#define BEGIN_MODE			0x0004
#define SET_BAC_LEVELS		0x0007
#define GET_BAC_LEVELS		0x0008
#define SET_DRIVE_TIMES		0x0009
#define GET_DRIVE_TIMES		0x000A
#define SET_CALIBRATION		0x000B
#define GET_CALIBRATION		0x000C
#define SET_CONTACT			0x000D
#define GET_CONTACT			0x000E
#define END_PACKET			0x000F
#define DATA_PACKET			0x0010
#define POLL_REQUEST		0x0011
#define SET_DATE_TIME		0x0012
#define GET_DATE_TIME		0x0013
#define DATA_PACKET_10      0x0014
#define DATA_PACKET_30      0x0015
#define CLEAR_DATA			0x0016
#define CLEAR_ALL_DATA		0x0017
#define SET_RF_SERIAL		0x0019
#define GET_RF_SERIAL		0x001A
#define READ_SERIAL			0x001B
#define GET_SERIAL			0x001C
#define READ_ADC0			0x001D
#define GET_ADC0			0x001E
#define READ_ADC1			0x001F
#define GET_ADC1			0x0020
#define SET_IDLE_TIMES		0x0023
#define GET_IDLE_TIMES		0x0024
#define READ_BUILD			0x0025
#define GET_BUILD			0x0026
#define READ_TACH			0x0027
#define GET_TACH			0x0028
#define READ_THS			0x0029
#define GET_THS				0x002A
#define READ_ACCEL			0x002B
#define GET_ACCEL			0x002C
#define SET_SERVICE_TIMES	0x002D
#define GET_SERVICE_TIMES	0x002E
#define SET_PRESSURE_MIN	0x002F
#define GET_PRESSURE_MIN	0x0030
#define SET_SNIFFER_LEVEL	0x0031
#define GET_SNIFFER_LEVEL	0x0032
#define SET_PIN_TIMEOUT		0x0033
#define GET_PIN_TIMEOUT		0x0034
#define SET_TACH_IDLE		0x0035
#define GET_TACH_IDLE		0x0036
#define SET_MONITOR_LOCKOUT	0x0037
#define GET_MONITOR_LOCKOUT	0x0038
#define SET_TOGGLES         0x0039
#define GET_TOGGLES         0x003A
#define SET_PIN				0x003B
#define GET_PIN				0x003C
#define SET_MATE_SERIAL     0x003D
#define GET_MATE_SERIAL     0x003E
#define SET_LANGUAGE        0x003F
#define GET_LANGUAGE        0x0040
#define SET_RECALL_CAUSE    0x0041
#define GET_RECALL_CAUSE    0x0042
#define SET_MATING_FIRMWARE	0x0043
#define GET_MATING_FIRMWARE	0x0044
#define READ_BAC			0x0045
#define GET_BAC				0x0046
#define SET_GOOD_BEHAVIOR   0x0047
#define GET_GOOD_BEHAVIOR   0x0048
#define SET_TEST_CHARGE		0x0049
#define GET_TEST_CHARGE		0x004A
#define SET_FUELCELL_TYPE	0x004B
#define GET_FUELCELL_TYPE	0x004C
#define SET_MINIMUM_VOLUME	0x004D
#define GET_MINIMUM_VOLUME	0x004E
#define	SET_MVADJ			0x004F
#define	GET_MVADJ			0x0050
#define	SET_CAL_DATE		0x0051
#define	GET_CAL_DATE		0x0052
#define	SET_CIV_TIMEOUT		0x0053
#define	GET_CIV_TIMEOUT		0x0054
#define	SET_MON_TIME		0x0055
#define	GET_MON_TIME		0x0056
#define	READ_RECORD_COUNT	0x0057
#define	GET_RECORD_COUNT	0x0058
#define SET_IO				0x0059
#define GET_IO				0x005A
#define SET_SYRINGE			0x005B
#define GET_SYRINGE			0x005C
#define SET_AUDIO			0x005D
#define GET_AUDIO			0x005E
#define SET_AUDIO_VOLUME	0x005F
#define GET_AUDIO_VOLUME	0x0060
#define SET_FCTEMP_SETTING	0x0061
#define GET_FCTEMP_SETTING	0x0062
#define SET_PINLIST			0x0063
#define GET_PINLIST			0x0064
#define SET_SECRET			0x0065
#define GET_SECRET			0x0066
#define SET_FREESTART		0x0067
#define GET_FREESTART		0x0068
#define SET_FC_MAXDROP		0x0069
#define GET_FC_MAXDROP		0x006A
#define SET_RUN_TEST_REQUEST_TIME	0x006B
#define GET_RUN_TEST_REQUEST_TIME	0x006C
#define SET_JURISDICTION	0x006D
#define GET_JURISDICTION	0x006E
#define SET_STALL_PROTECT_TIME	0x006F
#define GET_STALL_PROTECT_TIME	0x0070
#define SET_VIOLATION_COUNT	0x0071
#define GET_VIOLATION_COUNT	0x0072
#define SET_VREF_CAL	0x0074
#define GET_VREF_CAL	0x0075   // retrieve current Vcar calibration factor (x5mV)
#define	CAL_VREF			0x0076  	// self-calibrate the VRef adjustment value
#define SET_VCAR_RUN_THRESHOLD	0x0077
#define GET_VCAR_RUN_THRESHOLD	0x0078 // for virtual tach - normall only set through config at factory
#define SET_WAKEUPS							0x0079
#define GET_WAKEUPS							0x007A // for programmable wakeup times - normally only configured via menu
#define SET_LOW_BATT_ADJUST					0x007B
#define GET_LOW_BATT_ADJUST					0x007C // adjustment for low battery thresholds (sleep states) (+/-1.75V)
#define DEBUG_EVENTS_CMD	0x0080 // THSG - for dumping event logs during debugging of event synching
#define DEBUG_EVENTS_CMD2	0x0081 // THSG - for dumping event logs during debugging of event synching
#define DEBUG_MSGBOX_CMD	0x0082 // THSG - for passing messsagebox-type strings to event sniffer app.
#define DEBUG_ADD_EVENT		0x0083 // THSG - to allow host to push and event into the event log, as if it had just occurred
#define SET_HUM_THRESHOLD						0x0091
#define GET_HUM_THRESHOLD						0x0092  // hum threshold, in tens {30..90}, nominal 60, for value of 600 (units?)
#define SET_HUMIDITY_THRESHOLD			0x0093
#define GET_HUMIDITY_THRESHOLD			0x0094  // humidity threshold, in percent {50..90}, nominal 70, for a value of 70%
#define READ_PRESTART_TEST_STATUS		0x0095  // dummy command - the way other get-only commands have been done
#define GET_PRESTART_TEST_STATUS		0x0096  // get state of prestart test - background will respond to this while in prestart mode
#define	SET_FLASH			0x00A0
#define	GET_FLASH			0x00A1
#define SET_HEATERS			0x00B0	// for test only: set new heater setpoints for BT,FC,AP
#define GET_HEATERS			0x00B1	// for test only: get current heater setpoints for BT,FC,AP
#define SET_TEST_IO			0x00B2	// for test only: accept virtual trigger/button presses
#define GET_TEST_IO			0x00B3	// for test only: get text of LCD screen and thermistor readings
#define READ_CHECKSUM_CALC	0x00F2
#define GET_CHECKSUM_CALC	0x00F3
'''

mode_desc = '''
SLEEP_MODE, // 1
WAKEUP_MODE, // 2
MENU_MODE, // 3
PRESTART_MODE, // 4
START_MODE, // 5
RUN_MODE, // 6
WARN_MODE, // 7
ALARM_MODE, // 8
CIVILIAN_TEST_MODE, // 9
SNIFFER_MODE, // 10
RUNNING_TEST_MODE, // 11
EMERGENCY_MODE, // 12
CALIBRATION_MODE, // 13
SERVICE_MODE, // 14
LOCKOUT_MODE, // 15
HOST_MODE, // 16
DEBUG_TEST_MODE, // 17
HIBERNATION_MODE, // 18
DESTINATION_MODE, // 19
INSTALL_MODE, // 20
FATAL_MODE, // 21
VOLUME_MODE, // 22
'''

testmode_desc = '''
TESTING_NOT, // 0
TESTING_WAIT_FOR_PIN, // 1
TESTING_WAIT_FOR_BLOW, // 2
TESTING_BLOWING, // 3
TESTING_ANALYZING, // 4
TESTING_PASSED, // 5
TESTING_FAILED, // 6
TESTING_WARNED, // 7
TESTING_ABORTED, // 8
TESTING_WARMING, // 9
TESTING_WARMED, // 10
TESTING_TIMEOUT // 11
'''
class CmdType(dict):
    def __init__(self):
        self.clear()
        for line in cmd_desc.split('\n'):
            parts = line.split()
            #print parts
            if len(parts) < 3:
                continue
            index = int(parts[2],16)
            desc = parts[1]
            self[index] = desc

class ModeType(dict):
    def __init__(self):
        self.clear()
        for line in mode_desc.split('\n'):
            parts = line.split()
            #print parts
            if len(parts) < 3:
                continue
            index = int(parts[2])
            desc = parts[0][:-1]
            self[index] = desc

class TestModeType(dict):
    def __init__(self):
        self.clear()
        for line in testmode_desc.split('\n'):
            parts = line.split()
            #print parts
            if len(parts) < 3:
                continue
            index = int(parts[2])
            desc = parts[0][:-1]
            self[index] = desc

# dictionary of all command types descriptions
# this is global to avoid creating multiple instances
CmdDesc = CmdType()
ModeDesc = ModeType()
TestModeDesc = TestModeType()

class Packet():
    def __init__(self,data=None):
        if data:
            self.parsePacket(data)
            if self.valid:
                self.parseCmd()
        else:
            self.valid = False

    def parsePacket(self,data):
        self.valid = False
        d = bytearray.fromhex(data)
        if len(d) >= 7:
            self.FullPacket = d
            self.SOH = d[0]
            #assert(self.SOH == 1)
            self.Length = d[1]*256 + d[2]
            self.Cmd = d[3]*256 + d[4]
            self.Payload = d[5:-2]
            self.CRC = d[-2]*256 + d[-1]
            self.ts = time.time()
            #assert(CRC16(d[:-2]) == self.CRC)

            if (self.SOH == 1) and (self.CRC == CRC16(d[:-2]) ):
                self.valid = True
        #self.LCD = '|'+str(d[11:23])+'|\n|'+str(d[23:-3])+'|'
        #print self.LCD

    def parseCmd(self):
        # assumes a valid packet was parsed with parsePacket
        PType = {
            2: self.parseConduit,
            69: self.parseBrAC,
            178: self.parseTestIO      }
        PType[self.Cmd]()

    def parseConduit(self):
        self.FW = int(str(self.Payload[0:2]).encode('hex'),16)
        self.Bitfields = str(self.Payload[2:4]).encode('hex')
        self.Mode = int(str(self.Payload[4:6]).encode('hex'),16)
        self.RTC = int(str(self.Payload[20:24]).encode('hex'),16) + epoch_adj
        #self.CPU_temp= int(str(self.Payload[35:37]).encode('hex'),16)
        # change to accept as a signed short & display properly
        self.CPU_temp= struct.unpack('>h',self.Payload[35:37])[0] / 100.0
        self.VCar = int(str(self.Payload[37:39]).encode('hex'),16)
        self.SN = str(self.Payload[41:47]).encode('hex')
        #print self.FW, self.Bitfields, self.Mode, self.RTC, self.SN, self.CPU_temp, self.VCar
        #print time.ctime(self.RTC)
        #print self.SN

    def parseBrAC(self):
        self.BrAC = int(str(self.Payload[0:1]).encode('hex'),16)

    def parseTestIO(self):
        # new for f/w build on 3/3/14
        self.BT_temp = struct.unpack('b',self.Payload[0:1])[0]
        self.AP_temp = struct.unpack('b',self.Payload[1:2])[0]
        self.FC_temp = struct.unpack('b',self.Payload[2:3])[0]
        #self.CP_temp = int(str(self.Payload[3:4]).encode('hex'),16)
        self.CP_temp = struct.unpack('b',self.Payload[3:4])[0]
        self.WF_temp = struct.unpack('b',self.Payload[4:5])[0]
        self.V_Car = int(str(self.Payload[5:6]).encode('hex'),16) / 10.0
        self.Test_Mode = int(str(self.Payload[6:7]).encode('hex'),16)
        self.LCD = str(self.Payload[7:])
        #print self.BT_temp,self.AP_temp,self.FC_temp,':'+self.LCD+':'

    def dump(self):
##        for property, value in vars(self).iteritems():
##            print property, ":", value
##        print vars(self)
##        return
##        if 'LCD' in vars(self).keys():
##            print 'LCD: ', self.LCD
##        if 'SN' in vars(self).keys():
##            print 'SN: ', self.SN
        #print ':'+str(self.FullPacket).encode('hex')+':'
        #print 'Length: %s' % str(self.Length)
        print 'Command: 0x%02x (%s)' % (self.Cmd, CmdDesc[self.Cmd] )
        #print 'Payload: %s' % str(self.Payload).encode('hex')
        #print 'CRC: 0x%x' % self.CRC
        #print 'Valid: %s' % self.valid
        self.dumpCmd()
        print '-' * 20

    def dumpCmd(self):
        # assumes a valid packet was parsed with parsePacket
        DType = {
            2: self.dumpConduit,
            69: self.dumpBrAC,
            178: self.dumpTestIO      }

        #print '=Fields specific to %s:' % CmdDesc[self.Cmd]
        DType[self.Cmd]()

    def dumpConduit(self):
        print 'FW version:',self.FW
        print 'Bitfields:',self.Bitfields
        print 'Mode: %d (%s)' % (self.Mode, ModeDesc[self.Mode])
        print 'RTC:', time.ctime(self.RTC)
        print 'CPU Temp:', self.CPU_temp
        print 'Car Voltage:', self.VCar
        print 'Serial Number:', self.SN

    def dumpBrAC(self):
        print 'Last BrAC:', self.BrAC

    def dumpTestIO(self):
        print 'BT  AP  FC  CP  WF  VCar'
        print '%02d  %02d  %02d  %02d  %02d  %f' % (
            self.BT_temp, self.AP_temp, self.FC_temp,
            self.CP_temp, self.WF_temp, self.V_Car )
        print 'Test Mode: %d (%s)' % (self.Test_Mode, TestModeDesc[self.Test_Mode])
        print 'LCD Text:'
        print '|' + self.LCD[:12] + '|'
        print '|' + self.LCD[12:] + '|'

def main():

    #LCD grab
    test ='01 00 21 00 B2 05 C4 03 DD 03 C0 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2A 20 20 20 20 20 20 20 87 58'
    #test='01002100b205da037e036b2020202020202020202020202020202020202020202020202076ba'
    packet = Packet(test)
    packet.dump()

    #conduit traffic
    test ='0100320002042ee0030001172c02101a98ca76918b000002661a98ca9c00000000000000000e04140af0000000000000151fc98f0039a4'
    packet = Packet(test)
    packet.dump()

    #BrAC reading
    test='01 00 04 00 45 00 00 EB D5'
    packet = Packet(test)
    packet.dump()


    #print ModeDesc


if __name__ == '__main__':
    main()
