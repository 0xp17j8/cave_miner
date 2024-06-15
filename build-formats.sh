#!/bin/bash

ksc ./cave_miner/formats/elf.ksy -t python --outdir ./cave_miner/formats/ --python-package cave_miner.formats
ksc ./cave_miner/formats/mach_o.ksy -t python --outdir ./cave_miner/formats/ --python-package cave_miner.formats
ksc ./cave_miner/formats/pe.ksy -t python --outdir ./cave_miner/formats/ --python-package cave_miner.formats
