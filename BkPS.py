#-------------------------------------------------------------------------------
# Name:        BkPS.py
# Purpose:     General interface to control the BK Precision PS via serial
#
# Author:      jlsafrit
#
# Created:     23/04/2014
# Copyright:   (c) jlsafrit 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import serial
import time
import sys

class BkPS:
    """BK Precision PS object:
    General interface for the power supply.

      params:
        comm  -   Comm Port of the power supply (i.e. 'COM8')
    """
    def __init__(self, comm):
        self.comm = comm
        self.baud = 9600
        self.timeout = 1
        self.isOpen = False
        self.ser = None
        self.open()

    def __str__(self):
        str = 'Comm Port is %s. ' % self.comm
        str += 'Device is '
        if self.isOpen:
            str += 'open.\n'
        else:
            str += 'closed.\n'
        return str

    def open(self):
        try:
            self.ser=serial.Serial(self.comm, self.baud, timeout=self.timeout)
        except serial.serialutil.SerialException:
            print 'BOOM! @ %s' % self.comm
            #raise serial.serialutil.SerialException
        if not self.ser or not self.ser.isOpen():
            print "Problem opening port. Exiting..."
            sys.exit(3)
        else:
            self.isOpen=True

    def close(self):
        self.ser.close()
        if self.ser.isOpen():
            print "Problem closing port. Exiting..."
            sys.exit(3)
        self.isOpen = False

    def sendCmd(self, cmd):
        if not self.isOpen:
            print "Serial port not open. Exiting..."
            sys.exit(3)

        cmd = cmd + '\r\n'
        self.ser.write(cmd)
        time.sleep(.5)
        result = self.ser.read(3)
        if 'OK' not in result:
            print "Problem with command. Exiting..."
            sys.exit(3)

    def sendCmdResp(self, cmd, ln=10):
        if not self.isOpen:
            print "Serial port not open. Exiting..."
            sys.exit(3)

        cmd = cmd + '\r\n'
        self.ser.write(cmd)
        time.sleep(.5)
        resp = self.ser.read(ln)
        result = self.ser.read(3)
        if 'OK' not in result:
            print "Problem with command. Exiting..."
            sys.exit(3)
        return resp

    def off(self):
        """Turn power supply output off."""
        self.sendCmd('SOUT1')

    def on(self):
        """Turn power supply output on."""
        self.sendCmd('SOUT0')

    def setV(self,v):
        """Set the power supply voltage.

          params: v -   voltage in range of 0..16 inclusive
                        truncated to 1 decimal place.
        """
        if v<0 or v>16:
            print "Voltage out of range."
            return
        v = int(v * 10.0)
        v = str(v)
        while len(v)<3:
            v = '0'+v
        assert(len(str(v))==3)
        cmd = 'VOLT' + str(v)
        self.sendCmd(cmd)

    def setC(self,c):
        """Set the power supply current.

          params: c -   current in range of 0..5 inclusive
                        truncated to 1 decimal place.
        """
        if c<0 or c>5:
            print "Current out of range."
            return
        c = int(c * 10.0)
        c = str(c)
        while len(c)<3:
            c = '0'+c
        assert(len(str(c))==3)
        cmd = 'CURR' + str(c)
        self.sendCmd(cmd)

    def getAll(self):
        """Returns actual voltage, current, and mode
        as a tuple (v, c, mode)
        """
        resp = self.sendCmdResp('GETD',10)
        voltage = int(resp[:4]) / 100.0
        current = int(resp[4:8]) / 100.0
        mode = int(resp[8:9])
        if mode == 1:
            mode = 'CC'
        else:
            mode = 'CV'
        return (voltage, current, mode)


    def updateStatus(self):
        """Gets actual P/S conditions and prints to screen"""
        resp = self.getAll()
        print 'Current state:'
        print ' Voltage:   ', resp[0]
        print ' Current:   ', resp[1]
        print ' Mode:      ', resp[2]

def main():
    comm = raw_input('Please enter connected PS comm port (i.e. COM4): ')
    ps = BkPS(comm)
    ps.off()
    time.sleep(5)

    print 'Setting Voltage to 3.3V'
    ps.setV(3.3)
    ps.on()
    time.sleep(5)
    ps.off()

    print 'Setting Current to 1.2A'
    ps.setC(1.2)
    ps.on()
    time.sleep(5)
    ps.off()

    print 'Setting Voltage to 12V'
    ps.setV(12)
    ps.on()
    time.sleep(5)
    ps.off()

    print 'Getting Status'
    ps.updateStatus()

    print 'Setting Voltage to 20V'
    ps.setV(20)
    ps.on()
    time.sleep(5)
    ps.off()



if __name__ == '__main__':
    main()
