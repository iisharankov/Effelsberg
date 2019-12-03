import pytest

from subtools import mtcommand, config




@pytest.fixture(scope="module")
def mt_class():
    mt = mtcommand.MTCommand()
    return (mt)

@pytest.mark.usefixtures("mt_class")
class TestMTCommand:

    def test_init(self, mt_class):
        mt = mt_class
        assert mt.structure is None
        assert mt.msg is None
        assert mt.startflag == 0x1DFCCF1A
        assert mt.endflag == 0xA1FCCFD1
        assert mt.seconds == 10001
        assert mt.servertype[0] == '' or config.SR_IP
        assert mt.servertype[1] == config.SR_WRITE_PORT

    def test_get_server_address(self, mt_class):
        mt = mt_class
        mock_address = mt.get_server_address(True)
        assert mock_address == ('', config.SR_WRITE_PORT)

        real_address = mt.get_server_address(False)
        assert real_address == (config.SR_IP, config.SR_WRITE_PORT)
