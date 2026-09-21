from mct_safe_sysex import parse

def frame(op,payload=b""):
    core=bytes([0,op,0,len(payload)])+payload
    return bytes([0xF0,0x7D,0x4D,0x43,0x54])+core+bytes([sum(core)&0x7F,0xF7])

def test_read_only(): assert parse(frame(0x01)).verdict=="ALLOW_ANALYZE"
def test_simulate(): assert parse(frame(0x11,b"abc")).verdict=="ALLOW_SIMULATE"
def test_commit_denied_even_valid(): assert parse(frame(0x22)).verdict=="DENY_WRITE"
def test_firmware_denied_even_valid(): assert parse(frame(0x70)).verdict=="DENY_WRITE"
def test_unknown_holds(): assert parse(frame(0x55)).verdict=="HOLD_UNKNOWN"
def test_bad_checksum_holds():
    x=bytearray(frame(0x01)); x[-2]^=1
    assert parse(bytes(x)).verdict=="HOLD_UNKNOWN"
def test_hashes_original():
    x=frame(0x01); assert len(parse(x).raw_sha256)==64
