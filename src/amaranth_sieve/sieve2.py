from amaranth import *
from amaranth.lib.wiring import Component, In, Out
from amaranth.lib.memory import Memory

bits_to_store = 136
#maxN = min(1000000, (2**bits_to_store) - 1)

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
    #PrimeArray: Out(maxN, init=~0) ## LETS STOP DOING THIS 
    done: Out(1)
    reset: In(1)

    def __init__(self):
        super().__init__()
        self.pos = Signal(bits_to_store)
        self.prime = Signal.like(self.pos)

        self.PrimeArray = PrimeMemory(8,bits_to_store) # Mess with width for Optimizaiton.

    def elaborate(self, platform):
        m = Module()

        m.submodules += self.PrimeArray

        m.d.comb += [ 
                    self.PrimeArray.write.eq(0),
                    self.PrimeArray.wr_enable.eq(0)
                    ]
        
        m.d.comb += self.PrimeArray.n.eq(self.pos)



        with m.FSM():
            with m.State("INIT"):
                ## TODO add way to init the memory, presently it is set to all 1 by the init above

                m.d.comb += self.done.eq(0)
                m.d.sync += [self.pos.eq(0), self.prime.eq(0)]
                with m.If(~self.reset):
                    m.next = "STEPPING"

            with m.State("STEPPING"):
                m.d.sync += self.pos.eq(self.pos + 1)
                with m.If(self.pos <= bits_to_store):
                    m.next = "CHECKING"
                with m.Else():
                    m.next = "DONE"

            with m.State("CHECKING"):
                #with m.If(self.PrimeArray.bit_select(abs(self.pos - 1), 1)): # cant do this anymore 
                with m.If(self.PrimeArray.read):
                    m.d.sync += self.prime.eq(self.pos)
                    m.next = "STEPBYP"
                with m.Else():
                    m.next = "STEPPING"

            with m.State("STEPBYP"):
                # with m.If(self.prime > int(len(self.PrimeArray) / 2)):
                #     m.next = "DONE"
                with m.If((self.pos + self.prime) <= len(self.PrimeArray)):
                    m.d.sync += self.pos.eq(self.pos + self.prime)
                    m.next = "FLIPPING"
                with m.Else():
                    m.d.sync += self.pos.eq(self.prime)
                    m.next = "STEPPING"

            with m.State("FLIPPING"):
                ## this is the fun bit 

                ## TODO: check if the memory is actually ready so that things like 25 (8*3+1) actually get marked off........
                m.d.comb += [ 
                    self.PrimeArray.write.eq(0),
                    self.PrimeArray.wr_enable.eq(1)
                ]
                m.next = "STEPBYP"

            with m.State("DONE"):
                m.d.comb += self.done.eq(1)
                with m.If(self.reset):
                    m.next = "INIT"
        return m


class PrimeMemory(Component): ## TODO: add a way to re-init this ?
    n: In(bits_to_store)
    wr_enable: In(1)
    write: In(1)
    read: Out(1)
    ready: Out(1)

    def __init__(self, width, bits):
        super().__init__()

        depth = -(-bits//width)

        self.memory = Memory(shape=width,depth=depth,init=[~1]+([~0]*(depth-1)))
        print(self.memory.init)
        self.wr_port = self.memory.write_port(granularity=1) # I get choice of either 1 granularity here, or transparency below
        self.rd_port = self.memory.read_port() #does the read need to be transparent for the writes? does this matter?

        self.position = Signal.like(self.n)
        self.row = Signal(self.memory.depth)
        self.offset = Signal(self.memory.shape)

    def __len__(self):
        return self.memory.depth * self.memory.shape

    def elaborate(self, platform): 
        m = Module()

        m.submodules += self.memory

        prev_row = Signal.like(self.row)

        m.d.sync += prev_row.eq(self.row)

        m.d.comb += self.position.eq(self.n-1)

        m.d.comb += self.row.eq(self.position // self.memory.shape)
        m.d.comb += self.offset.eq(self.position % self.memory.shape)
        m.d.comb += self.rd_port.addr.eq(self.row)

        m.d.comb += self.wr_port.en.eq(self.wr_enable << self.offset) # if use transparancy, remove this shift (maybe)
        
        m.d.comb += [
            self.wr_port.addr.eq(self.row),
            #self.wr_port.data.eq( ( self.rd_port.data & ~( 1 << self.offset )) | ( self.write << self.offset))
            self.wr_port.data.eq(0)
        ]


        ## the purpose of the below was to handle state during the 1 cycle delay on reading a new row
        with m.FSM():
            with m.State("BECOMING_UNREADY"):

                m.d.comb += self.ready.eq(1)

                m.d.comb += self.read.eq(self.rd_port.data.bit_select(self.offset,1))

                with m.If(self.row != prev_row):
                    m.d.comb += self.ready.eq(0)
                    m.next = "BECOMING_READY"
                    
            with m.State("BECOMING_READY"):
                m.d.comb += self.ready.eq(1) ##  im just... like... waiting a cycle for the state change and then going back ready.... that feels Bad?
                m.next = "BECOMING_UNREADY"
        
        return m 

