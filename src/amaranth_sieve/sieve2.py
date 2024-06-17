from amaranth import *
from amaranth.lib.wiring import Component, In, Out

bits_to_store=16
maxN=min(1000000,(2**bits_to_store)-1)

class TopLevel(Elaboratable):
    def elaborate(self,platform):
        m = Module()
        m.submodules.sieve = sieve = Sieve()

        button = platform.request("button").i

        platform.add_resources(platform.break_off_pmod)

        m.d.comb += sieve.reset.eq(button)
        
        m.d.comb += platform.request("led_r",1).o.eq(sieve.done)
        m.d.comb += platform.request("led_g",0).o.eq(button)

        return m

class Sieve(Component):
    isPrimeArray: Out(maxN,init=~0)
    done: Out(1)
    reset: In(1)

    def elaborate(self,platform):
        m = Module()
        pos = Signal(bits_to_store)
        prime = Signal.like(pos)


        with m.FSM():
            with m.State("INIT"):
                m.d.comb += self.isPrimeArray.eq(~1)
                m.d.comb += self.done.eq(0)
                m.d.sync += [
                    pos.eq(0),
                    prime.eq(0)
                ]
                with m.If(~self.reset):
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
                with m.If(prime > int(len(self.isPrimeArray)/2)):
                    m.next = "DONE"
                with m.Elif((pos+prime)<=len(self.isPrimeArray)):
                    m.d.sync += pos.eq(pos+prime)
                    m.next = "FLIPPING"
                with m.Else():
                    m.d.sync += pos.eq(prime)
                    m.next = "STEPPING"
            with m.State("FLIPPING"):
                m.d.comb += self.isPrimeArray.bit_select(abs(pos-1),1).eq(0)
                m.next = "STEPBYP"
            with m.State("DONE"):
                m.d.comb += self.done.eq(1)
                with m.If(self.reset):
                    m.next = "INIT"
        return m