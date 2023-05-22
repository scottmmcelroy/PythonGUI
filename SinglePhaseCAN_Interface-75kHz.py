from tkinter import *
from tkinter import ttk
import sys
import os
import tempfile
import datetime
import threading
import time
import can
from can.interface import Bus

# Add default PATHS for interfaces (not permanent and only temp during program run)
os.environ['PATH'] =  r"C:\Program Files (x86)\National Instruments\RT Images\NI-CAN" + os.pathsep + os.environ['PATH'] # nican
#print (os.environ['PATH'])

import can.interfaces.nican

interfaceTextsList = "NI-CAN"
interfaceNamesList = "nican"
interfaceChannelsList = "CAN1"
interfaceBitRatesList = 1000000
canState = False
sendApproved = False

##############
##Functions###
##############

def sendCAN():
    
    #setting up the packets
    #need to format the input for this transmission
    FSBin = '{0:008b}'.format(int(float(fsw.get())/1000))
    #print(f"FSBin: {FSBin}")
    DutyBin = '{0:010b}'.format(int(duty.get())) #duty cycle, duty cycle is integer only 0-100
    #print(f"DutyBin: {DutyBin}")
    TDBin = '{0:012b}'.format(0) #Dont care value at the reference design
    #print(f"TDBin: {TDBin}")
    FFBin = '{0:010b}'.format(0) #Dont care value at the reference design
    #print(f"FFBin: {FFBin}")
    if psen.get() == 'On':
        PD1Bin = '1'
    else:
        PD1Bin = '0'
    #print(f"PD1Bin: {PD1Bin}")
    PD2Bin = '0' #Dont care value at the reference design
    #print(f"PD2Bin: {PD2Bin}")
    PD3Bin = '0' #Dont care value at the reference design
    #print(f"PD3Bin: {PD3Bin}")
    if len.get() == 'On':
        LE1Bin = '1'    
    else:
        LE1Bin = '0'
    #print(f"LE1Bin: {LE1Bin}")
    LE2Bin = '0' #Dont care value at the reference design
    LE3Bin = '0' #Dont care value at the reference design
    R1Bin = '0' #reset value
    F1Bin = '0' #fault value
    F2Bin = '0' #Dont care value at the reference design
    F3Bin = '0' #Dont care value at the reference design
    
    #setup the full packet
    s = FSBin+DutyBin+TDBin+FFBin+'0'+PD1Bin+PD2Bin+PD3Bin+'0'+LE1Bin+LE2Bin+LE3Bin+R1Bin+F1Bin+F2Bin+F3Bin+'000000000000'
    t = "%016x" % (int(s,2))
    u = bytearray.fromhex(t)
    #print(s)
    #print(t)
    #print(u)
    
    msg = can.Message(data=u, is_extended_id=False)
    print(msg)
    
    #add the CAN message to the transaction window
    addText(str(msg))
    
    try:    
        print(bus1.send(msg))
        print(f"Message sent on {bus1.channel_info}")
    except:
        print("Message Not Sent")

#bus connection function
def busConnect():
    global bus1
    global canState
    #load the interface for NICAN (might be neousys)
    bustype = interfaceNamesList
    channel = interfaceChannelsList
    bitrate = int(interfaceBitRatesList)

    if canState == False:
        try:
            bus1 = can.Bus(bustype=bustype,channel=channel,bitrate=bitrate)
        except:
            print("Connection Issue. Please check the port config.")
            addText("**CAN Bus Connection Issue: Check port settings!**")
            canState = False
        else:
            addText("**CAN Bus Connected**")
            canState = True
    elif canState == True:
        try:
            bus1.shutdown()
        except:
            addText("**CAN Bus connection could not be terminated!**")
        else:
            addText("**CAN Bus connection is terminated!**")
            canState = False    

def addText(string):
    textBox.config(state='normal')  
    textBox.insert(INSERT,string)
    textBox.insert(INSERT, "\n")
    textBox.config(state='disabled')  
    textBox.see("end")    

