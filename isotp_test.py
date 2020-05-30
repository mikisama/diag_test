import time
import asyncio
import logging

import can
from can import BusABC, Message


# create logger
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

# create formatter
fmt = logging.Formatter('"%(pathname)s", line %(lineno)s --- %(message)s')

# add formatter to sh
sh.setFormatter(fmt)

# add sh to logger
logger.addHandler(sh)

# Tester TX ID
TX_ID = 0x72b
# Tester RX ID
RX_ID = 0x73b
# Tester FN ID
FN_ID = 0x7df

# # Tester TX ID
# TX_ID = 0x692
# # Tester RX ID
# RX_ID = 0x693
# # Tester FN ID
# FN_ID = 0x600

N_Bs = 75  # 75ms
N_Cr = 150  # 150ms


def send_can_msg(bus: BusABC, arb_id: int, data: bytes):
    msg = Message(arbitration_id=arb_id, dlc=len(data),
                  is_extended_id=False, data=bytes(data))
    bus.send(msg)


async def recv_can_msg(bus: BusABC, arb_id, data_only=True) -> bytes:
    await asyncio.sleep(0.01)
    for _ in range(20):
        msg: Message = bus.recv(timeout=0.01)
        if msg is not None and msg.arbitration_id == arb_id:
            if data_only:
                return msg.data
            else:
                return msg


