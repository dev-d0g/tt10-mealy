# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge


@cocotb.test()
async def test_project(dut):
    dut._log.info("Starting D-Latch Test")

    # 100 kHz clock (10 us period)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    #
    # RESET SEQUENCE
    #
    dut._log.info("Applying reset")
    dut.ena.value = 1
    dut.ui_in.value = 0     # D = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    assert dut.uo_out[0].value == 0, "Q must reset to 0"

    #
    # TEST 1: Latch transparent HIGH — Q should follow D
    #
    dut._log.info("Test: Transparent High")

    # Drive D=1 while clk HIGH
    dut.ui_in[0].value = 1

    await RisingEdge(dut.clk)  # clk goes high → transparent region
    await ClockCycles(dut.clk, 1)

    assert dut.uo_out[0].value == 1, "Q should follow D when clk=1"

    #
    # TEST 2: Hold LOW — Q should freeze
    #
    dut._log.info("Test: Hold Mode")

    dut.ui_in[0].value = 0   # Change D while clk is LOW

    await FallingEdge(dut.clk)  # go to hold mode
    await ClockCycles(dut.clk, 1)

    assert dut.uo_out[0].value == 1, "Q should HOLD when clk=0"

    #
    # TEST 3: Change D again → still should not update
    #
    dut.ui_in[0].value = 1
    await ClockCycles(dut.clk, 1)

    assert dut.uo_out[0].value == 1, "Q must remain latched until clk=1"

    #
    # TEST 4: Let clk go HIGH → Q should update now
    #
    dut._log.info("Test: Update after Hold")

    await RisingEdge(dut.clk)  # transparent again
    await ClockCycles(dut.clk, 1)

    assert dut.uo_out[0].value == 1, "Q must update when clk=1"

    dut._log.info("D-Latch Test completed successfully!")
