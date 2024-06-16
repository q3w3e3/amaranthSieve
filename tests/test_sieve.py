from amaranth.sim import Simulator

from amaranth_sieve.sieve2 import Sieve as Sieve2
from amaranth_sieve.sieve import Sieve

def test_sieve():
    length = 100

    sieve = Sieve()

    sim = Simulator(sieve)
    sim.add_clock(period=1)
    with sim.write_vcd("sieve.vcd"):
        sim.run_until(length)

def test_sieve2():
    sieve2 = Sieve2()

    async def testbench(ctx):
        while ctx.get(~sieve2.done):
            await ctx.tick().repeat(3)

    sim2 = Simulator(sieve2)
    sim2.add_clock(period=1e-6)
    sim2.add_testbench(testbench)
    with sim2.write_vcd("sieve2.vcd"):
        sim2.run()