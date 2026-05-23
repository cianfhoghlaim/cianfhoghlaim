#!/bin/bash

# Gets Libero version

dir=$(pwd)
while [[ "$dir" != "/" ]]; do
  for subdir in "$dir"/*/; do
    if [[ $subdir =~ Libero_SoC_v([0-9]+\.[0-9]+)/ ]]; then
      Libero_ver="${BASH_REMATCH[1]}"
      break 2
    fi
  done
  dir=$(dirname "$dir")
done


#Set preferred Libero version here if needed
#Libero_ver=2023.2

echo "Using Libero version:" $Libero_ver

# Check if Libero_ver was set; if not, print an error and exit
if [[ -z "$Libero_ver" ]]; then
  echo "Error: No directory found matching the pattern 'Libero_SoC_vXXXX.Y/'"
  return 1
fi

#===============================================================================
# Edit the following section with the location where the following tools are
# installed if they aren't in the default location:
#   - SoftConsole (SC_INSTALL_DIR)
#   - Libero (LIBERO_INSTALL_DIR)
#   - Licensing daemon for Libero (LICENSE_DAEMON_DIR)
#===============================================================================

export SC_INSTALL_DIR=/home/$USER/Microchip/SoftConsole-v2022.2-RISC-V-747
export LIBERO_INSTALL_DIR=/home/$USER/Microchip/Libero_SoC_v$Libero_ver
export LICENSE_DAEMON_DIR=/home/$USER/Microchip/Linux_Licensing_Daemon
export LICENSE_FILE_DIR=/home/$USER/Microchip/license
export SMARTHLS_INSTALL_DIR=$LIBERO_INSTALL_DIR/SmartHLS-$Libero_ver/SmartHLS

#===============================================================================
# The following was tested on Ubuntu 20.04 with:
#   - Libero 2023.2 and 2024.1
#   - SoftConsole 2022.2
# It was also tested on Ubuntu 22.04 with:
#   - Libero 2024.2
#   - SoftConsole 2022.2
#===============================================================================

#
# SoftConsole
#
export PATH=$PATH:$SC_INSTALL_DIR/riscv-unknown-elf-gcc/bin
export FPGENPROG=$LIBERO_INSTALL_DIR/Libero/bin64/fpgenprog

#
# Libero
#
export PATH=$PATH:$LIBERO_INSTALL_DIR/Libero/bin:$LIBERO_INSTALL_DIR/Libero/bin64
export PATH=$PATH:$LIBERO_INSTALL_DIR/SynplifyPro/bin
export PATH=$PATH:$LIBERO_INSTALL_DIR/ModelSimPro/modeltech/linuxacoem
export PATH=$PATH:$SMARTHLS_INSTALL_DIR/bin
export PATH=$PATH:$SMARTHLS_INSTALL_DIR/swtools/binutils/riscv-gnu-toolchain/bin

export LOCALE=C
export LD_LIBRARY_PATH=/usr/lib/i386-linux-gnu:$LD_LIBRARY_PATH

#
# Libero License daemon
#
export LM_LICENSE_FILE=1702@localhost
export SNPSLMD_LICENSE_FILE=1702@localhost

$LICENSE_DAEMON_DIR/lmgrd -c $LICENSE_FILE_DIR/License.dat -l $LICENSE_FILE_DIR/license.log
