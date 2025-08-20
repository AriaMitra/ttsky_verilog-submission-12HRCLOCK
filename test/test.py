# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Create a 100 kHz clock on dut.clk (10us period)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.ena.value = 1
    dut.rst_n.value = 0

    # Apply reset
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1

    # Enable the design (set ena and clk from ui_in)
    dut.ui_in.value = 0b11100000  # ui_in[7] = clk, [6] = reset, [5] = ena

    # Wait a few cycles to let time pass
    await ClockCycles(dut.clk, 6000)  # simulate 6000 cycles = 1 minute

    # Read outputs
    pm_bit = dut.uo_out.value.integer >> 7
    hh_bcd = dut.uo_out.value.integer & 0x7F
    mm_bcd = dut.uio_out.value.integer

    dut._log.info(f"Time: HH={hh_bcd:02X} MM={mm_bcd:02X} PM={pm_bit}")

    # Example assertion: expect time to have incremented from 12:00:00 to 12:01:00
    assert mm_bcd >= 0x01, "Minutes should have incremented"
    assert hh_bcd == 0x12, "Hour should still be 12"
    assert pm_bit == 0, "Should still be AM"

    # Optional: Wait more time and check PM transition
    await ClockCycles(dut.clk, 3600 * 12 * 10)  # Simulate 12 hours (~432,000 cycles)

    pm_bit = dut.uo_out.value.integer >> 7
    hh_bcd = dut.uo_out.value.integer & 0x7F
    mm_bcd = dut.uio_out.value.integer

    dut._log.info(f"After 12 hours: HH={hh_bcd:02X} MM={mm_bcd:02X} PM={pm_bit}")
    assert pm_bit == 1, "Should be PM after 12 hours"

