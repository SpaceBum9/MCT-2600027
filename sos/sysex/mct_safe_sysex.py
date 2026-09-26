"""Pure parser for the virtual MCT_SAFE SysEx v0 protocol. No MIDI I/O."""
from dataclasses import dataclass
from hashlib import sha256

OPS={0x01:("CAPS?","ALLOW_ANALYZE"),0x02:("STATE?","ALLOW_ANALYZE"),0x03:("PATTERN?","ALLOW_ANALYZE"),
0x10:("DIFF","ALLOW_SIMULATE"),0x11:("SIMULATE","ALLOW_SIMULATE"),0x20:("STAGE","DENY_WRITE"),
0x21:("VERIFY","ALLOW_SIMULATE"),0x22:("COMMIT","DENY_WRITE"),0x23:("ROLLBACK","ALLOW_SIMULATE"),
0x70:("FIRMWARE","DENY_WRITE")}
PREFIX=bytes([0xF0,0x7D,0x4D,0x43,0x54])

@dataclass(frozen=True)
class Result:
    verdict:str; operation:str; checksum:str; raw_sha256:str; reason:str

def parse(raw:bytes)->Result:
    digest=sha256(raw).hexdigest()
    def r(v,o="UNKNOWN",c="unknown",why=""): return Result(v,o,c,digest,why)
    if len(raw)<11 or not raw.startswith(PREFIX) or raw[-1]!=0xF7: return r("HOLD_UNKNOWN",why="bad framing/namespace")
    if any(b>0x7F for b in raw[1:-1]): return r("HOLD_UNKNOWN",why="non-7-bit data")
    version,op,flags,length=raw[5:9]
    if version!=0: return r("HOLD_UNKNOWN",why="unsupported version")
    payload=raw[9:-2]; supplied=raw[-2]
    if len(payload)!=length: return r("HOLD_UNKNOWN",why="length mismatch")
    calc=sum(raw[5:-2]) & 0x7F
    if supplied!=calc: return r("HOLD_UNKNOWN",c="invalid",why="checksum mismatch")
    name,verdict=OPS.get(op,("UNKNOWN","HOLD_UNKNOWN"))
    if op not in OPS: return r(verdict,name,"valid","unknown opcode")
    return r(verdict,name,"valid","v0 policy")
