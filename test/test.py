import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
import os
os.environ["COCOTB_RESOLVE_X"] = "ZERO"

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start test")

    # Simulated 100 kHz system clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset sequence
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1

    # Set enable = 1, reset = 0, clk = 1 in ui_in[7:5]
    dut.ui_in.value = 0b11100000

    # Simulate 60 seconds (should increment mm from 00 to 01)
    # Each second = 10 clk cycles (BCD-encoded seconds)
    await ClockCycles(dut.clk, 600)

    # Read results
    pm = (dut.uo_out.value >> 7) & 0x1
    hh = dut.uo_out.value.integer & 0x7F
    mm = dut.uio_out.value.integer

    dut._log.info(f"HH={hh:02X}, MM={mm:02X}, PM={pm}")

    # Assert that minutes incremented to 0x01
    assert mm == 0x01, f"Expected MM=0x01 after 60s, got {mm:02X}"
    assert hh == 0x12, f"Expected HH=0x12 (12h), got {hh:02X}"
    assert pm == 0, "Expected AM (PM=0)"

    # Simulate one full hour (60 * 10 = 600 seconds = 6000 cycles)
    await ClockCycles(dut.clk, 6000)

    mm = dut.uio_out.value.integer
    hh = dut.uo_out.value.integer & 0x7F
    pm = (dut.uo_out.value >> 7) & 0x1

    dut._log.info(f"After 1 hour: HH={hh:02X}, MM={mm:02X}, PM={pm}")
    assert mm == 0x00, "Minutes should roll back to 0"
    assert hh == 0x01, "Hour should increment to 01"
