import pytest

from subtools import mtcommand, config, mock_subreflector, process_message


@pytest.fixture(scope="module")
def mock_connection():

    mock_sr = mock_subreflector.Receiver()
    mock_sr.create_socket()
    
    yield (mock_sr)

    mock_sr.shutdown()
    print('killed mock_sr')

@pytest.fixture(scope="module")
def mt():
    mt = mtcommand.MTCommand()
    return (mt)

# # # # # # # # HELPER FUNCTIONS # # # # # # # #
def assert_hxpd_values(mt, fashion,
                       mode_lin=0, xlin=0.0, ylin=0.0, zlin=0.0, vlin=0.0,
                       mode_rot=0, xrot=0.0, yrot=0.0, zrot=0.0, vrot=0.0):

    assert isinstance(mt.structure, process_message.HexapodStructure)
    assert mt.structure.command == 101
    assert mt.structure.fashion == fashion
    assert mt.structure.mode_lin == mode_lin
    assert mt.structure.anzahl_lin == 0
    assert mt.structure.phase_lin == 0
    assert mt.structure.p_xlin == xlin
    assert mt.structure.p_ylin == ylin
    assert mt.structure.p_zlin == zlin
    assert mt.structure.v_lin == vlin
    assert mt.structure.mode_rot == mode_rot
    assert mt.structure.anzahl_rot == 0
    assert mt.structure.phase_rot == 0
    assert mt.structure.p_xrot == xrot
    assert mt.structure.p_yrot == yrot
    assert mt.structure.p_zrot == zrot
    assert mt.structure.v_rot == vrot
    assert mt.mt_command_status == "sent successfully"
    
def assert_asf_values(mt, mode, offset_dr_nr, offset_active):
    assert isinstance(mt.structure, process_message.AsfStructure)
    assert mt.structure.command == 100
    assert mt.structure.mode == mode
    assert mt.structure.offset_dr_nr == offset_dr_nr
    assert mt.structure.offset_active ==  offset_active
    # Rest are all set to 0 since they've been unused during current development
    assert mt.structure.offset_value1 == 0
    assert mt.structure.offset_value2 == 0
    assert mt.structure.offset_value3 == 0
    assert mt.structure.offset_value4 == 0
    assert mt.structure.offset_value5 == 0
    assert mt.structure.offset_value6 == 0
    assert mt.structure.offset_value7 == 0
    assert mt.structure.offset_value8 == 0
    assert mt.structure.offset_value9 == 0
    assert mt.structure.offset_value10 == 0
    assert mt.structure.offset_value11 == 0
    assert mt.mt_command_status == "sent successfully"