async def tp_test_7_1(bus: BusABC):
    # 7.1
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x0f, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # Abort the transmission
    ## send_can_msg(bus, TX_ID, [0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # No response is expected
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_2(bus: BusABC):
    # 7.2
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x0f, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Do not send any consecutive frames (CF)
    ## send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ## send_can_msg(bus, TX_ID, [0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # No response is expected
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_3(bus: BusABC):
    # 7.3
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x0f, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Drop the first consecutive frame (CF)
    ## send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    send_can_msg(bus, TX_ID, [0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # No response is expected
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_4(bus: BusABC):
    # 7.4
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x0f, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Send the first consecutive frame (CF) twice
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    send_can_msg(bus, TX_ID, [0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # No response is expected
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_5(bus: BusABC):
    # 7.5
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Delay the first consecutive frame by Timeout Cr + 100ms
    await asyncio.sleep((N_Cr + 100) / 1000)
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # No response is expected
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_6(bus: BusABC):
    # 7.6
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After the First frame is received
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    # The Tester does not send a Flow Control
    ## send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send a response
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_7(bus: BusABC):
    # 7.7
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After the First frame is received
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    # The Tester delays a Flow Control
    await asyncio.sleep((N_Bs + 100) / 1000)
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # The ECU has to cancel the response
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_8(bus: BusABC):
    # 7.8
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After the First frame is received
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # Tester sends two Flow Controls (FC)
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # The ECU should send a response
    count = (data_len + 7 - 1) // 7
    for i in range(count):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (1 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_9(bus: BusABC):
    # 7.9
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    t1 = time.time()
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    t2 = time.time()
    # check if the Flow control frame from ECU is received within Timeout Bs.
    assert (t2 - t1) * 1000 < N_Bs
    logger.debug([f'0x{i:02x}' for i in response])
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[1] == 0x7f and response[2] == 0x22
    logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_10(bus: BusABC):
    # 7.10
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After the First frame is received
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # Tester verifies that every Consecutive frame is received within TimeoutCr.
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    count = (data_len + 7 - 1) // 7
    for i in range(count):
        t1 = time.time()
        response = await recv_can_msg(bus, RX_ID)
        t2 = time.time()
        assert (t2 - t1) * 1000 < N_Cr
        assert response is not None and response[0] == 0x20 + (1 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_11(bus: BusABC):
    # 7.11
    STMin_values = [1, 10, 20, 30, 40, 50, 60]
    for STmin in STMin_values:
        # Tester sends a request with a response that is longer than one frame
        send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00,
                                  0x00, 0x00, 0x00, 0x00])
        # After the First frame is received
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] & 0xf0 == 0x10
        logger.debug([f'0x{i:02x}' for i in response])
        data_len = (response[0] & 0xf) << 8 | response[1]
        data_len -= 6  # first frame contains 6 bytes data
        # Tester verifies that the time between the Consecutive Frames is not below STMin time. This is tested for STMin values
        timestamps = []
        send_can_msg(bus, TX_ID, [0x30, 0x00, STmin,
                                  0x00, 0x00, 0x00, 0x00, 0x00])
        count = (data_len + 7 - 1) // 7
        for i in range(count):
            response = await recv_can_msg(bus, RX_ID, False)
            timestamps.append(response.timestamp)
            assert response is not None and \
                response.data[0] == 0x20 + (1 + i) % 0x10
            logger.debug([f'0x{i:02x}' for i in response.data])

        ts1 = timestamps[:-1]
        ts2 = timestamps[1:]
        stmin = sum([j - i for i, j in zip(ts1, ts2)]) / len(ts1)
        stmin = stmin * 1000 if stmin < 0.1 else stmin / 1000 # The timestamp unit of VECTOR is seconds and CANALYSTII is microseconds
        assert (stmin - STmin) > 0 and (stmin - STmin) < 2
        logger.debug(f'expected: {STmin}, actually: {stmin}')


async def tp_test_7_12(bus: BusABC):
    # 7.12
    # Tester sends a segmented request to check for a valid STMin time in the ECU Flow control
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    STMin = response[2]
    # The STMin time value must be within 0x00-0x7F or 0xF1-0xF9.
    assert 0 <= STMin and STMin <= 0x7F or 0xF1 <= STMin and STMin <= 0xF9


async def tp_test_7_13(bus: BusABC):
    # 7.13
    # Tester sends a request with a Single frame response.
    send_can_msg(bus, TX_ID, [0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After response is received
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[1] == 0x50 and response[2] == 0x01
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf)
    # check that the datalength of the Single frame is within valid range.
    assert data_len < 8


async def tp_test_7_14(bus: BusABC):
    # 7.14
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After the First frame is received
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    # check that the datalength of the First frame is within valid range.
    assert data_len >= 8
    data_len -= 6  # first frame contains 6 bytes data
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    count = (data_len + 7 - 1) // 7
    for i in range(count):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (1 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_15(bus: BusABC):
    # 7.15
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # After the Flow control
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # the Tester sends a second diagnostic request.
    send_can_msg(bus, TX_ID, [0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must send a diagnostic response for the first request
    count = (data_len + 7 - 1) // 7
    for i in range(count):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (1 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])
    # and must ignore the second request.
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_16(bus: BusABC):
    # 7.16
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # After sending a Flow Control
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # the Tester sends the First frame of a another incomplete request
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must send a diagnostic response for the first request
    count = (data_len + 7 - 1) // 7
    for i in range(count):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (1 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])
    # ECU must not send a response for the First frame
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_17(bus: BusABC):
    # 7.17
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # After the Flow control
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # the Tester sends a Consecutive frame.
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    count = (data_len + 7 - 1) // 7
    for i in range(count):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (1 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])
    # ECU must not send a response for the Consecutive frame
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_18(bus: BusABC):
    # 7.18
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # After sending the Flow control
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # the Tester receives the first Consecutive frame
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] == 0x21
    # and sends another Flow control with status overflow (OVFLW)
    send_can_msg(bus, TX_ID, [0x32, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must send a diagnostic response for the first request
    count = (data_len + 7 - 1) // 7 - 1
    for i in range(count):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (2 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])
    # ECU must not send a response for the Flow control.
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_19(bus: BusABC):
    # 7.19
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # After sending the Flow control
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # the Tester receives the first Consecutive frame
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] == 0x21
    # and sends an unknown frame
    send_can_msg(bus, TX_ID, [0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must send a diagnostic response for the first request
    count = (data_len + 7 - 1) // 7 - 1
    for i in range(count):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (2 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])
    # ECU must not send a response for the unknown frame
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_20(bus: BusABC):
    # 7.20
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Tester sends a segmented request interrupted by a Single frame
    send_can_msg(bus, TX_ID, [0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
    # The ECU must send a response for the second request.
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[1] == 0x50 and response[2] == 0x01
    logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_21(bus: BusABC):
    # 7.21
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Tester sends a First frame of a segmented request.
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x23, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # The ECU must send a response for the second request.
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[1] == 0x7f and response[2] == 0x23
    logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_22(bus: BusABC):
    # 7.22
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Tester sends a segmented request interrupted by a Flow control
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After that the Tester sends the remaining consecutive frames
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU should send a diagnostic response for the request
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[1] == 0x7f and response[2] == 0x22
    logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_23(bus: BusABC):
    # 7.23
    # Tester sends a request that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Tester sends a segmented request interrupted by a unknown frame
    send_can_msg(bus, TX_ID, [0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After that the Tester sends the remaining consecutive frames
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU should send a diagnostic response for the request
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[1] == 0x7f and response[2] == 0x22
    logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_24(bus: BusABC):
    # 7.24
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    # Tester sends a Flow control with status overflow
    send_can_msg(bus, TX_ID, [0x32, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send Consecutive frame(s).
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_25(bus: BusABC):
    # 7.25
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # Tester sends a Flow control with a special Blocksize
    BS = 0x01  # BS can be modified larger if the response is long enough
    send_can_msg(bus, TX_ID, [0x30, BS, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must send the number of Consecutive frames that matches the blocksize.
    for i in range(BS):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (1 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])
    # BS count of CF is received above, so recve nothing
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_26(bus: BusABC):
    # 7.26
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    data_len = (response[0] & 0xf) << 8 | response[1]
    data_len -= 6  # first frame contains 6 bytes data
    # Tester sends a Flow control with Blocksize 0
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must send the complete response.
    count = (data_len + 7 - 1) // 7
    for i in range(count):
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] == 0x20 + (1 + i) % 0x10
        logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_27(bus: BusABC):
    # 7.27
    for sts in range(3, 16):
        # Tester sends a request with a response that is longer than one frame
        send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A,
                                  0x00, 0x00, 0x00, 0x00, 0x00])
        response = await recv_can_msg(bus, RX_ID)
        assert response is not None and response[0] & 0xf0 == 0x10
        logger.debug([f'0x{i:02x}' for i in response])
        # Tester sends a Flow control with an invalid Status value (3-15)
        send_can_msg(bus, TX_ID, [0x30 + sts, 0x00,
                                  0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
        # ECU must not send a response.
        response = await recv_can_msg(bus, RX_ID)
        assert response is None


async def tp_test_7_28(bus: BusABC):
    # 7.28
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    # Tester sends a Flow control with Status value wait (WT)
    send_can_msg(bus, TX_ID, [0x31, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send Consecutive frames
    response = await recv_can_msg(bus, RX_ID)
    assert response is None
    await asyncio.sleep((N_Bs + 100) / 1000)  # make N_Bs timeout
    # After the N_Bs Timeout the Tester sends another Flow control with status continue to send (CTS).
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # Then the tester sends a new request.
    send_can_msg(bus, TX_ID, [0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must send a response for the last request.
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[1] == 0x50 and response[2] == 0x01
    logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_29(bus: BusABC):
    # 7.29
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    # Tester sends a Flow control with a too short CAN-DLC
    send_can_msg(bus, TX_ID, [0x30, 0x00])
    # ECU must not send Consecutive frames
    response = await recv_can_msg(bus, RX_ID)
    assert response is None
    # After that the tester sends a new request
    send_can_msg(bus, TX_ID, [0x02, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must send a response for the last request
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[1] == 0x50 and response[2] == 0x01
    logger.debug([f'0x{i:02x}' for i in response])


async def tp_test_7_30(bus: BusABC):
    # 7.30
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x02, 0x19, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00])
    # After the First frame is received
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x10
    logger.debug([f'0x{i:02x}' for i in response])
    # the Tester sends a functional adressed Flow control
    send_can_msg(bus, FN_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must abort sending of the response.
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_31(bus: BusABC):
    # 7.31
    # Tester sends a Single frame with a data length that is not allowed by the protocol
    send_can_msg(bus, TX_ID, [0x00, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send a response
    response = await recv_can_msg(bus, RX_ID)
    assert response is None

    send_can_msg(bus, TX_ID, [0x08, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_32(bus: BusABC):
    # 7.32
    # Tester sends a Single frame with a CAN-DLC shorter and equal to the transport protocol data length field
    send_can_msg(bus, TX_ID, [0x02, 0x10, 0x01])
    # ECU must not send a response
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_33(bus: BusABC):
    # 7.33
    # Tester sends a First frame with Data length set to 0
    send_can_msg(bus, TX_ID, [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send a response
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_34(bus: BusABC):
    # 7.34
    # Tester sends a request with a response that is longer than one frame
    send_can_msg(bus, TX_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # Tester sends a Consecutive frame with a CAN-DLC shorter or equal to transport protocol data length field
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00])
    # ECU must not send a response
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_35(bus: BusABC):
    # 7.35
    # Tester sends a single unknown frame (N_PCItype > 3)
    send_can_msg(bus, TX_ID, [0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send a response.
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_36(bus: BusABC):
    # 7.36
    # Tester sends a functional adressed First frame
    send_can_msg(bus, FN_ID, [0x10, 0x09, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send a response.
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_37(bus: BusABC):
    # same as 7.2???
    # 7.37
    # Tester sends a incomplete diagnostic request with a First frame
    send_can_msg(bus, TX_ID, [0x10, 0x0f, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00])
    # after the ECU Flow control
    response = await recv_can_msg(bus, RX_ID)
    assert response is not None and response[0] & 0xf0 == 0x30
    logger.debug([f'0x{i:02x}' for i in response])
    # without Consecutive frames.
    ## send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    ## send_can_msg(bus, TX_ID, [0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send a diagnostic response.
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_38(bus: BusABC):
    # 7.38
    # Tester sends a single Consecutive frame
    send_can_msg(bus, TX_ID, [0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send a response.
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test_7_39(bus: BusABC):
    # 7.39
    # Tester sends a single Flow Control
    send_can_msg(bus, TX_ID, [0x30, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00])
    # ECU must not send a response.
    response = await recv_can_msg(bus, RX_ID)
    assert response is None


async def tp_test(bus: BusABC):

    tests = [
        tp_test_7_1,
        tp_test_7_2,
        tp_test_7_3,
        tp_test_7_4,
        tp_test_7_5,
        tp_test_7_6,
        tp_test_7_7,
        tp_test_7_8,
        tp_test_7_9,
        tp_test_7_10,
        tp_test_7_11,
        tp_test_7_12,
        tp_test_7_13,
        tp_test_7_14,
        tp_test_7_15,
        tp_test_7_16,
        tp_test_7_17,
        tp_test_7_18,
        tp_test_7_19,
        tp_test_7_20,
        tp_test_7_21,
        tp_test_7_22,
        tp_test_7_23,
        tp_test_7_24,
        tp_test_7_25,
        tp_test_7_26,
        tp_test_7_27,
        tp_test_7_28,
        tp_test_7_29,
        tp_test_7_30,
        tp_test_7_31,
        tp_test_7_32,
        tp_test_7_33,
        tp_test_7_34,
        tp_test_7_35,
        tp_test_7_36,
        tp_test_7_37,
        tp_test_7_38,
        tp_test_7_39,
    ]

    for test in tests:
        await test(bus)


if __name__ == '__main__':

    bus_config = {
        'interface': 'vector',
        # 'interface': 'canalystii',
        'channel': 0,
        'bitrate': 500000,
        'can_filters': [
            {'can_id': RX_ID, 'can_mask': 0xffffffff}
        ]
    }

    bus = can.interface.Bus(**bus_config)

    # send something to start
    bus.send(Message(arbitration_id=0))
    bus.recv(0.5)
    #######################################################

    t1 = time.time()
    asyncio.run(tp_test(bus))
    t2 = time.time()
    print(f'finished in {t2 - t1:.2f}s')

    bus.shutdown()
