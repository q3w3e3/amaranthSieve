# this is bad, this doesnt compile, do not do this, 

from amaranth import *
from amaranth.lib.wiring import Component, In, Out

width = 24

class Sieve(Component):
    #1. Create a list of consecutive integers from 2 through n: (2, 3, 4, ..., n).
    isPrimeArray: Out(width, init=~0)

    def elaborate(self,platform):

        flipMultiplesofP = FlipMultiplesofP()
        findFirstSetBit = FindFirstSetBit()

        m = Module()
        m.submodules += flipMultiplesofP, findFirstSetBit

        #2. Initially, let p equal 2, the smallest prime number.
        prime = Signal(20, init=2) 
        prime_initial = Signal.like(prime)

        with m.FSM():
            with m.State("Initializing"):
                #Mark 1 as not prime
                m.d.sync += self.isPrimeArray.eq(~1)
                m.next = "starting"
            with m.State("starting"):
                # handle shit for flipMultiplesofP
                m.d.sync += [
                    flipMultiplesofP.p.eq(prime), 
                    flipMultiplesofP.bits_in.eq(self.isPrimeArray),
                    flipMultiplesofP.run.eq(1)
                ]
                m.next = "waiting"
            with m.State("waiting"):
                with m.If(flipMultiplesofP.done):
                    m.next = "getting"
            with m.State("getting"):
                m.d.sync += self.isPrimeArray.eq(flipMultiplesofP.bits_out)
                m.d.sync += flipMultiplesofP.run.eq(0)
                m.next = "searching"
            with m.State("searching"):
                m.d.comb += [
                    findFirstSetBit.bits_in.eq(self.isPrimeArray),
                    findFirstSetBit.start.eq(prime+1)
                ]
                m.d.sync += prime_initial.eq(prime)
                m.d.sync += prime.eq(findFirstSetBit.n)
                m.next = "check conditions"
            with m.State("check conditions"):
                with m.If(prime > prime_initial):
                    m.next = "starting"
        return m



class FlipMultiplesofP(Component):
    p: In(20)
    bits_in: In(width)
    bits_out: Out(width)
    run: In(1)
    done: Out(1)

    def elaborate(self,platform):
        m = Module()

        i=Signal(20)

        accum = Signal.like(self.bits_in)
        m.d.comb += self.bits_out.eq(accum)

        with m.FSM():
            with m.State("Idle"):
                with m.If(self.run):
                    m.d.sync += accum.eq(self.bits_in)
                    m.d.sync += i.eq(self.p + self.p)
                    m.next = "Flip"
            with m.State("Flip"):
                with m.If(i <= len(accum)):
                    m.d.sync += accum.bit_select(abs(i-1),1).eq(0)
                    m.d.sync += i.eq(i + self.p)
                with m.Else():
                    m.next = "Done"
            with m.State("Done"):
                m.d.comb += self.done.eq(1)
                with m.If(~self.run):
                    m.next = "Idle"
        return m

class FindFirstSetBit(Component):
    n: Out(20, init=1)
    start: In(20)
    bits_in: In(width)

    def elaborate(self,platform):

        m = Module()

        with m.If(0):
            pass
        for i in range(0, len(self.bits_in)):
            with m.Elif((i >= self.start) & ~self.bits_in[i]):
                m.d.comb += self.n.eq(i)
        return m