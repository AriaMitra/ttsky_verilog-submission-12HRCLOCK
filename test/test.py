# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import os
os.environ["COCOTB_RESOLVE_X"] = "ZERO"  # Treat 'x' as 0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Starting test for AriaMitraClock")

    # Start system clock (100kHz = 10us period)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Step 1: Apply reset (ui_in[6] = 1)
    dut.ena.value = 1
    dut.ui_in.value = 0b01000000  # Reset=1
    await ClockCycles(dut.clk, 5)

    # Step 2: Release reset and enable internal clock logic
    dut.ui_in.value = 0b11100000  # clk=1, reset=0, ena=1
    await ClockCycles(dut.clk, 1)

    # Step 3: Let the clock run for 60 seconds = 600 clock cycles
    await ClockCycles(dut.clk, 600)

    # Step 4: Check outputs (hh, mm, pm)
    hh_raw = dut.uo_out.value.integer
    mm_raw = dut.uio_out.value.integer

    pm = (hh_raw >> 7) & 1
    hh = hh_raw & 0x7F  # Extract hh[6:0]

    dut._log.info(f"⏱️ Time after 60s: HH = {hh:02X}, MM = {mm_raw:02X}, PM = {pm}")

    # Step 5: Assertions
    assert mm_raw == 0x00, f"Expected MM = 0x01 after 60s, got {mm_raw:02X}"
    assert hh == 0x12, f"Expected HH = 0x12 after 60s, got {hh:02X}"
    assert pm == 0, "Expected PM = 0 (AM) after 60s"

    dut._log.info("Test passed: Minute incremented correctly after 60s")
