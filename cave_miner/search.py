from utils import *
from formats import * 
from struct import *

def search_cave(name, body, cave_size, file_offset, vaddr, infos=""):
  null_count = 0

  for offset in xrange(len(body)):
    byte = body[offset]

    if byte == "\x00":
      null_count += 1
    else:
      if null_count >= cave_size:
        print "{}[*]{} New cave detected !{}".format(Bcolors.YELLOW, Bcolors.BOLD, Bcolors.ENDC)
        print "  section_name: {}".format(name)
        print "  cave_begin:   0x{:08x}".format(file_offset + offset - null_count)
        print "  cave_end:     0x{:08x}".format(file_offset + offset)
        print "  cave_size:    0x{:08x}".format(null_count)
        print "  vaddress:     0x{:08x}".format(vaddr + offset - null_count)
        print "  infos:        {}".format(infos)
        print

      null_count = 0

def parse_macho_flags(byte):
  ret = []

  if 0x1 & byte == 0x1: ret.append("READ")
  if 0x2 & byte == 0x2: ret.append("WRITE")
  if 0x4 & byte == 0x4: ret.append("EXECUTE")

  return ", ".join(ret)

def parse_sh_flags(byte):
  ret = []

  if 0x1 & byte == 0x1: ret.append("SHF_WRITE")
  if 0x2 & byte == 0x2: ret.append("SHF_ALLOC")
  if 0x4 & byte == 0x4: ret.append("SHF_EXECINSTR")
  if 0x10 & byte == 0x20: ret.append("SHF_MERGE")
  if 0x20 & byte == 0x20: ret.append("SHF_STRINGS")
  if 0x40 & byte == 0x40: ret.append("SHF_INFO_LINK")
  if 0x80 & byte == 0x80: ret.append("SHF_LINK_ORDER")
  if 0x100 & byte == 0x100: ret.append("SHF_OS_NONCONFORMING")
  if 0x200 & byte == 0x200: ret.append("SHF_GROUP")
  if 0x400 & byte == 0x400: ret.append("SHF_TLS")
  if 0xff00000 & byte == 0xff00000: ret.append("SHF_MASKOS")

  return ", ".join(ret)

def parse_pe_flags(byte):
  ret = []

  if 0x00008 & byte == 0x00008: ret.append("IMAGE_SCN_TYPE_NO_PAD")
  if 0x00020 & byte == 0x00020: ret.append("IMAGE_SCN_CNT_CODE")
  if 0x00040 & byte == 0x00040: ret.append("IMAGE_SCN_CNT_INITIALIZED_DATA")
  if 0x00080 & byte == 0x00080: ret.append("IMAGE_SCN_CNT_UNINITIALIZED_DATA")
  if 0x00100 & byte == 0x00100: ret.append("IMAGE_SCN_LNK_OTHER")
  if 0x00200 & byte == 0x00200: ret.append("IMAGE_SCN_LNK_INFO")
  if 0x00800 & byte == 0x00800: ret.append("IMAGE_SCN_LNK_REMOVE")
  if 0x01000 & byte == 0x01000: ret.append("IMAGE_SCN_LNK_COMDAT")
  if 0x04000 & byte == 0x04000: ret.append("IMAGE_SCN_NO_DEFER_SPEC_EXC")
  if 0x08000 & byte == 0x08000: ret.append("IMAGE_SCN_GPREL")
  if 0x20000 & byte == 0x20000: ret.append("IMAGE_SCN_MEM_PURGEABLE")
  if 0x40000 & byte == 0x40000: ret.append("IMAGE_SCN_MEM_LOCKED")
  if 0x80000 & byte == 0x80000: ret.append("IMAGE_SCN_MEM_PRELOAD")

  return ", ".join(ret)

def search_pe(filename, cavesize):
  g = MicrosoftPe.from_file(filename)

  for section in g.sections:
    section_offset = section.pointer_to_raw_data
    infos = parse_pe_flags(section.characteristics)
    search_cave(section.name, section.body, cavesize, section_offset, section.virtual_address, infos)

def search_macho(filename, cavesize):
  g = MachO.from_file(filename)

  for command in g.load_commands:
    if command.type == MachO.LoadCommandType.segment_64:
      for section in command.body.sections:
        if isinstance(section.data, str):
          infos = "init: [{}], max: [{}]".format(parse_macho_flags(command.body.initprot), parse_macho_flags(command.body.maxprot))
          search_cave("{}.{}".format(section.seg_name, section.sect_name), section.data, cavesize, section.offset, section.addr, infos)

def search_elf(filename, cavesize):
  g = Elf.from_file(filename)

  for section in g.header.section_headers:
    infos = parse_sh_flags(section.flags)
    search_cave(section.name, section.body, cavesize, section.offset, section.addr, infos)

def detect_type(filename, cavesize):
  data = open(filename, "rb").read()

  mz    = "MZ"
  elf   = "\x7FELF"
  macho = pack("I", 0xfeedfacf)

  if   data[0x0:0x2] == mz:    search_pe(filename, cavesize)
  elif data[0x0:0x4] == elf:   search_elf(filename, cavesize)
  elif data[0x0:0x4] == macho: search_macho(filename, cavesize)

def search(filename, cavesize):
  print "{}[*]{} Starting cave mining process...{}".format(Bcolors.YELLOW, Bcolors.BOLD, Bcolors.ENDC)
  print

  detect_type(filename, parse_int(cavesize))

  print "{}[*]{} Mining finished.{}".format(Bcolors.YELLOW, Bcolors.BOLD, Bcolors.ENDC)