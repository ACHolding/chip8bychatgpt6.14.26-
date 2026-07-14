#!/usr/bin/env python3

# ==========================================
# ChatGPT CHIP-8 Emulator
# Single File
# mGBA Inspired Blue GUI
# ==========================================

import tkinter as tk
from tkinter import filedialog, messagebox
import random


# CHIP-8 screen
WIDTH = 64
HEIGHT = 32
SCALE = 10

BLUE = "#33ccff"
BLACK = "#000000"


FONT = [
0xF0,0x90,0x90,0x90,0xF0,
0x20,0x60,0x20,0x20,0x70,
0xF0,0x10,0xF0,0x80,0xF0,
0xF0,0x10,0xF0,0x10,0xF0,
0x90,0x90,0xF0,0x10,0x10,
0xF0,0x80,0xF0,0x10,0xF0,
0xF0,0x80,0xF0,0x90,0xF0,
0xF0,0x10,0x20,0x40,0x40,
0xF0,0x90,0xF0,0x90,0xF0,
0xF0,0x90,0xF0,0x10,0xF0
]


class CHIP8:

    def __init__(self):

        self.memory = [0]*4096

        self.V = [0]*16

        self.I = 0

        self.pc = 0x200

        self.stack = []

        self.delay = 0
        self.sound = 0

        self.keys = [0]*16

        self.display = [
            [0]*WIDTH
            for _ in range(HEIGHT)
        ]

        self.load_font()


    def load_font(self):

        for i,b in enumerate(FONT):
            self.memory[0x50+i] = b



    def reset(self):

        self.__init__()



    def load_rom(self,path):

        self.reset()

        with open(path,"rb") as f:
            rom=f.read()

        for i,b in enumerate(rom):
            self.memory[
                0x200+i
            ]=b



    def cycle(self):

        opcode = (
            self.memory[self.pc] << 8
            |
            self.memory[self.pc+1]
        )

        self.pc += 2


        x = (opcode & 0x0F00)>>8
        y = (opcode & 0x00F0)>>4
        n = opcode & 0x000F
        kk = opcode & 0x00FF
        addr = opcode & 0x0FFF


        if opcode == 0x00E0:

            self.display=[
                [0]*WIDTH
                for _ in range(HEIGHT)
            ]


        elif opcode == 0x00EE:

            self.pc=self.stack.pop()


        elif opcode & 0xF000 == 0x1000:

            self.pc=addr


        elif opcode & 0xF000 == 0x2000:

            self.stack.append(self.pc)
            self.pc=addr


        elif opcode & 0xF000 == 0x6000:

            self.V[x]=kk


        elif opcode & 0xF000 == 0x7000:

            self.V[x]=(self.V[x]+kk)&255


        elif opcode & 0xF000 == 0xA000:

            self.I=addr


        elif opcode & 0xF000 == 0xD000:

            vx=self.V[x]
            vy=self.V[y]

            self.V[0xF]=0


            for row in range(n):

                sprite=self.memory[
                    self.I+row
                ]

                for col in range(8):

                    if sprite & (0x80>>col):

                        px=(vx+col)%WIDTH
                        py=(vy+row)%HEIGHT

                        if self.display[py][px]:
                            self.V[0xF]=1

                        self.display[py][px]^=1



        elif opcode & 0xF000 == 0x3000:

            if self.V[x]==kk:
                self.pc+=2


        elif opcode & 0xF000 == 0x4000:

            if self.V[x]!=kk:
                self.pc+=2


        elif opcode & 0xF000 == 0x5000:

            if self.V[x]==self.V[y]:
                self.pc+=2


        elif opcode & 0xF00F == 0x8000:

            self.V[x]=self.V[y]


        elif opcode & 0xF00F == 0x8004:

            total=self.V[x]+self.V[y]

            self.V[0xF]=1 if total>255 else 0

            self.V[x]=total&255



        elif opcode & 0xF00F == 0x8005:

            self.V[0xF]=1 if self.V[x]>self.V[y] else 0

            self.V[x]-=self.V[y]

            self.V[x]&=255



        elif opcode & 0xF000 == 0xF000:

            if kk==0x15:
                self.delay=self.V[x]

            elif kk==0x18:
                self.sound=self.V[x]

            elif kk==0x29:
                self.I=0x50+self.V[x]*5



        if self.delay:
            self.delay-=1

        if self.sound:
            self.sound-=1




class GUI:

    def __init__(self):

        self.root=tk.Tk()

        self.root.title(
            "CHIP-8 Emulator"
        )

        self.root.configure(
            bg=BLACK
        )


        self.chip=CHIP8()


        self.canvas=tk.Canvas(
            self.root,
            width=WIDTH*SCALE,
            height=HEIGHT*SCALE,
            bg=BLACK
        )

        self.canvas.pack()


        for text,cmd in [

            ("LOAD ROM",self.load),
            ("PLAY GAME",self.start),
            ("RUN EMULATOR",self.run),
            ("ABOUT",self.about),
            ("EXIT",self.root.destroy)

        ]:

            tk.Button(
                self.root,
                text=text,
                command=cmd,
                bg=BLACK,
                fg=BLUE
            ).pack(fill="x")


        self.running=False

        self.loop()

        self.root.mainloop()



    def load(self):

        file=filedialog.askopenfilename()

        if file:
            self.chip.load_rom(file)



    def start(self):

        self.running=True



    def run(self):

        self.chip.cycle()



    def draw(self):

        self.canvas.delete("all")

        for y in range(HEIGHT):

            for x in range(WIDTH):

                if self.chip.display[y][x]:

                    self.canvas.create_rectangle(
                        x*SCALE,
                        y*SCALE,
                        x*SCALE+SCALE,
                        y*SCALE+SCALE,
                        fill=BLUE,
                        outline=""
                    )



    def loop(self):

        if self.running:

            for _ in range(10):
                self.chip.cycle()


        self.draw()

        self.root.after(
            1000//60,
            self.loop
        )



    def about(self):

        messagebox.showinfo(
            "About",
            "Single File CHIP-8 Emulator\nPython"
        )



if __name__=="__main__":
    GUI()