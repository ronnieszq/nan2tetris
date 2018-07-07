// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

   @SCREEN
   D=A
   @addr
   M=D    // addr = 16384
          // (screen's base address)
   @i
   M=0    // i = 0

(LOOP)
   @i
   D=M
   @8192  // number of pixels in the screen
   D=D-A
   @RESET
   D;JGT  // if i == 8192 goto RESET

   @KBD
   D=M
   @FILL
   D;JNE  // if RAM[KBD] != 0 goto FILL
   @addr
   A=M
   M=0    // RAM[addr] = 0000000000000000

   @i
   M=M+1  // i = i + 1
   @addr
   M=M+1  // addr = addr + 1
          // proceed to the next position
   @LOOP
   0;JMP  // goto LOOP

(FILL)
   @addr
   A=M
   M=-1   // RAM[addr] = 1111111111111111

   @i
   M=M+1  // i = i + 1
   @addr
   M=M+1  // addr = addr + 1
          // proceed to the next position
   @LOOP
   0;JMP  // goto LOOP

(RESET)
   @SCREEN
   D=A
   @addr
   M=D
   @i
   M=0
   @LOOP
   0;JMP  // goto LOOP
