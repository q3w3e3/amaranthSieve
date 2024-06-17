from amaranth import *

from amaranth_boards.icebreaker import ICEBreakerPlatform

from .sieve2 import TopLevel

def build_icebreaker():
    ICEBreakerPlatform().build(TopLevel())
