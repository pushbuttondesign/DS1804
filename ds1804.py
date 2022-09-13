"""
Control of DS1804-XXX+ digital potentiometers
for adafruit circuitpython prototyping boards
"""

#TODO
#   - test new save timings
#   - test with ds1804 chips other than -100+ (-050+ and -010+), do # of steps change?

import sys
if 'board' not in sys.modules:
    import board
if 'digitalio' not in sys.modules:
    import digitalio
if 'time' not in sys.modules:
    import time
if 'gc' not in sys.modules:
    import gc

class potentiometer:
    def __init__(self, max_kohm, inc, ud, cs, curr_kohm=None, vin=3.3):
        time.sleep(0.0005) #initial startup time to load eeprom
        if(max_kohm != 10 and max_kohm != 50 and max_kohm != 100):
            raise ValueError("Only DS1804-XXX+ variants 010, 050, 100 are valid")
        self.max_kohm = max_kohm
        self.step_number = 100
        self.step_size = round(self.max_kohm / self.step_number)
        self.curr_kohm = curr_kohm
        self.vin = vin
        #setup pins
        self.cs = digitalio.DigitalInOut(cs)
        self.inc = digitalio.DigitalInOut(inc)
        self.ud = digitalio.DigitalInOut(ud)
        self.cs.direction = digitalio.Direction.OUTPUT
        self.inc.direction = digitalio.Direction.OUTPUT
        self.ud.direction = digitalio.Direction.OUTPUT
        #set default values
        self.cs.value = True #when high INC and UD will do nothing
        self.inc.value = True #high to low transition steps tap one place
        self.ud.value = True #when high INC pulse steps up
        #initalise a known value
        if curr_kohm is None:
            #step up to max resistance
            for i in range(0,self.step_number):
                self.step(True)
            self.curr_kohm = max_kohm
        else:
            self.curr_kohm = curr_kohm
    def step(self, direction):
        """
        FUNCTION DESCRIPTION
        steps the wiper one step in given direction
        INPUTS
        direction, bool, True is up, False is down
        """
        self.ud.value = direction #set direction
        self.cs.value = False #activate operating mode
        time.sleep(0.001) #tci 50ns
        self.inc.value = False #step
        time.sleep(0.001) #til 50ns
        self.cs.value = True #deactivate operating mode without saving
        self.inc.value = True #reset to default value
        time.sleep(0.001) #pause to avoid skipping steps

        #update position if known, stop at boundrys
        if self.curr_kohm is not None:
            if direction == True and self.curr_kohm < self.max_kohm:
                self.curr_kohm += 1
            if direction == False and self.curr_kohm > 0:
                self.curr_kohm -= 1
    def set(self, new_kohm):
        """
        FUNCTION DESCRIPTION
        caculates difference in kohm value between new and old position
        moves wiper by caculated steps and direction
        INPUTS
        new_kohm, int, the desired resistance between min and max
        """
        if new_kohm > self.max_kohm or new_kohm < 0:
            raise ValueError("out of range resistance requested")

        #caculate steps between old and new kohm and direction
        if self.curr_kohm > new_kohm:
            direction = False
            diff = round((self.curr_kohm - new_kohm) / self.step_size)
        elif self.curr_kohm <= new_kohm:
            direction = True
            diff = round((new_kohm - self.curr_kohm) / self.step_size)

        #step difference
        for i in range(0,diff):
            self.step(direction)
            gc.collect()

        del diff
        gc.collect()
    def save(new_kohm):
        '''
        FUNCTION DESCRIPTION
        saves the wiper position in nonvolatile wiper storage
        INPUTS
        kohm, int, desired kohm value
        '''
        if new_kohm > self.max_kohm or new_kohm < 0:
            raise ValueError("out of range resistance requested")

        #step to top
        direction = True
        for i in range(0,self.step_number):
            step(direction)
            gc.collect()

        #decrease to desired value
        direction = False
        for i in range(0,round((self.max_kohm - new_kohm) / self.step_size)):
            step(direction)
            gc.collect

        print("set to {} kohm".format(self.curr_kohm))
        volts = (self.vin * self.curr_kohm) / (100 + self.curr_kohm)
        print("voltmeter should now read {} v".format(volts))
        del(volts)
        gc.collect()
        print("waiting for 5 seconds...")
        time.sleep(5)

        self.cs.value = False
        time.sleep(0.000000550) #tic 500ns
        self.cs.value = True
        time.sleep(0.01) #twst 10ms

        #save wiper position in EEPROM
        print("saved {} kohm value in EEPROM".format(self.curr_kohm))
        self.cs.value = False #reset default

        #this old code worked, some timing changes above not yet tested
        '''
        #step to bottom
        direction = False
        for i in range(0,110):
            print("step count {} in direction {}".format(i, "UP" if direction == True else "DOWN"))
            step(direction)

        #incease to desired value
        direction = True
        kohm_per_tap = 2
        kohm = 40
        for i in range(0,kohm/kohm_per_tap):
            print("step count {} in direction {}".format(i, "UP" if direction == True else "DOWN"))
            step(direction)

        time.sleep(200000)
        '''
    def test(self):
        """
        FUNCTION DESCRIPTION
        manipulates pot resistance while printing corrosponding voltmeter value
        assumes voltmeter across W5 / L6 with 100kohm potential devider resistor above
        between 3.3v and gnd
        """
        #check initilised value
        print()
        print("IF POWER TO WAS NOT JUST CYCLED OFF/ON, THIS MAY NOT BE EEPROM SAVED VALUE")
        print("{} kohm is initalised value".format(self.curr_kohm))
        volts = (self.vin * self.curr_kohm) / (100 + self.curr_kohm)
        print("voltmeter should now read {} v".format(volts))
        del(volts)
        gc.collect()
        print("waiting for 5 seconds...")
        print()
        time.sleep(5)

        #step down and up
        direction = False #down
        for i in range(0,self.step_number):
            #print("step count {} in direction {}".format(i, "UP" if direction == True else "DOWN"))
            self.step(direction)
            gc.collect()
        print("stepped to bottom")
        volts = (self.vin * self.curr_kohm) / (100 + self.curr_kohm)
        print("voltmeter should now read {} v".format(volts))
        del(volts)
        gc.collect()
        print("waiting for 5 seconds...")
        print()
        time.sleep(5)
        direction = True #up
        for i in range(0,self.step_number):
            #print("step count {} in direction {}".format(i, "UP" if direction == True else "DOWN"))
            self.step(direction)
            gc.collect()
        print("stepped to top")
        volts = (self.vin * self.curr_kohm) / (100 + self.curr_kohm)
        print("voltmeter should now read {} v".format(volts))
        del(volts)
        gc.collect()
        print("waiting for 5 seconds...")
        print()
        time.sleep(5)

        #set min, mid, max values
        self.set(0)
        gc.collect()
        print('set to {} kohm'.format(self.curr_kohm))
        volts = (self.vin * self.curr_kohm) / (100 + self.curr_kohm)
        print("voltmeter should now read {} v".format(volts))
        del(volts)
        gc.collect()
        print("waiting for 5 seconds...")
        print()
        time.sleep(5)

        self.set(round(self.max_kohm / 2))
        gc.collect()
        print('set to {} kohm'.format(self.curr_kohm))
        gc.collect()
        volts = (self.vin * self.curr_kohm) / (100 + self.curr_kohm)
        print("voltmeter should now read {} v".format(volts))
        del(volts)
        gc.collect()
        print("waiting for 5 seconds...")
        print()
        time.sleep(5)

        self.set(self.max_kohm)
        gc.collect()
        print("set to {} kohm".format(self.curr_kohm))
        volts = (self.vin * self.curr_kohm) / (100 + self.curr_kohm)
        print("voltmeter should now read {} v".format(volts))
        del(volts)
        gc.collect()
        print("waiting for 5 seconds...")
        print()
        time.sleep(5)
