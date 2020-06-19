"""CPU functionality."""

import sys
from os import path

HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
IRET = 0b00010011
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # init ram
        self.RAM = [0] * 256
        # init register
        self.REG = [0] * 8
        # init program counter
        self.PC = 0
        # init instruction register
        self.IR = 0
        # Memory Address Register
        self.MAR = 0
        # Memory Data Register
        self.MDR = 0
        # Flag
        self.FLAG = [0] * 8
        # Stack pointer
        self.SP = 0xf3

    def load(self):
        """Load a program into memory."""
        self.MAR = 0
        filename = sys.argv[1]

        # with open(program) as file:
        #     for line in file:
        #         # skip line breaks and comments:
        #         if line[0] is '#' or line[0] is '\n':
        #             continue
        #         self.MDR = int(line[:8], 2)
        #         self.ram_write(self.MDR, self.MAR)
        #         self.MAR += 1

        with open(filename) as program:
            for line in program:
                # separate out the # character
                line = line.split('#')
                # remove space at 0 index
                line = line[0].strip

                if line == '':
                    continue
                self.RAM[self.MAR] = int(line, 2)
                self.MAR += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.REG[reg_a] += self.REG[reg_b]
        elif op == 'MUL':
            self.REG[reg_a] *= self.REG[reg_b]
        # Compare ops
        elif op == 'CMP':
            # if equal, flag 1
            if self.REG[reg_a] == self.REG[reg_b]:
                self.FLAG = 0b00000001
            # if reg a is less than reg b set L flag to 1
            elif self.REG[reg_a] < self.REG[reg_b]:
                self.FLAG = 0b00000100
            # if reg a is greater than b set G flag to 1
            elif self.REG[reg_a] > self.REG[reg_b]:
                self.flag = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            #self.fl,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.REG[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            # instruction register at the program counter
            self.IR = self.ram_read(self.PC)

            if self.IR == LDI:
                # self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
                self.MAR = self.ram_read(self.pc + 1)
                self.MDR = self.ram_read(self.pc + 2)
                self.REG[self.MAR] = self.MDR
                self.PC += 3

            elif self.IR == CALL:
                # cals a function at the address stored in the register
                self.SP -= 1
                self.RAM[self.SP] = self.PC + 2
                self.PC = self.REG[self.ram_read(self.pc + 1)]

            elif self.IR == RET:
                self.PC = self.RAM[self.SP]
                self.SP += 1

            elif self.IR == PUSH:
                self.SP -= 1
                self.RAM[self.SP] = self.REG[self.ram_read(self.pc + 1)]
                self.PC += 2

            elif self.IR == POP:
                self.REG[self.ram_read(self.pc + 1)] = self.RAM[self.SP]
                self.SP += 1
                self.PC += 2

            elif self.IR == MUL:
                self.alu('MUL', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
                self.pc += 3

            elif self.IR == ADD:
                self.alu('ADD', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
                self.PC += 3

            elif self.IR == CMP:
                self.alu('CMP', self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
                self.PC += 3

            elif self.IR == JMP:
                self.PC = self.REG[self.ram_read(self.PC + 1)]

            elif self.IR == JNE:
                if not self.flag_check():
                    reg_num = self.RAM[self.PC + 1]
                    self.PC = self.REG[reg_num]
                else:
                    self.PC += 2

            elif self.IR == JEQ:
                if self.flag_check():
                    reg_num = self.RAM[self.PC + 1]
                    self.PC = self.REG[reg_num]
                else:
                    self.PC += 2

            elif self.IR == PRN:
                self.MAR = self.ram_read(self.pc + 1)
                print(self.reg[self.MAR])
                self.pc += 2

            elif self.IR == HLT:
                running = False
                self.PC += 1

            else: 
                print(f'Unknown instruction {self.IR} at address {self.PC}')
                sys.exit(1)

    def ram_read(self, memory_address):
        return self.RAM[memory_address]

    def ram_write(self, memory_data, memory_address):
        self.RAM[memory_address] = memory_data

    def flag_check(self):
        return (self.FLAG == 1)