# # # # # # # #  TEST CLASS  # # # # # # # #
@pytest.mark.usefixtures("mock_connection")
class TestMTCommand:

    def test_init(self, mt):
        assert mt.structure is None
        assert mt.mt_command_status is None
        assert mt.startflag == 0x1DFCCF1A
        assert mt.endflag == 0xA1FCCFD1
        assert mt.seconds == 10001
        assert mt.servertype[0] == '' or config.SR_IP
        assert mt.servertype[1] == config.SR_WRITE_PORT

    def test_get_server_address(self, mt):
        mt.get_server_address(True)
        assert mt.servertype == ('', config.SR_WRITE_PORT)

        mt.get_server_address(False)
        assert mt.servertype == (config.SR_IP, config.SR_WRITE_PORT)

    def test_send_command(self, mt):

        # Sets up the mtcommand socket
        mt.get_server_address(True)
        mt.start_mtcommand()

        # Sends a command, checking if mt_command_status was correct (proves mt_command_status was sent)
        mt.send_command(b"Hello World")
        assert mt.mt_command_status == "sent successfully"

    def test_interlock_command_to_struct(self, mt):
        full_command = 106, 2000, 42, 0

        try:
            # create the ctypes struct
            mt.interlock_command_to_struct(full_command)

        except Exception as E:
            raise E

        else:
            assert mt.structure.start_flag == 503107354
            assert mt.structure.message_length == 36
            assert mt.structure.command_serial_number == 10001
            assert mt.structure.command == 106
            assert mt.structure.mode == 2000
            assert mt.structure.elevation == 42
            assert mt.structure.reserved == 0
            assert mt.structure.end_flag == 2717700049

    def test_asf_command_to_struct(self, mt):

        # Setup values for mock structure
        command, mode, offset_dr_nr = 100, 1, 0
        full_command = (command, mode, offset_dr_nr,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        try:
            # create the ctypes struct
            mt.asf_command_to_struct(full_command)

        except Exception as E:
            raise E

        else:
            assert mt.structure.start_flag == 503107354
            assert mt.structure.message_length == 46
            assert mt.structure.command_serial_number == 10001
            assert mt.structure.command == 100
            assert mt.structure.mode == 1
            assert mt.structure.offset_dr_nr == 0
            assert mt.structure.offset_active == 0
            assert mt.structure.offset_value1 == 0
            assert mt.structure.offset_value2 == 0
            assert mt.structure.offset_value3 == 0
            assert mt.structure.offset_value4 == 0
            assert mt.structure.offset_value5 == 0
            assert mt.structure.offset_value6 == 0
            assert mt.structure.offset_value7 == 0
            assert mt.structure.offset_value8 == 0
            assert mt.structure.offset_value9 == 0
            assert mt.structure.offset_value10 == 0
            assert mt.structure.offset_value11 == 0
            assert mt.structure.end_flag == 2717700049

    def test_hexapod_command_to_struct(self, mt):
        full_command = 101, 2, 3, 0, 0, 50, 25, 15, \
                       0, 3, 0, 0, 0.1, 0.2, 0.3, 0

        try:
            # create the ctypes struct
            mt.hxpd_command_to_struct(full_command)

        except Exception as E:
            raise E

        else:
            assert mt.structure.start_flag == 503107354
            assert mt.structure.message_length == 108
            assert mt.structure.command_serial_number == 10001
            assert mt.structure.command == 101
            assert mt.structure.fashion == 2
            assert mt.structure.mode_lin == 3
            assert mt.structure.anzahl_lin == 0
            assert mt.structure.phase_lin == 0
            assert mt.structure.p_xlin == 50
            assert mt.structure.p_ylin == 25
            assert mt.structure.p_zlin == 15
            assert mt.structure.v_lin == 0
            assert mt.structure.mode_rot == 3
            assert mt.structure.anzahl_rot == 0
            assert mt.structure.phase_rot == 0
            assert mt.structure.p_xrot == 0.1
            assert mt.structure.p_yrot == 0.2
            assert mt.structure.p_zrot == 0.3
            assert mt.structure.v_rot == 0
            assert mt.structure.end_flag == 2717700049

    def test_polar_command_to_struct(self, mt):
        full_command = 102, 2000, 42, 0

        try:
            # create the ctypes struct
            mt.polar_command_to_struct(full_command)

        except Exception as E:
            raise E

        else:
            assert mt.structure.start_flag == 503107354
            assert mt.structure.message_length == 36
            assert mt.structure.command_serial_number == 10001
            assert mt.structure.command == 102
            assert mt.structure.mode == 2000
            assert mt.structure.p_soll == 42
            assert mt.structure.v_cmd == 0
            assert mt.structure.end_flag == 2717700049

    def test_can_pack_and_unpack(self, mt):

        try:
            # create the ctypes struct
            full_command = 102, 2000, 42, 0
            mt.interlock_command_to_struct(full_command)

            # Above line sets mt.structure which is how we call it here
            byte_string = mt.pack(mt.structure)
            assert isinstance(byte_string, bytes) # packed successfully

            unpacked = mt.unpack(process_message.InterlockStructure,
                                 byte_string)

            assert unpacked.start_flag == 503107354
            assert unpacked.message_length == 36
            assert unpacked.command_serial_number == 10001
            assert unpacked.command == 102
            assert unpacked.mode == 2000
            assert unpacked.elevation == 42
            assert unpacked.reserved == 0
            assert unpacked.end_flag == 2717700049  # unpacked successfully

        except Exception as E:
            raise E

    def test_encapsulate_command(self, mt):
        mt.mt_command_status = None
        mt.encapsulate_command("interlock", (0, 0, 0, 0))
        assert isinstance(mt.structure, process_message.InterlockStructure)
        assert mt.mt_command_status == "sent successfully"

        mt.mt_command_status = None
        mt.encapsulate_command("asf", (0, 0, 0, 0, 0, 0, 0, 0,
                                       0, 0, 0, 0, 0, 0, 0))
        assert isinstance(mt.structure, process_message.AsfStructure)
        assert mt.mt_command_status == "sent successfully"

        mt.mt_command_status = None
        mt.encapsulate_command("hxpd", (0, 0, 0, 0, 0, 0, 0, 0,
                                        0, 0, 0, 0, 0, 0, 0, 0))
        assert isinstance(mt.structure, process_message.HexapodStructure)
        assert mt.mt_command_status == "sent successfully"

        mt.mt_command_status = None
        mt.encapsulate_command("polar", (0, 0, 0, 0))
        assert isinstance(mt.structure, process_message.PolarStructure)
        assert mt.mt_command_status == "sent successfully"

    """ The rest of these tests cannot test just the method as each method 
    calls encapsulate_command(), so we test that the message is sent, and the
    structure params are correct. Basically a collective of the above tests"""

    # # # # # # # # # # INTERLOCK # # # # # # # # # #
    def test_set_mt_elevation(self, mt):
        mt.set_mt_elevation(40)

        assert mt.structure.command == 106
        assert mt.structure.mode == 2000
        assert mt.structure.elevation == 40
        assert mt.mt_command_status == "sent successfully"

        mt.set_mt_elevation(90)

        assert mt.structure.command == 106
        assert mt.structure.mode == 2000
        assert mt.structure.elevation == 90
        assert mt.mt_command_status == "sent successfully"

    def test_activate_mt(self, mt):
        mt.activate_mt()

        assert mt.structure.command == 106
        assert mt.structure.mode == 2
        assert mt.structure.elevation == 0.0
        assert mt.mt_command_status == "sent successfully"

    def test_deactivate_mt(self, mt):
        mt.deactivate_mt()

        assert mt.structure.command == 106
        assert mt.structure.mode == 1
        assert mt.structure.elevation == 0.0
        assert mt.mt_command_status == "sent successfully"

    # # # # # # # # # # ASF # # # # # # # # # #
    def test_ignore_asf(self, mt):
        mt.ignore_asf()
        assert_asf_values(mt, 0, 1, 0)

    def test_deactivate_asf(self, mt):
        mt.deactivate_asf()
        assert_asf_values(mt, 1, 1, 0)

    def test_rest_pos_asf(self, mt):
        mt.rest_pos_asf()
        assert_asf_values(mt, 6, 1, 0)

    def test_stop_asf(self, mt):
        mt.stop_asf()
        assert_asf_values(mt, 7, 1, 0)

    def test_preset_pos_asf(self, mt):
        mt.preset_pos_asf()
        assert_asf_values(mt, 23, 1, 0)

    def test_set_automatic_asf(self, mt):
        mt.set_automatic_asf()
        assert_asf_values(mt, 42, 1, 0)

    def test_set_offset_asf(self, mt):
        mt.set_offset_asf()
        assert_asf_values(mt, 44, 1, 0)

    def test_acknowledge_error_on_asf(self, mt):
        mt.acknowledge_error_on_asf()
        assert_asf_values(mt, 15, 1, 0)
    # # # # # # # # # # HEXAPOD # # # # # # # # # #
    def test_deactivate_hxpd(self, mt):
        mt.deactivate_hxpd()
        assert_hxpd_values(mt, 1)

    def test_activate_hxpd(self, mt):
        mt.activate_hxpd()
        assert_hxpd_values(mt, 2)

    def test_stop_hxpd(self, mt):
        mt.stop_hxpd()
        assert_hxpd_values(mt, 7)

    def test_interlock_hxpd(self, mt):
        mt.interlock_hxpd()
        assert_hxpd_values(mt, 14)

    def test_acknowledge_error_on_hxpd(self, mt):
        mt.acknowledge_error_on_hxpd()
        assert_hxpd_values(mt, 15)

    @pytest.mark.parametrize(
        "preset_tuple", [(-225, -175, -195, 0.001), (225, 175, 45, 10),
                         (0, 0, 0, 1), (120.14, 53.7, 12.2, 3.5),
                         (0, 0, 0, 1), (1, 143, 35, 4), (-23, -23, -149, 7.4)])
    def test_preset_abs_lin_hxpd(self, mt, preset_tuple):

        xlin, ylin, zlin, vlin = preset_tuple
        mt.preset_abs_lin_hxpd(xlin, ylin, zlin, vlin)
        assert_hxpd_values(mt, 2, 3, xlin, ylin, zlin, vlin)

    @pytest.mark.parametrize(
        "preset_tuple", [(-226, -175, -195, 0.001), (-225, -176, -195, 0.001),
                         (-225, -175, -196, 0.001), (-226, -175, -195, 0.0001),
                         (226, 175, 45, 10), (225, 176, 45, 10),
                         (225, 175, 46, 10), (225, 175, 45, 10.5),])
    def test_preset_abs_lin_hxpd_raise_error(self, mt, preset_tuple):
        mt.mt_command_status = None
        xlin, ylin, zlin, vlin = preset_tuple
        mt.preset_abs_lin_hxpd(xlin, ylin, zlin, vlin)
        assert mt.mt_command_status == "Assertion error, parameters out of range. See manual"

    @pytest.mark.parametrize(
        "preset_tuple", [(-0.95, -0.95, -0.95, 0.000_01),
                         (0.95, 0.95, 0.95, 0.1), (0, 0, 0, 0.1),
                         (0.34, 0.25, 0.67, 0.0345)
                         ])
    def test_preset_abs_rot_hxpd(self, mt, preset_tuple):

        xrot, yrot, zrot, vrot = preset_tuple
        mt.preset_abs_rot_hxpd(xrot, yrot, zrot, vrot)
        assert_hxpd_values(mt, 2, mode_rot=3, xrot=xrot,
                           yrot=yrot, zrot=zrot, vrot=vrot)

    @pytest.mark.parametrize(
        "preset_tuple",
        [(-0.96, -0.95, -0.95, 0.000_01), (-0.95, -0.96, -0.95, 0.000_01),
         (-0.95, -0.95, -0.96, 0.000_01), (-0.95, -0.95, -0.95, 0.000_001),
         (0.96, 0.95, 0.95, 0.1), (0.95, 0.96, 0.95, 0.1),
         (0.95, 0.95, 0.96, 0.1), (0.95, 0.95, 0.95, 0.15), ])
    def test_preset_abs_rot_hxpd_raise_error(self, mt, preset_tuple):
        mt.mt_command_status = None
        xrot, yrot, zrot, vrot = preset_tuple
        mt.preset_abs_rot_hxpd(xrot, yrot, zrot, vrot)
        assert mt.mt_command_status == "Assertion error, parameters out of range. See manual"

    # # # # # # # # # # POLAR # # # # # # # # # #
    def test_ignore_polar(self, mt):
        mt.ignore_polar()

        assert mt.structure.command == 102
        assert mt.structure.mode == 0
        assert mt.structure.p_soll == 0.0
        assert mt.structure.v_cmd == 0.0
        assert mt.mt_command_status == "sent successfully"

    def test_activate_polar(self, mt):
        mt.activate_polar()

        assert mt.structure.command == 102
        assert mt.structure.mode == 2
        assert mt.structure.p_soll == 0.0
        assert mt.structure.v_cmd == 0.0
        assert mt.mt_command_status == "sent successfully"

    def test_deactivate_polar(self, mt):
        mt.deactivate_polar()

        assert mt.structure.command == 102
        assert mt.structure.mode == 1
        assert mt.structure.p_soll == 0.0
        assert mt.structure.v_cmd == 0.0
        assert mt.mt_command_status == "sent successfully"

    def test_stop_polar(self, mt):
        mt.stop_polar()

        assert mt.structure.command == 102
        assert mt.structure.mode == 7
        assert mt.structure.p_soll == 0.0
        assert mt.structure.v_cmd == 0.0
        assert mt.mt_command_status == "sent successfully"

    def test_acknowledge_error_on_polar(self, mt):
        mt.acknowledge_error_on_polar()

        assert mt.structure.command == 102
        assert mt.structure.mode == 15
        assert mt.structure.p_soll == 0.0
        assert mt.structure.v_cmd == 0.0
        assert mt.mt_command_status == "sent successfully"

    def test_preset_abs_polar(self, mt):

        def helper(val1, val2):
            assert mt.structure.command == 102
            assert mt.structure.mode == 3
            assert mt.structure.p_soll == val1
            assert mt.structure.v_cmd == val2
            assert mt.mt_command_status == "sent successfully"

        mt.preset_abs_polar(5, 1)
        helper(5, 1)

        mt.preset_abs_polar(195, 3)
        helper(195, 3)

        mt.preset_abs_polar(-195, 0.000_01)
        helper(-195, 0.000_01)

        mt.preset_abs_polar(100, 1.5)
        helper(100, 1.5)

        mt.preset_abs_polar(123.54, 0.9382)
        helper(123.54, 0.9382)

    def test_preset_rel_polar(self, mt):

        def helper(val1, val2):
            assert mt.structure.command == 102
            assert mt.structure.mode == 4
            assert mt.structure.p_soll == val1
            assert mt.structure.v_cmd == val2
            assert mt.mt_command_status == "sent successfully"

        mt.preset_rel_polar(5, 1)
        helper(5, 1)

        mt.preset_rel_polar(195, 3)
        helper(195, 3)

        mt.preset_rel_polar(-195, 0.000_01)
        helper(-195, 0.000_01)

        mt.preset_rel_polar(100, 1.5)
        helper(100, 1.5)

        mt.preset_rel_polar(123.54, 0.9382)
        helper(123.54, 0.9382)
