import random
import math
import os
import time

from graphics import *
import keyboard

class chip8:

    const_START_ADDRESS = 0x200
    const_FONTSET_START_ADDRESS = 0x50
    const_VIDEO_WIDTH = 64
    const_VIDEO_HEIGHT = 32
    #declaring stuff
    registers = [0] *16
    memory = [0]*4096
    indexRegister = 0
    programCounter = 0x200
    stack = [0] * 16
    stackPointer = 0
    delayTimer = 0
    soundTimer = 0
    inputKeys = 0
    displayMemory = [0]*(64*32)
    opcode = 0
    keypad = [0]*16
    drawflag = False
    fontset = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
	0x20, 0x60, 0x20, 0x20, 0x70, # 1
	0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
	0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
	0x90, 0x90, 0xF0, 0x10, 0x10, # 4
	0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
	0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
	0xF0, 0x10, 0x20, 0x40, 0x40, # 7
	0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
	0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
	0xF0, 0x90, 0xF0, 0x90, 0x90, # A
	0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
	0xF0, 0x80, 0x80, 0x80, 0xF0, # C
	0xE0, 0x90, 0x90, 0x90, 0xE0, # D
	0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
	0xF0, 0x80, 0xF0, 0x80, 0x80 # F
    ]
    

    def loadROM(self, filename):
        f = open(filename, 'rb')
        for i in range(os.path.getsize(filename)):
            self.memory[self.const_START_ADDRESS + i] = f.read(1)
            
            
    def chip8(self):
        for i in range(len(self.fontset)):
            self.memory[self.const_FONTSET_START_ADDRESS + i] = self.fontset[i]

    def randGen(self):
        return random.randint(0,255)
    #wipe display memory
    def OP_00E0(self):
         self.displayMemory = [0]*(64*32)
         self.drawflag = True
    # return from subroutine
    def OP_00EE(self):
        self.stackPointer = self.stackPointer - 1
        self.programCounter = self.stack[self.stackPointer]
    
    # jump to location nnn
    def OP_1nnn(self):
        address = self.opcode & 0x0FFF
        #print(hex(self.opcode),address)
        self.programCounter = address
    
    # call sub-routine at nnn
    def OP_2nnn(self):
        address = self.opcode & 0x0FFF
        self.stack[self.stackPointer] = self.programCounter
        self.stackPointer = self.stackPointer + 1
        self.programCounter = address

    # Skip next instruction if Vx = kk
    def OP_3xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        if (self.registers[Vx] == byte):
	        self.programCounter = self.programCounter + 2
    
    # Skip next instruction if Vx != kk
    def OP_4xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        if (self.registers[Vx] != byte):
	        self.programCounter += 2
    # Skip next instruction if Vx = Vy
    def OP_5xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        if (self.registers[Vx] == self.registers[Vy]):
	        self.programCounter += 2
    
    # Set Vx equal to kk
    def OP_6xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        self.registers[Vx] = byte
	         
    
    # Set Vx equal to Vx + kk
    def OP_7xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        self.registers[Vx] = self.registers[Vx] +  byte
        if self.registers[Vx] > 255:
            self.registers[Vx] -=256
    
    # Set Vx = Vy
    def OP_8xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[Vx] = self.registers[Vy]

    # Set Vx = Vx OR Vy
    def OP_8xy1(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[Vx] = self.registers[Vx] | self.registers[Vy]

    # Set Vx = Vx AND Vy
    def OP_8xy2(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[Vx] = self.registers[Vx] & self.registers[Vy]
    
    # Set Vx = Vx XOR Vy
    def OP_8xy3(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[Vx] = self.registers[Vx] ^ self.registers[Vy]

    # Set Vx = Vx + Vy, set VF = carry
    def OP_8xy4(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        summ = self.registers[Vx] + self.registers[Vy]
        if(summ > 255):
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0
        self.registers[Vx] = summ & 0xFF
    
    # Set Vx = Vx - Vy, set VF = NOT borrow
    def OP_8xy5(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        if(self.registers[Vx] > self.registers[Vy]):
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0
        self.registers[Vx] = self.registers[Vx] - self.registers[Vy]
        if self.registers[Vx] < 0:
            self.registers[Vx] += 256
    
    # Set Vx = Vx SHR 1
    def OP_8xy6(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.registers[0xF] = (self.registers[Vx] & 0x1)
        self.registers[Vx] = self.registers[Vx] >> 1
    
    # Set Vx = Vy - Vx, set VF = NOT borrow
    def OP_8xy7(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        if(self.registers[Vy] > self.registers[Vx]):
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0
        self.registers[Vx] = self.registers[Vy] - self.registers[Vx]
    
    # Set Vx = Vx SHL 1
    def OP_8xyE(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.registers[0xF] = (self.registers[Vx] & 0x80) >> 7
        self.registers[Vx] = self.registers[Vx] << 1
    
    # Skip next instruction if Vx != Vy
    def OP_9xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        if(self.registers[Vy] != self.registers[Vx]):
            self.programCounter = self.programCounter + 2
    
    # set index =  to location nnn
    def OP_Annn(self):
        address = self.opcode & 0x0FFF
        self.indexRegister = address
    
    # jump to location nnn + V0
    def OP_Bnnn(self):
        address = self.opcode & 0x0FFF
        self.programCounter = address + self.registers[0]
    
    # Set Vx equal to random byte AND kk
    def OP_Cxkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        self.registers[Vx] = random.randint(0,255) & byte
    
    # Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
    def OP_Dxyn(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        height = self.opcode & 0x000F

        xpos = self.registers[Vx] % self.const_VIDEO_WIDTH
        ypos = self.registers[Vy] % self.const_VIDEO_HEIGHT

        self.registers[0xF] = 0
        for row in range(height):
            spriteByte = self.memory[self.indexRegister + row]
            if isinstance(spriteByte,bytes):
                spriteByte = int.from_bytes(spriteByte, "big")
            for col in range(8):
                spritePixel = spriteByte & (0x80 >> col)
                pNo = (ypos + row) * self.const_VIDEO_WIDTH + (xpos + col)
                if pNo > 2047:
                    pNo -= 2048
                screenPixel = self.displayMemory[pNo]
               
                if(spritePixel):
                    if(screenPixel == 0xFFFFFFFF):
                        self.registers[0xF] = 1
                    self.displayMemory[pNo] = screenPixel ^ 0xFFFFFFFF
        self.drawflag = True
    
    # Skip next instruction if key Vx is pressed
    def OP_Ex9E(self):
        Vx = (self.opcode & 0x0F00) >> 8
        key = self.registers[Vx]
        if (self.keypad[key]):
	        self.programCounter = self.programCounter + 2
    
    # Skip next instruction if key Vx is not pressed
    def OP_ExA1(self):
        Vx = (self.opcode & 0x0F00) >> 8
        key = self.registers[Vx]
        if (not self.keypad[key]):
	        self.programCounter = self.programCounter + 2

    # Set Vx = delay timer
    def OP_Fx07(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.registers[Vx] = self.delayTimer
    
    # wait for key, store value of keyin Vx
    def OP_Fx0A(self):
        Vx = (self.opcode & 0x0F00) >> 8
        i = 0
        for val in self.keypad:
            if val:
                self.registers[Vx] = i
                break
            else:
                i += 1
        if(i == 16):
            self.programCounter -= 2
        
    # Set delaytimer = Vx
    def OP_Fx15(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.delayTimer = self.registers[Vx] 
    
    # Set soundtimer = Vx
    def OP_Fx18(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.soundTimer = self.registers[Vx] 
    
    # Set index = index + Vx
    def OP_Fx1E(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.indexRegister += self.registers[Vx]

    # Set index = to location of sprite for digit Vx
    def OP_Fx29(self):
        Vx = (self.opcode & 0x0F00) >> 8
        digit = self.registers[Vx]
        self.indexRegister = self.const_FONTSET_START_ADDRESS + (5 * digit)
    
    # Store BCD of Vx in index, index + 1 and index + 2
    def OP_Fx33(self):
        Vx = (self.opcode & 0x0F00) >> 8
        value = self.registers[Vx]
        self.memory[self.indexRegister + 2] = math.trunc(value % 10)
        value /= 10
        self.memory[self.indexRegister + 1] = math.trunc(value % 10)
        value /= 10
        self.memory[self.indexRegister] = math.trunc(value % 10)
    
    # store registers V0 - Vx starting at index
    def OP_Fx55(self):
        Vx = (self.opcode & 0x0F00) >> 8
        for i in range(Vx+1):
            self.memory[self.indexRegister + i] =  self.registers[i]

    # read registers V0 - Vx starting at index
    def OP_Fx65(self):
        Vx = (self.opcode & 0x0F00) >> 8
        for i in range(Vx+1):
            self.registers[i] = self.memory[self.indexRegister + i]
    
    #TODO This function needs code cleaned up
    def executeInsruction(self, opcode):
        op1 = opcode & 0xF000
        if(op1 == 0x0000):
            
            if opcode == 0x00E0:
                
               self.OP_00E0(self)
               
            else:
                if opcode == 0x00EE:
                    
                    self.OP_00EE(self)
                #else:
                 #   print(hex(opcode))
                    
                   
        else:
            if op1 == 0x1000:
                self.OP_1nnn(self)
            else:
                if op1 == 0x2000:
                    self.OP_2nnn(self)
                else:
                    if op1 == 0x3000:
                        self.OP_3xkk(self)
                    else:
                        if op1 == 0x4000:
                            self.OP_4xkk(self)
                        else:
                            if op1 == 0x5000:
                                self.OP_5xy0(self)
                            else:
                                if op1 == 0x6000:
                                    self.OP_6xkk(self)
                                else: 
                                    if op1 == 0x7000:
                                        self.OP_7xkk(self)
                                    else:
                                        if op1 == 0x8000:
                                            op2 = opcode & 0xF
                                            if op2 == 0x0:
                                                self.OP_8xy0(self)
                                            else:
                                                if op2 == 0x1:
                                                    self.OP_8xy1(self)
                                                else:
                                                    if op2 == 0x2:
                                                        self.OP_8xy2(self)
                                                    else:
                                                        if op2 == 0x3:
                                                            self.OP_8xy3(self)
                                                        else:
                                                            if op2 == 0x4:
                                                                self.OP_8xy4(self)
                                                            else:
                                                                if op2 == 0x5:
                                                                    self.OP_8xy5(self)
                                                                else:
                                                                    if op2 == 0x6:
                                                                        self.OP_8xy6(self)
                                                                    else:
                                                                        if op2 == 0x7:
                                                                            self.OP_8xy7(self)
                                                                        else:
                                                                            if op2 == 0xE:
                                                                                self.OP_8xyE(self)
                                                                            
                                        elif op1 == 0x9000:
                                            self.OP_9xy0(self)
                                        elif op1 == 0xA000:
                                            #print("yo")
                                            self.OP_Annn(self)
                                        elif op1 == 0xB000:
                                            self.OP_Bnnn(self)
                                        elif op1 == 0xC000:
                                            self.OP_Cxkk(self)
                                        elif op1 == 0xD000:
                                            #print("helo")
                                            self.OP_Dxyn(self)
                                        elif op1 == 0xE000:
                                            op2 = opcode & 0xFF
                                            if op2 == 0x9E:
                                                self.OP_Ex9E(self)
                                            elif op2 == 0xA1:
                                                self.OP_ExA1(self)
                                        elif op1 == 0xF000:
                                            op2 = opcode & 0xFF
                                            #print(hex(op2))
                                            if op2 == 0x07:
                                                self.OP_Fx07(self)
                                            elif op2 == 0x0A:
                                                self.OP_Fx0A(self)
                                            elif op2 == 0x15:
                                                self.OP_Fx15(self)
                                            elif op2 == 0x18:
                                                self.OP_Fx18(self)
                                            elif op2 == 0x1E:
                                                self.OP_Fx1E(self)
                                            elif op2 == 0x29:
                                                self.OP_Fx29(self)
                                            elif op2 == 0x33:
                                                self.OP_Fx33(self)
                                            elif op2 == 0x55:
                                                self.OP_Fx55(self)
                                            elif op2 == 0x65:
                                                self.OP_Fx65(self)
                                            else:
                                                print("Error: Opcode: ", hex(opcode) , " not found")
                                                



                                            


    def getInput(self):
        if keyboard.is_pressed('1'):
            self.keypad[0] = True
        else:
            self.keypad[0] = False
        if keyboard.is_pressed('2'):
            self.keypad[1] = True
        else:
            self.keypad[1] = False
        if keyboard.is_pressed('3'):
            self.keypad[2] = True
        else:
            self.keypad[2] = False
        if keyboard.is_pressed('4'):
            self.keypad[3] = True
        else:
            self.keypad[3] = False
        if keyboard.is_pressed('q'):
            self.keypad[4] = True
        else:
            self.keypad[4] = False
        if keyboard.is_pressed('w'):
            self.keypad[5] = True
        else:
            self.keypad[5] = False
        if keyboard.is_pressed('e'):
            self.keypad[6] = True
        else:
            self.keypad[6] = False
        if keyboard.is_pressed('r'):
            self.keypad[7] = True
        else:
            self.keypad[7] = False
        if keyboard.is_pressed('a'):
            self.keypad[8] = True
        else:
            self.keypad[8] = False
        if keyboard.is_pressed('s'):
            self.keypad[9] = True
        else:
            self.keypad[9] = False
        if keyboard.is_pressed('d'):
            self.keypad[10] = True
        else:
            self.keypad[10] = False
        if keyboard.is_pressed('f'):
            self.keypad[11] = True
        else:
            self.keypad[11] = False
        if keyboard.is_pressed('z'):
            self.keypad[12] = True
        else:
            self.keypad[12] = False
        if keyboard.is_pressed('x'):
            self.keypad[13] = True
        else:
            self.keypad[13] = False
        if keyboard.is_pressed('c'):
            self.keypad[14] = True
        else:
            self.keypad[14] = False
        if keyboard.is_pressed('v'):
            self.keypad[15] = True
        else:
            self.keypad[15] = False

    def cycle(self):
        
            opPt1 = self.memory[self.programCounter]
           
            opPt2 = self.memory[self.programCounter + 1]
            
            if(isinstance(opPt1, bytes)):
                opPt1 = int.from_bytes(opPt1,"big")
            if(isinstance(opPt2, bytes)):
                opPt2 = int.from_bytes(opPt2,"big")
            self.opcode = ((opPt1 << 8) | opPt2)
            self.programCounter += 2
            self.executeInsruction(self, self.opcode)
            if self.delayTimer > 0:
                self.delayTimer -= 1
            if self.soundTimer > 0:
                self.soundTimer -= 1

def drawVideo(emu, win, scale):   
    for j in range(32):
        for i in range(64):
            if emu.displayMemory[i + 64*j]:
                
                point1 = Point(i*scale,j*scale)
                point2 = Point(i*scale + scale, j*scale + scale)
                pixel = Rectangle(point1,point2)
                pixel.setFill('black')
                pixel.draw(win)
           



def main():
    videoscale, fps, rom = input("Enter Options in format <videoscale (10 recommended)> <targetfps (>100 recommended)> <rom file>: ").split()
    videoscale = int(videoscale)
    fps = int(fps)
    #videoscale = 10
    #fps = 100
    #rom = "Tetris.ch8"
    win = GraphWin("Chip8", 64 * videoscale,32*videoscale, autoflush=False)
    emu = chip8
    emu.loadROM(emu, rom)
    emu.chip8(emu)
    quit = False

   
    i = 0
    x = 0
    lastTime = time.time_ns()/1000000
    
    while(not quit):
        currentTime = time.time_ns()/1000000
        if (currentTime - lastTime) > 1000/fps:
            lastTime = currentTime

            if keyboard.is_pressed('0'):
                quit = True
            emu.cycle(emu)
            emu.getInput(emu)
    
            for item in win.items:
                item.undraw()
            if emu.drawflag:
                drawVideo(emu,win,videoscale)
                win.update()
                emu.drawflag = False
            
        
        
        
        
            
    
    
   
    win.close()
    


    
    
        


     
            
            

main()
        

    

	    
    
	

