import asyncio

from udsoncan import Response, Request, Dtc, MemoryLocation, services
from udsoncan.exceptions import NegativeResponseException, UnexpectedResponseException, ConfigError
from udsoncan.configs import default_client_config


class Client(object):

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, config=default_client_config):
        self._reader = reader
        self._writer = writer
        self._config = dict(config)

    async def send_request(self, request: Request, suppress_positive_response=False, timeout=None):
        if timeout is None:
            timeout = self._config['request_timeout']

        payload = request.get_payload(suppress_positive_response)
        self._writer.write(payload)

        if suppress_positive_response is False:
            payload = await asyncio.wait_for(self._reader.read(4095), timeout)
            response = Response.from_payload(payload)

            if not response.positive:
                while response.code == Response.Code.RequestCorrectlyReceived_ResponsePending:
                    payload = await asyncio.wait_for(self._reader.read(4095), timeout)
                    response = Response.from_payload(payload)
                else:
                    if not response.positive:
                        raise NegativeResponseException(response)

            return response

    async def send_raw(self, data: bytes, timeout=None) -> bytes:
        self._writer.write(data)
        if timeout is None:
            return None
        else:
            payload = await asyncio.wait_for(self._reader.read(4095), timeout)
            return payload

    async def change_session(self, newsession, suppress_positive_response=False, timeout=None):
        request = services.DiagnosticSessionControl.make_request(newsession)

        response = await self.send_request(request, suppress_positive_response, timeout)

        if response is None:
            return

        services.DiagnosticSessionControl.interpret_response(response)

        if newsession != response.service_data.session_echo:
            raise UnexpectedResponseException(response, 'Response subfunction received from server (0x%02x) does not match the requested subfunction (0x%02x)' % (
                response.service_data.session_echo, newsession))

        return response

    async def request_seed(self, level):
        request = services.SecurityAccess.make_request(
            level, mode=services.SecurityAccess.Mode.RequestSeed)

        response = await self.send_request(request)

        if response is None:
            return

        services.SecurityAccess.interpret_response(
            response, mode=services.SecurityAccess.Mode.RequestSeed)

        expected_level = services.SecurityAccess.normalize_level(
            mode=services.SecurityAccess.Mode.RequestSeed, level=level)
        received_level = response.service_data.security_level_echo

        if expected_level != received_level:
            raise UnexpectedResponseException(
                response, 'Response subfunction received from server (0x%02x) does not match the requested subfunction (0x%02x)' % (received_level, expected_level))

        return response

    async def send_key(self, level, key):
        request = services.SecurityAccess.make_request(
            level, mode=services.SecurityAccess.Mode.SendKey, key=key)

        response = await self.send_request(request)

        if response is None:
            return

        services.SecurityAccess.interpret_response(
            response, mode=services.SecurityAccess.Mode.SendKey)

        expected_level = services.SecurityAccess.normalize_level(
            mode=services.SecurityAccess.Mode.SendKey, level=level)
        received_level = response.service_data.security_level_echo

        if expected_level != received_level:
            raise UnexpectedResponseException(
                response, 'Response subfunction received from server (0x%02x) does not match the requested subfunction (0x%02x)' % (received_level, expected_level))

        return response

    async def tester_present(self, suppress_positive_response=False, timeout=None):
        request = services.TesterPresent.make_request()

        response = await self.send_request(request, suppress_positive_response, timeout)

        if response is None:
            return

        services.TesterPresent.interpret_response(response)

        if request.subfunction != response.service_data.subfunction_echo:
            raise UnexpectedResponseException(response, 'Response subfunction received from server (0x%02x) does not match the requested subfunction (0x%02x)' % (
                response.service_data.subfunction_echo, request.subfunction))

        return response

    async def read_data_by_identifier_first(self, didlist):
        didlist = services.ReadDataByIdentifier.validate_didlist_input(didlist)
        response = await self.read_data_by_identifier(didlist)
        values = response.service_data.values
        if len(values) > 0 and len(didlist) > 0:
            return values[didlist[0]]

    async def read_data_by_identifier(self, didlist):
        didlist = services.ReadDataByIdentifier.validate_didlist_input(didlist)

        request = services.ReadDataByIdentifier.make_request(
            didlist=didlist, didconfig=self._config['data_identifiers'])

        if 'data_identifiers' not in self._config or not isinstance(self._config['data_identifiers'], dict):
            raise AttributeError(
                'Configuration does not contains a valid data identifier description.')

        response = await self.send_request(request)

        if response is None:
            return

        params = {
            'didlist': didlist,
            'didconfig': self._config['data_identifiers'],
            'tolerate_zero_padding': self._config['tolerate_zero_padding']
        }

        try:
            services.ReadDataByIdentifier.interpret_response(
                response, **params)
        except ConfigError as e:
            if e.key in didlist:
                raise
            else:
                raise UnexpectedResponseException(
                    response, "Server returned values for data identifier 0x%04x that was not requested and no Codec was defined for it. Parsing must be stopped." % (e.key))

        set_request_didlist = set(didlist)
        set_response_didlist = set(response.service_data.values.keys())
        extra_did = set_response_didlist - set_request_didlist
        missing_did = set_request_didlist - set_response_didlist

        if len(extra_did) > 0:
            raise UnexpectedResponseException(
                response, "Server returned values for %d data identifier that were not requested. Dids are : %s" % (len(extra_did), extra_did))

        if len(missing_did) > 0:
            raise UnexpectedResponseException(
                response, "%d data identifier values are missing from server response. Dids are : %s" % (len(missing_did), missing_did))

        return response

    async def write_data_by_identifier(self, did, value):
        request = services.WriteDataByIdentifier.make_request(
            did, value, didconfig=self._config['data_identifiers'])

        response = await self.send_request(request)

        if response is None:
            return

        services.WriteDataByIdentifier.interpret_response(response)

        if response.service_data.did_echo != did:
            raise UnexpectedResponseException(response, 'Server returned a response for data identifier 0x%04x while client requested for did 0x%04x' % (
                response.service_data.did_echo, did))

        return response

    async def ecu_reset(self, reset_type, suppress_positive_response=False, timeout=None):
        request = services.ECUReset.make_request(reset_type)

        response = await self.send_request(request, suppress_positive_response, timeout)

        if response is None:
            return

        services.ECUReset.interpret_response(response)

        if response.service_data.reset_type_echo != reset_type:
            raise UnexpectedResponseException(response, 'Response subfunction received from server (0x%02x) does not match the requested subfunction (0x%02x)' % (
                response.service_data.reset_type_echo, reset_type))

        return response

    async def clear_dtc(self, group=0xFFFFFF):
        request = services.ClearDiagnosticInformation.make_request(group)

        response = await self.send_request(request)

        if response is None:
            return

        services.ClearDiagnosticInformation.interpret_response(response)

        return response

    async def start_routine(self, routine_id, data=None):
        response = await self.routine_control(routine_id, services.RoutineControl.ControlType.startRoutine, data)
        return response

    async def stop_routine(self, routine_id, data=None):
        response = await self.routine_control(routine_id, services.RoutineControl.ControlType.stopRoutine, data)
        return response

    async def routine_control(self, routine_id, control_type, data=None):
        request = services.RoutineControl.make_request(
            routine_id, control_type, data=data)

        response = await self.send_request(request)

        if response is None:
            return

        services.RoutineControl.interpret_response(response)

        if control_type != response.service_data.control_type_echo:
            raise UnexpectedResponseException(response, 'Control type of response (0x%02x) does not match request control type (0x%02x)' % (
                response.service_data.control_type_echo, control_type))

        if routine_id != response.service_data.routine_id_echo:
            raise UnexpectedResponseException(response, 'Response received from server (ID = 0x%04x) does not match the requested routine ID (0x%04x)' % (
                response.service_data.routine_id_echo, routine_id))

        return response

    async def communication_control(self, control_type, communication_type, suppress_positive_response=False, timeout=None):
        request = services.CommunicationControl.make_request(
            control_type, communication_type)

        response = await self.send_request(request, suppress_positive_response, timeout)

        if response is None:
            return

        services.CommunicationControl.interpret_response(response)

        if control_type != response.service_data.control_type_echo:
            raise UnexpectedResponseException(response, 'Control type of response (0x%02x) does not match request control type (0x%02x)' % (
                response.service_data.control_type_echo, control_type))

        return response

    async def request_download(self, memory_location, dfi=None):
        response = await self.request_upload_download(services.RequestDownload, memory_location, dfi)
        return response

    async def request_upload(self, memory_location, dfi=None):
        response = await self.request_upload_download(services.RequestUpload, memory_location, dfi)
        return response

    async def request_upload_download(self, service_cls, memory_location, dfi=None):
        dfi = service_cls.normalize_data_format_identifier(dfi)

        if service_cls not in [services.RequestDownload, services.RequestUpload]:
            raise ValueError(
                'Service must either be RequestDownload or RequestUpload')

        if not isinstance(memory_location, MemoryLocation):
            raise ValueError(
                'memory_location must be an instance of MemoryLocation')

        if 'server_address_format' in self._config:
            memory_location.set_format_if_none(
                address_format=self._config['server_address_format'])

        if 'server_memorysize_format' in self._config:
            memory_location.set_format_if_none(
                memorysize_format=self._config['server_memorysize_format'])

        request = service_cls.make_request(
            memory_location=memory_location, dfi=dfi)

        response = await self.send_request(request)

        if response is None:
            return

        service_cls.interpret_response(response)

        return response

    async def transfer_data(self, sequence_number, data=None):
        request = services.TransferData.make_request(sequence_number, data)

        response = await self.send_request(request)

        if response is None:
            return

        services.TransferData.interpret_response(response)

        if sequence_number != response.service_data.sequence_number_echo:
            raise UnexpectedResponseException(response, 'Block sequence number of response (0x%02x) does not match request block sequence number (0x%02x)' % (
                response.service_data.sequence_number_echo, sequence_number))

        return response

    async def request_transfer_exit(self, data=None):
        request = services.RequestTransferExit.make_request(data)

        response = await self.send_request(request)

        if response is None:
            return

        services.RequestTransferExit.interpret_response(response)

        return response

    async def control_dtc_setting(self, setting_type, data=None, suppress_positive_response=False, timeout=None):
        request = services.ControlDTCSetting.make_request(
            setting_type, data=data)

        response = await self.send_request(request, suppress_positive_response, timeout)

        if response is None:
            return

        services.ControlDTCSetting.interpret_response(response)

        if response.service_data.setting_type_echo != setting_type:
            raise UnexpectedResponseException(response, 'Setting type of response (0x%02x) does not match request control type (0x%02x)' % (
                response.service_data.setting_type_echo, setting_type))

        return response

    async def get_dtc_by_status_mask(self, status_mask, timeout=None):
        request = services.ReadDTCInformation.make_request(
            services.ReadDTCInformation.Subfunction.reportDTCByStatusMask, status_mask)

        response = await self.send_request(request, False, timeout)

        if response is None:
            return

        services.ReadDTCInformation.interpret_response(
            response, services.ReadDTCInformation.Subfunction.reportDTCByStatusMask)

        if response.service_data.subfunction_echo != services.ReadDTCInformation.Subfunction.reportDTCByStatusMask:
            raise UnexpectedResponseException(response, 'Echo of ReadDTCInformation subfunction gotten from server(0x%02x) does not match the value in the request subfunction (0x%02x)' % (
                response.service_data.subfunction_echo, services.ReadDTCInformation.Subfunction.reportDTCByStatusMask))

        return response

    async def get_number_of_dtc_by_status_mask(self, status_mask, timeout=None):
        request = services.ReadDTCInformation.make_request(
            services.ReadDTCInformation.Subfunction.reportNumberOfDTCByStatusMask, status_mask)

        response = await self.send_request(request, False, timeout)

        if response is None:
            return

        services.ReadDTCInformation.interpret_response(
            response, services.ReadDTCInformation.Subfunction.reportNumberOfDTCByStatusMask)

        if response.service_data.subfunction_echo != services.ReadDTCInformation.Subfunction.reportNumberOfDTCByStatusMask:
            raise UnexpectedResponseException(response, 'Echo of ReadDTCInformation subfunction gotten from server(0x%02x) does not match the value in the request subfunction (0x%02x)' % (
                response.service_data.subfunction_echo, services.ReadDTCInformation.Subfunction.reportNumberOfDTCByStatusMask))

        return response

    async def get_supported_dtc(self, timeout=None):
        request = services.ReadDTCInformation.make_request(
            services.ReadDTCInformation.Subfunction.reportSupportedDTCs)

        response = await self.send_request(request, False, timeout)

        if response is None:
            return

        services.ReadDTCInformation.interpret_response(
            response, services.ReadDTCInformation.Subfunction.reportSupportedDTCs)

        if response.service_data.subfunction_echo != services.ReadDTCInformation.Subfunction.reportSupportedDTCs:
            raise UnexpectedResponseException(response, 'Echo of ReadDTCInformation subfunction gotten from server(0x%02x) does not match the value in the request subfunction (0x%02x)' % (
                response.service_data.subfunction_echo, services.ReadDTCInformation.Subfunction.reportSupportedDTCs))

        return response
