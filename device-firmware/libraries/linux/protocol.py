from dataclasses import dataclass

@dataclass
class AttrPacket:
    seq: int = 0
    cmd: int = 0
    attr: int = 0
    val: int = 0


def parse_attr_packet(message: str):
	parts = message.strip().split(',')
	if len(parts) != 4:
		# TODO: raise exception
		return None

	print("Parsing packet:", parts)

	seq = int(parts[0], 16)
	cmd = int(parts[1], 16)
	attr = int(parts[2], 16)
	val = int(parts[3], 16)

	return AttrPacket(seq = seq, cmd = cmd, attr = attr, val = val)


def format_attr_packet(p: AttrPacket):
	return f"{p.seq:04X},{p.cmd:02X},{p.attr:02X},{p.val:08X}"

