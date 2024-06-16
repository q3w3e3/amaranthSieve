from amaranth.sim import Simulator

from amaranth_sieve.sieve import Sieve

def test_sieve():
    print("woof")
    sieve = Sieve()
    async def testbench(ctx):
        ctx.get(sieve.isPrimeArray)
        await ctx.tick().repeat(3000)
    sim = Simulator(sieve)
    sim.add_clock(1)
    sim.add_testbench(testbench)
    with sim.write_vcd("sieve.vcd"):
        sim.run()