def buttonPress():
    #print("Fsw value: ", fsw.get())
    #print("Duty Cycle value: ", duty.get())
    #print("PSEN: ", psen.get())
    #print("LEN", len.get())

    #########
    #Check for valid number in the Fsw box
    if fsw.get() == "":
        addText("**Please input a switching frequency!**")
        sendApproved = False
    elif int(float(fsw.get())) >= 0 and 75000 >= int(float(fsw.get())):
        #put into a valid variable for passing to a function
        addText("Fsw is: " + fsw.get() + "Hz")
        sendApproved = True
        #################ADD FUNCTION FOR STORING VARIABLE to USE FOR CAN send
    else:
        addText("**Please input a VALID switching frequency between between 0-75kHz!**")
        sendApproved = False
    #######    

    #########
    #Check for valid number in the Duty Cycle box
    if duty.get() == "":
        addText("**Please input a duty cycle!**")
        sendApproved = False
    elif int(float(duty.get())) >= 0 and 100 >= int(float(duty.get())):
        #put into a valid variable for passing to a function
        addText("Duty Cycle is: " + duty.get() + "%")
        sendApproved = True
        #################ADD FUNCTION FOR STORING VARIABLE to USE FOR CAN send
    else:
        addText("**Please input a VALID valid duty cylce between between 0-100%!**")
        sendApproved = False
    #######    

    #######
    if psen.get() == 'On':
        psenState_label.config(text='PSEN On')
        addText("PSEN On - Gate Driver Power Supply Enabled")
    elif psen.get() == 'Off':
        psenState_label.config(text='PSEN Off')
        addText("PSEN Off - Gate Driver Power Supply Disabled")
    #######

    #######
    if len.get() == 'On':
        lenState_label.config(text='LEN On')
        #fault_label.config(text='Fault', foreground='red')
        addText("LEN On - PWM Logic Enabled")
    elif len.get() == 'Off':
        lenState_label.config(text='LEN Off')
        #fault_label.config(text='No Fault', foreground='green')
        addText("LEN Off - PWM Logic Disabled")
    #######

    #######
    if sendApproved == True:
        if canState == True:
            sendCAN()
            addText("***CAN message sent!***")
        else:
            addText("***CAN Bus not connected!***")
    else:
        addText("***Please check errors before sending CAN messages!***")
    #######

def busThread():
    #global bus1
    global msgVoltage, msgTemperature, msgCurrent
    #print("***Thread is running!***")
    #eliminate old message out of the buffer
    try:
        msgOld = bus1.recv()
    except:
        #print("***No old messages!***")    
        pass
    #run the while loop to receive new messages
    while True:
        if canState == True:
            try:
                newMsg = bus1.recv()
                print(newMsg)
                #decode the type of message so the GUI can be updated
                if newMsg.arbitration_id == 0: #control communication message
                    pass
                    #print("Control Message Received")
                elif newMsg.arbitration_id == 255: #temperature feedback
                    #print("Temperature Message Received")
                    msgTemperature = newMsg
                elif newMsg.arbitration_id == 254: #current feedback
                    #print("Current Message Received")
                    msgCurrent = newMsg
                elif newMsg.arbitration_id == 253: #voltage feedback
                    #print("Voltage Message Received")
                    msgVoltage = newMsg
                #update the values in the GUI  
                updateMeasurements(msgVoltage, msgCurrent, msgTemperature)      
            except:
                pass

def updateMeasurements(msgV, msgI, msgT):

    #voltage
    v = ''.join('{:02x}'.format(x) for x in msgV.data)
    voltages = bin(int(v, 16))[2:].zfill(64)
    voltageA = twoscomplement(int(voltages[0:16],2),16)
    #print(f"voltageA: {voltageA}")
    phaseAVoltageReading_label.config(text=str(voltageA))
    #print(f"PhaseA Voltage Value: {voltageA}")
    voltageDC = twoscomplement(int(voltages[48:64],2),16)
    dclReading_label.config(text=str(voltageDC))
    #print(f"DC Link Voltage Value: {voltageDC}")
    
    #get the values from the incoming messages
    #temperature
    t = ''.join('{:02x}'.format(x) for x in msgT.data)
    temperatures = bin(int(t, 16))[2:].zfill(64)
    tempA = (int(temperatures[0:16],2)-273)
    phaseATemperatureReading_label.config(text=str(tempA))
    #print(f"Temp Value: {tempA}")

    #current
    c = ''.join('{:02x}'.format(x) for x in msgI.data)
    currents = bin(int(c, 16))[2:].zfill(64)
    currentA = twoscomplement(int(currents[0:16],2),16)
    phaseACurrentReading_label.config(text=str(currentA))
    #print(f"Current Value: {currentA}")

