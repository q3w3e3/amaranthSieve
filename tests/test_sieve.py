from amaranth.sim import Simulator

from amaranth_sieve.sieve2 import Sieve as Sieve2

def test_sieve2():
    sieve2 = Sieve2()

    async def testbench(ctx):
        while ctx.get(~sieve2.done):
            await ctx.tick()


    sim2 = Simulator(sieve2)
    sim2.add_clock(period=1.667e-7)
    sim2.add_testbench(testbench)
    with sim2.write_vcd("sieve2.vcd"):
        sim2.run()