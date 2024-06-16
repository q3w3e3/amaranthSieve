# chain of 1000000 1 bit registers
# start at second position (flip first as 1 is not prime)
# store this pisiton to a 20 bit register (n)
# flip that bit
# move n positions along the chain
# flip this bit
# move again
# flip
# until at end of chain
# move to start of chain
# look for first set bit
# goto: store this pisiton to a 20 bit register (n)


"""
1. INIT
pos = 1
prime = 0
array = 
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
^
flip first bit

2. STEPPING
pos = 2
prime = 0
array = 
0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
  ^
  step right 
  if {pos} < len(array) GOTO 3
  else GOTO 6

3. CHECKING
pos = 2
prime = 2
array = 
0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
  ^
  if bit is set store {pos} to {prime}
  else GOTO 2


4. STEPBYP
pos = 4
prime = 2
array = 
0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
      ^
      if {pos}+{prime} < len(array) 
        step right by {prime} 
      else
        else set {pos} to {prime} and GOTO 2
5. FLIPPING
pos = 4
prime = 2
array = 
0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1
      ^
      flip bit at {pos}
      GOTO 4

6.

DONE

"""

from amaranth import *
from amaranth.lib.wiring import Component, In, Out

nPrimes=10000
bits_to_store=20

class Sieve(Component):
    isPrimeArray: Out(nPrimes,init=~0)
    done: Out(1)

    def elaborate(self,platform):
        m = Module()
        pos = Signal(bits_to_store)
        prime = Signal.like(pos)

        with m.FSM():
            with m.State("INIT"):
                m.d.sync += self.isPrimeArray.eq(~1)
                m.next = "STEPPING"
            with m.State("STEPPING"):
                m.d.sync += pos.eq(pos+1)
                with m.If(pos<=len(self.isPrimeArray)):
                    m.next = "CHECKING"
                with m.Else():
                    m.next = "DONE"
            with m.State("CHECKING"):
                with m.If(self.isPrimeArray.bit_select(abs(pos-1),1)):
                    m.d.sync += prime.eq(pos)
                    m.next = "STEPBYP"
                with m.Else():
                    m.next = "STEPPING"
            with m.State("STEPBYP"):
                with m.If((pos+prime)<=len(self.isPrimeArray)):
                    m.d.sync += pos.eq(pos+prime)
                    m.next = "FLIPPING"
                with m.Else():
                    m.d.sync += pos.eq(prime)
                    m.next = "STEPPING"
            with m.State("FLIPPING"):
                m.d.sync += self.isPrimeArray.bit_select(abs(pos-1),1).eq(0)
                m.next = "STEPBYP"
            with m.State("DONE"):
                m.d.comb += self.done.eq(1)
        return m