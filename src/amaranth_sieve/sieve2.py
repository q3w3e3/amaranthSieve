from amaranth import *
from amaranth.lib.wiring import Component, In, Out
from amaranth.lib.memory import Memory

bits_to_store = 12
maxN = min(1000000, (2**bits_to_store) - 1)


class TopLevel(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.submodules.sieve = sieve = Sieve()

        platform.add_resources(platform.break_off_pmod)

        button = platform.request("button", 1).i

        m.d.comb += sieve.reset.eq(button)

        m.d.comb += platform.request("led_r", 1).o.eq(sieve.done)
        m.d.comb += platform.request("led_g", 0).o.eq(button)

        return m


class Sieve(Component):
    isPrimeArray: Out(maxN, init=~0) ## LETS STOP DOING THIS 
    done: Out(1)
    reset: In(1)

    def __init__(self):
        super().__init__()
        self.pos = Signal(bits_to_store)
        self.prime = Signal.like(self.pos)

    def elaborate(self, platform):
        m = Module()

        with m.FSM():
            with m.State("INIT"):
                m.d.sync += self.isPrimeArray.eq(~1)
                m.d.comb += self.done.eq(0)
                m.d.sync += [self.pos.eq(0), self.prime.eq(0)]
                with m.If(~self.reset):
                    m.next = "STEPPING"
            with m.State("STEPPING"):
                m.d.sync += self.pos.eq(self.pos + 1)
                with m.If(self.pos <= len(self.isPrimeArray)):
                    m.next = "CHECKING"
                with m.Else():
                    m.next = "DONE"
            with m.State("CHECKING"):
                with m.If(self.isPrimeArray.bit_select(abs(self.pos - 1), 1)):
                    m.d.sync += self.prime.eq(self.pos)
                    m.next = "STEPBYP"
                with m.Else():
                    m.next = "STEPPING"
            with m.State("STEPBYP"):
                with m.If(self.prime > int(len(self.isPrimeArray) / 2)):
                    m.next = "DONE"
                with m.Elif((self.pos + self.prime) <= len(self.isPrimeArray)):
                    m.d.sync += self.pos.eq(self.pos + self.prime)
                    m.next = "FLIPPING"
                with m.Else():
                    m.d.sync += self.pos.eq(self.prime)
                    m.next = "STEPPING"
            with m.State("FLIPPING"):
                m.d.sync += self.isPrimeArray.bit_select(abs(self.pos - 1), 1).eq(0)
                m.next = "STEPBYP"
            with m.State("DONE"):
                m.d.comb += self.done.eq(1)
                with m.If(self.reset):
                    m.next = "INIT"
        return m


class PrimeMemory(Component): ## THIS DOESNT QUITE WORK AS IS, READS LAG BEHIND ADDR BY ONE CYCLE 
    n: In(bits_to_store)
    wr_enable: In(1)
    write: In(1)
    read: Out(1)

    def __init__(self, bits):
        super().__init__()
        self.memory = Memory(shape=8,depth=3,init=b"\xff\x00\x77")
        self.wr_port = self.memory.write_port()
        self.r_port = self.memory.read_port(domain="comb") #does the read need to be transparent for the writes? does this matter? maybe comb domain?

    def elaborate(self, platform): 
        m = Module()

        m.submodules += self.memory

        row = self.n//self.memory.shape
        offset = self.n % self.memory.shape

        m.d.comb += self.r_port.addr.eq(row)

        m.d.comb += self.wr_port.en.eq(self.wr_enable)
        m.d.comb += self.read.eq(self.r_port.data.bit_select(offset,1))


        m.d.comb += [
            self.wr_port.addr.eq( row ),
            self.wr_port.data.eq(self.r_port.data | (1 << offset))
        ]

        
        return m 

