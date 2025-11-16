#!/bin/bash

# The BSP_MSP_DIR variable should use an *absolute path* to the SDK's msp/out directory (adjust according to your environment)
# Example: /absolute/path/to/sdk/msp/out

# Change build_dir to the desired build directory name
build_dir=build
echo "build dir: ${build_dir}"
mkdir ${build_dir}
cd ${build_dir}

bsp_url="https://github.com/ZHEQIUSHUI/assets/releases/download/ax_3.6.2/msp_3.6.2.zip"
if [ ! -d "msp_3.6.2" ]; then
    echo "Downloading bsp from ${bsp_url}"
    if [ ! -f "msp_3.6.2.zip" ]; then
        wget ${bsp_url}
    fi
    unzip msp_3.6.2.zip
fi

BSP_MSP_DIR=$PWD/msp_3.6.2/out/
echo "bsp dir: ${BSP_MSP_DIR}"
# The script will perform a simple check to ensure the BSP path is correct
if [ ! -d "${BSP_MSP_DIR}" ]; then
    echo "Error: ${BSP_MSP_DIR} is not a directory"
    exit 1
fi

if [ ! -f "${BSP_MSP_DIR}/lib/libax_sys.so" ]; then
    echo "Error: ${BSP_MSP_DIR}/lib/libax_sys.so is not a file"
    exit 1
fi

# If download fails, you can download the file manually and place it into $build_dir, then extract as shown below
URL="https://developer.arm.com/-/media/Files/downloads/gnu-a/9.2-2019.12/binrel/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu.tar.xz"
FOLDER="gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu"

aarch64-none-linux-gnu-gcc -v
if [ $? -ne 0 ]; then
    # Check if the file exists
    if [ ! -f "$FOLDER.tar.xz" ]; then
        # Download the file
        echo "Downloading $URL"
        wget "$URL" -O "$FOLDER.tar.xz"
    fi

    # Check if the folder exists
    if [ ! -d "$FOLDER" ]; then
        # Extract the file
        echo "Extracting $FOLDER.tar.xz"
        tar -xf "$FOLDER.tar.xz"
    fi

    export PATH=$PATH:$PWD/$FOLDER/bin/
    aarch64-none-linux-gnu-gcc -v
    if [ $? -ne 0 ]; then
        echo "Error: aarch64-none-linux-gnu-gcc not found"
        exit 1
    fi
fi

# Start build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=./install -DBSP_MSP_DIR=${BSP_MSP_DIR} -DCMAKE_TOOLCHAIN_FILE=../toolchains/aarch64-none-linux-gnu.toolchain.cmake ..
make -j16
make install