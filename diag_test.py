import time
import asyncio
import logging
import struct

import can
from can import BusABC, Message
from uds.client import Client
import aioisotp
from udsoncan.configs import default_client_config
from udsoncan import AsciiCodec, DidCodec

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


SEEDMASK = 0x80000000
UNLOCKKEY = 0x00000000
UNLOCKSEED = 0x00000000
UNDEFINESEED = 0xffffffff
SHIFTBIT = 1
ALGORITHMASK = 0x521025A0


def seed_to_key(seed):
    key = 0
    if seed != 0:
        for _ in range(35):
            if seed & SEEDMASK:
                seed = seed << SHIFTBIT
                seed = seed ^ ALGORITHMASK
            else:
                seed = seed << SHIFTBIT
        key = seed

    return key & 0xffffffff


class BCDCodec(DidCodec):

    def __init__(self, data_len=None):
        if data_len is None:
            raise ValueError(
                "You must provide a data length to the BCDCodec")
        self.data_len = data_len

    def encode(self, data_bytes):
        if len(data_bytes) != self.data_len:
            raise ValueError('Data must be %d long' % self.data_len)
        return data_bytes

    def decode(self, data_bytes):
        if len(data_bytes) != self.data_len:
            raise ValueError('Trying to decode a string of %d bytes but codec expects %d bytes' % (
                len(data_bytes), self.data_len))
        return ''.join([f'{i:02x}' for i in data_bytes])

    def __len__(self):
        return self.data_len


async def Test_0x10(client: Client):

    # DiagnositicSessionControl
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])


async def Test_0x11(client: Client):

    # ECUReset
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.ecu_reset(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.ecu_reset(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.ecu_reset(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)

    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.ecu_reset(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.ecu_reset(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.ecu_reset(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)


async def Test_0x14(client: Client):

    # ClearDiagnosticInformation
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.clear_dtc()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.clear_dtc()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.clear_dtc()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    await asyncio.sleep(0.5)


async def Test_0x19(client: Client):

    # ReadDTCInformation
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.get_dtc_by_status_mask(9)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.get_supported_dtc()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.get_dtc_by_status_mask(9)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.get_supported_dtc()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.get_dtc_by_status_mask(9)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.get_supported_dtc()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])


async def Test_0x22(client: Client):

    # ReadDataByIdentifier
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.read_data_by_identifier(0xf180)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf180])

    response = await client.read_data_by_identifier(0xf187)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf187])

    response = await client.read_data_by_identifier(0xf188)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf188])

    response = await client.read_data_by_identifier(0xf18A)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf18A])

    response = await client.read_data_by_identifier(0xf191)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf191])

    response = await client.read_data_by_identifier(0xf199)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf199])

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.read_data_by_identifier(0xf180)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf180])

    response = await client.read_data_by_identifier(0xf187)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf187])

    response = await client.read_data_by_identifier(0xf188)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf188])

    response = await client.read_data_by_identifier(0xf18A)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf18A])

    response = await client.read_data_by_identifier(0xf191)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf191])

    response = await client.read_data_by_identifier(0xf199)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf199])

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.read_data_by_identifier(0xf180)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf180])

    response = await client.read_data_by_identifier(0xf187)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf187])

    response = await client.read_data_by_identifier(0xf188)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf188])

    response = await client.read_data_by_identifier(0xf18A)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf18A])

    response = await client.read_data_by_identifier(0xf191)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf191])

    response = await client.read_data_by_identifier(0xf199)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf199])


async def Test_0x2e(client: Client):

    # WriteDataByIdentifier
    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.request_seed(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    seed = struct.unpack('>I', response.service_data.seed)[0]
    key = seed_to_key(seed)
    response = await client.send_key(4, struct.pack('>I', key))
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.write_data_by_identifier(0xf199, bytes([0x20, 0x20, 0x09, 0x01]))
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.read_data_by_identifier(0xf199)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    logger.debug(response.service_data.values[0xf199])


async def Test_0x27(client: Client):

    # SecurityAccess
    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.request_seed(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    seed = struct.unpack('>I', response.service_data.seed)[0]
    key = seed_to_key(seed)
    response = await client.send_key(4, struct.pack('>I', key))
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.request_seed(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    seed = struct.unpack('>I', response.service_data.seed)[0]
    key = seed_to_key(seed)
    response = await client.send_key(4, struct.pack('>I', key))
    logger.debug([f'0x{i:02x}' for i in response.original_payload])


async def Test_0x28(client: Client):

    # CommunicationControl
    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.communication_control(3, 1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.communication_control(0, 1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.communication_control(3, 1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.communication_control(0, 1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])


async def Test_0x3e(client: Client):

    # TesterPresent
    response = await client.change_session(1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.tester_present()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.tester_present(True)

    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.tester_present()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.tester_present(True)

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.tester_present()
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    response = await client.tester_present(True)


async def Test_0x85(client: Client):

    # ControlDTCSetting
    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.control_dtc_setting(2)  # off
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.control_dtc_setting(1)  # on
    logger.debug([f'0x{i:02x}' for i in response.original_payload])


async def Test_0x31(client: Client):

    # RoutineControl
    response = await client.change_session(2)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.request_seed(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    seed = struct.unpack('>I', response.service_data.seed)[0]
    key = seed_to_key(seed)
    response = await client.send_key(4, struct.pack('>I', key))
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.routine_control(0x1830, 1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.change_session(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.request_seed(3)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])
    seed = struct.unpack('>I', response.service_data.seed)[0]
    key = seed_to_key(seed)
    response = await client.send_key(4, struct.pack('>I', key))
    logger.debug([f'0x{i:02x}' for i in response.original_payload])

    response = await client.routine_control(0x1830, 1)
    logger.debug([f'0x{i:02x}' for i in response.original_payload])


async def diag_test(bus: BusABC):

    config = dict(default_client_config)
    config['data_identifiers'] = {
        0xF180: AsciiCodec(32),
        0xF187: AsciiCodec(13),
        0xF188: AsciiCodec(13),
        0xF18A: AsciiCodec(3),
        0xF191: AsciiCodec(10),
        0xF199: BCDCodec(4),
    }

    network = aioisotp.ISOTPNetwork(bus=bus, tx_padding=0x00)
    with network.open():

        reader, writer = await network.open_connection(RX_ID, TX_ID)
        client = Client(reader, writer, config)

        await Test_0x10(client)
        await Test_0x11(client)
        await Test_0x14(client)
        await Test_0x19(client)
        await Test_0x22(client)
        await Test_0x2e(client)
        await Test_0x27(client)
        await Test_0x28(client)
        await Test_0x3e(client)
        await Test_0x85(client)
        await Test_0x31(client)

        reader, writer = await network.open_connection(RX_ID, FN_ID)
        client = Client(reader, writer, config)

        await Test_0x10(client)
        await Test_0x14(client)
        await Test_0x28(client)
        await Test_0x3e(client)
        await Test_0x85(client)


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
    asyncio.run(diag_test(bus))
    t2 = time.time()
    logger.debug(f'finished in {t2 - t1:.2f}s')

    # bus.shutdown()
