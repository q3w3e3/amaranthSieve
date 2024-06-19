from amaranth.sim import Simulator

from amaranth_sieve.sieve2 import Sieve as Sieve2
from amaranth_sieve.sieve2 import PrimeMemory

# def test_sieve2():
#     sieve2 = Sieve2()

#     async def testbench(ctx):
#         while ctx.get(~sieve2.done):
#             await ctx.tick()


#     sim2 = Simulator(sieve2)
#     sim2.add_clock(period=1.667e-7)
#     sim2.add_testbench(testbench)
#     with sim2.write_vcd("sieve2.vcd"):
#         sim2.run()

def test_memory():
    memory = PrimeMemory(256)

    async def testbench(ctx):
        ctx.set(memory.write,1)
        for n in range(24):
            ctx.set(memory.n,n)
            await ctx.tick()
        await ctx.tick().repeat(10)
        for n in range(24):
            ctx.set(memory.n,n)
            #await ctx.tick() ## if i dont wait here then my Write will use the last row read, which isnt fine when changing rows
            ctx.set(memory.wr_enable,1)
            ctx.set(memory.write,1)
            await ctx.tick()
        ctx.set(memory.wr_enable,0)
        await ctx.tick().repeat(10)
        for n in range(24):
            ctx.set(memory.n,n)
            await ctx.tick()
        await ctx.tick().repeat(10)
        # for n in range(24):
        #     ctx.set(memory.n,n)
        #     ctx.set(memory.wr_enable,1)
        #     ctx.set(memory.write,0)
        #     await ctx.tick().repeat(1)

    sim = Simulator(memory)
    sim.add_clock(period=8.33e-8)
    sim.add_testbench(testbench)
    with sim.write_vcd("memory.vcd"):
        sim.run()