def twoscomplement(number, length):
    if(number & (1<<(length-1))) != 0:
        number = number - (1 <<length)
    return number
#############
####Start of the actual program
##############
####entry point for the code
if __name__ == '__main__':
####Main Start######
    root = Tk() #creates a window
    #windows specs/setup
    root.config(background='black')
    root.geometry('800x500')
    root.title("XM3 Reference Design CAN Interface")
    root.iconbitmap(r'C:\\Users\\smcelroy\\Pictures\\WOLF_for_ICON_larger.ico')
    #do not allow window size to change
    root.resizable(False, False)
    style = ttk.Style()
    style.theme_use('alt')
    
    #input storage Values
    fsw = StringVar() #variable for Fsw entry
    duty = StringVar() #variable for duty cycle
    psen = StringVar()
    len = StringVar()
    #output storage values
    DCLinkVoltage = StringVar()
    PhaseCurrent = StringVar()
    PhaseVoltage = StringVar()
    PhaseTemperature = StringVar()
    #start adding labels, entries, and buttons into a grid
    #reference Wolfspeed Color is Amathest Purple RGB Hex='#582C83'
    
    #############
    #Row 0, Title
    title_label = ttk.Label(root, text="XM3 Ref Design - Single Phase Operation", foreground='#582C83', background="black", font=('San Serif Pro', 22, 'bold italic underline'))
    title_label.grid(row=0,column=0, columnspan=3, padx=50)
    title_label.config(compound=RIGHT)
    
    #############
    #Row 1, Switching Frequency
    fsw_label = ttk.Label(root, text="Switching Frequency", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    fsw_label.grid(row=1,column=0, padx=0)
    
    fsw_entry = ttk.Entry(root, textvariable=fsw, font=('San Serif Pro', 16, 'italic'), justify=CENTER)
    fsw_entry.config(width=15)
    fsw_entry.grid(row=1, column=1)
    
    hz_label = ttk.Label(root, text="Hz", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    hz_label.grid(row=1,column=2)

    note_label = ttk.Label(root, text="(0-75kHz)", foreground='white', background="black", font=('San Serif Pro', 12))
    note_label.grid(row=1,column=3)

    ############
    #Row 2
    duty_label = ttk.Label(root, text="Duty Cycle", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    duty_label.grid(row=2,column=0, padx=0)
    
    duty_entry = ttk.Entry(root, textvariable=duty, font=('San Serif Pro', 16, 'italic'), justify=CENTER)
    duty_entry.config(width=15)
    duty_entry.grid(row=2, column=1)
    
    dutyEnd_label = ttk.Label(root, text="%", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    dutyEnd_label.grid(row=2,column=2)

    dutyNote_label = ttk.Label(root, text="(0-100%)", foreground='white', background="black", font=('San Serif Pro', 12))
    dutyNote_label.grid(row=2,column=3)

    ############
    #Row 3
    psen_label = ttk.Label(root, text="Power Supply Enable", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    psen_label.grid(row=3,column=0, padx=0)
    
    style = ttk.Style()
    style.configure('TCheckbutton', background='black')
    psen_checkbox = ttk.Checkbutton(root, variable=psen, onvalue='On', offvalue='Off')
    psen.set('Off')
    psen_checkbox.grid(row=3, column=1)
    
    psenState_label = ttk.Label(root, text="PSEN Off", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    psenState_label.grid(row=3,column=2)

    ############
    #Row 4
    len_label = ttk.Label(root, text="Logic PWM Enable", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    len_label.grid(row=4,column=0, padx=0)
    
    len_checkbox = ttk.Checkbutton(root, variable=len, onvalue='On', offvalue='Off')
    len.set('Off')
    len_checkbox.grid(row=4, column=1)
    
    lenState_label = ttk.Label(root, text="LEN Off", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    lenState_label.grid(row=4,column=2)

    #############
    #Row 5/6, Title
    style.configure('TSeparator', background='white', foreground='white')
    sepALine = ttk.Separator(root, orient=HORIZONTAL, style='TSeparator')
    sepALine.grid(row=5, column=0, columnspan=4, sticky='ew', padx=50)

    output_label = ttk.Label(root, text="Output Measurements", foreground='#582C83', background="black", font=('San Serif Pro', 22, 'bold italic underline'))
    output_label.grid(row=6,column=0, columnspan=3, padx=50)
    output_label.config(compound=RIGHT)

    ############
    # Outputs
    ############
    #Row 7
    dcl_label = ttk.Label(root, text="DC Link Voltage", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    dcl_label.grid(row=7,column=0, padx=0)
    
    dclReading_label = ttk.Label(root, text="0", foreground='white', background="black", font=('San Serif Pro', 12, 'italic'))
    dclReading_label.grid(row=7,column=1, padx=0)
        
    dclVoltage_label = ttk.Label(root, text="Volts", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    dclVoltage_label.grid(row=7,column=2)

    ##########
    #Row 8
    phaseACurrent_label = ttk.Label(root, text="Phase-A Output Current", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    phaseACurrent_label.grid(row=8,column=0, padx=0)
    
    phaseACurrentReading_label = ttk.Label(root, text="0", foreground='white', background="black", font=('San Serif Pro', 12, 'italic'), borderwidth=1)
    phaseACurrentReading_label.grid(row=8,column=1, padx=0)
        
    phaseACurrentUnits_label = ttk.Label(root, text="Amps", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    phaseACurrentUnits_label.grid(row=8,column=2)

    ##########
    #Row 9
    phaseAVoltage_label = ttk.Label(root, text="Phase-A Output Voltage", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    phaseAVoltage_label.grid(row=9,column=0, padx=0)
    
    phaseAVoltageReading_label = ttk.Label(root, text="0", foreground='white', background="black", font=('San Serif Pro', 12, 'italic'), borderwidth=1)
    phaseAVoltageReading_label.grid(row=9,column=1, padx=0)
        
    phaseAVoltageUnits_label = ttk.Label(root, text="Volts", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    phaseAVoltageUnits_label.grid(row=9,column=2)

    ##########
    #Row 10
    phaseATemperature_label = ttk.Label(root, text="Phase-A Temperature", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    phaseATemperature_label.grid(row=10,column=0, padx=0)
    
    phaseATemperatureReading_label = ttk.Label(root, text="0", foreground='white', background="black", font=('San Serif Pro', 12, 'italic'), borderwidth=1)
    phaseATemperatureReading_label.grid(row=10,column=1, padx=0)
        
    phaseATemperatureUnits_label = ttk.Label(root, text="°C", foreground='white', background="black", font=('San Serif Pro', 18, 'bold'))
    phaseATemperatureUnits_label.grid(row=10,column=2)

    ###########
    #row 11
    fault_label = ttk.Label(root, text="No Faults", foreground='green', background="black", font=('San Serif Pro', 24, 'bold italic'))
    fault_label.grid(row=11,column=0, padx=0)

    style.configure('TButton', background='#582C83', foreground='white', font=('San Serif Pro', 14, 'bold italic'))
    sendCAN_button = ttk.Button(root, command=buttonPress, text='Send CAN Message')
    sendCAN_button.grid(row=11, column=1, ipadx=2, ipady=2)

    connect_button = ttk.Button(root, command=busConnect, text='CAN Connect')
    connect_button.grid(row=11, column=2, ipadx=2, ipady=2)

    ###########
    #row 12
    sepBLine = ttk.Separator(root, orient=HORIZONTAL, style='TSeparator')
    sepBLine.grid(row=12, column=0, columnspan=4, sticky='ew', padx=50)

    ###########
    #row 13
    textBox = Text(root, width=95, height=6, relief=RIDGE)
    textBox.grid(row=13, column=0, columnspan=4, padx=5, pady=10)
    style.configure('Vertical.TScrollbar', troughcolor='black', background='white')
    textScroll = ttk.Scrollbar(root, orient=VERTICAL, command=textBox.yview)
    textScroll.grid(row=13, column=4, sticky='ns')
    textBox.config(yscrollcommand=textScroll.set, background='black', foreground='white')

    thread = threading.Thread(target=busThread)
    thread.daemon = True
    thread.start()

root.mainloop()