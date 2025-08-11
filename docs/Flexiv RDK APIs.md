Flexiv RDK APIs  1.6.0

# Flexiv RDK

Flexiv RDK (Robotic Development Kit), a key component of the Flexiv Robotic Software Platform, is a powerful development toolkit that enables the users to create complex and customized robotic applications using APIs that provide both low-level real-time (RT) and high-level non-real-time (NRT) access to Flexiv robots.

# References

[Flexiv RDK Home Page](https://www.flexiv.com/software/rdk) is the main reference. It contains important information including user manual and API documentation. The instructions below serve as a quick reference, and you can find the full documentation at [Flexiv RDK Manual](https://www.flexiv.com/software/rdk/manual).

# Environment Compatibility

| **OS**          | **Platform** | **C++ compiler kit** | **Python interpreter** |
| --------------------- | ------------------ | -------------------------- | ---------------------------- |
| Linux (Ubuntu 20.04+) | x86_64, arm64      | GCC v9.4+                  | 3.8, 3.10, 3.12              |
| macOS 12+             | arm64              | Clang v14.0+               | 3.10, 3.12                   |
| Windows 10+           | x86_64             | MSVC v14.2+                | 3.8, 3.10, 3.12              |

**IMPORTANT**: You might need to turn off your computer's firewall or whitelist the RDK programs to be able to establish connection with the robot.

# Quick Start - Python

## Install RDK Python library

For all supported platforms, the RDK Python library and its dependencies for a specific version of Python can be installed using its `pip` module:

```
python3.x -m pip install numpy spdlog flexivrdk
```

Replace `3.x` with a specific Python version.

## Use the installed Python library

After the library is installed as `flexivrdk` Python package, it can be imported from any Python script. Test with the following commands in a new Terminal, which should start Flexiv RDK:

```
python3.x
import flexivrdk
robot = flexivrdk.Robot("Rizon4-123456")
```

The program will start searching for a robot with serial number `Rizon4-123456`, and will exit after a couple of seconds if the specified robot is not found in the local network.

## Run example Python scripts

To run an example Python script in this repo:

```
cd flexiv_rdk/example_py
python3.x <example_name>.py [robot_serial_number]
```

For example:

```
python3.10 ./basics1_display_robot_states.py Rizon4-123456
```

# Quick Start - C++

## Prepare build tools

### Linux

1. Install compiler kit using package manager:

   ```
   sudo apt install build-essential
   ```
2. Install CMake using package manager:

   ```
   sudo apt install cmake
   ```

   ### macOS
3. Install compiler kit using `xcode` tool:

   ```
   xcode-select 
   ```

   This will invoke the installation of Xcode Command Line Tools, then follow the prompted window to finish the installation.
4. Install CMake using package manager:

   ```
   brew install cmake
   ```

   ### Windows
5. Install compiler kit: Download and install Microsoft Visual Studio 2019 (MSVC v14.2) or above. Choose "Desktop development with C++" under the Workloads tab during installation. You only need to keep the following components for the selected workload:

   - MSVC ... C++ x64/x86 build tools (Latest)
   - C++ CMake tools for Windows
   - Windows 10 SDK or Windows 11 SDK, depending on your actual Windows version
6. Install CMake: Download `cmake-3.x.x-windows-x86_64.msi` from [CMake download page](https://cmake.org/download/) and install the msi file. The minimum required version is 3.16.3. **Add CMake to system PATH** when prompted, so that `cmake` and `cmake-gui` command can be used from Command Prompt or a bash emulator.
7. Install bash emulator: Download and install [Git for Windows](https://git-scm.com/download/win/), which comes with a bash emulator Git Bash. The following steps are to be carried out in this bash emulator.

## Install RDK C++ library

The following steps are identical on all supported platforms.

1. Choose a directory for installing RDK C++ library and all its dependencies. This directory can be under system path or not, depending on whether you want RDK to be globally discoverable by CMake. For example, a new folder named `rdk_install` under the home directory.
2. In a new Terminal, run the provided script to compile and install all C++ dependencies to the installation directory chosen in step 1:

   ```
   cd flexiv_rdk/thirdparty
   bash build_and_install_dependencies.sh ~/rdk_install
   ```
3. In a new Terminal, configure the flexiv_rdk CMake project:

   ```
   cd flexiv_rdk
   mkdir build && cd build
   cmake .. -DCMAKE_INSTALL_PREFIX=~/rdk_install
   ```

   NOTE:

   ```
   -D
   ```

   followed by

   ```
   CMAKE_INSTALL_PREFIX
   ```

   sets the absolute path of the installation directory, which should be the one chosen in step 1.
4. Install

   ```
   flexiv_rdk
   ```

   C++ library to

   ```
   CMAKE_INSTALL_PREFIX
   ```

   path, which may or may not be globally discoverable by CMake:

   ```
   cd flexiv_rdk/build
   cmake --build . --target install --config Release
   ```

   ## Use the installed C++ library

After the library is installed as `flexiv_rdk` CMake target, it can be linked from any other CMake projects. Using the provided `flexiv_rdk-examples` project for instance:

```
cd flexiv_rdk/example
mkdir build && cd build
cmake .. -DCMAKE_PREFIX_PATH=~/rdk_install
cmake --build . --config Release -j 4
```

NOTE: `-D` followed by `CMAKE_PREFIX_PATH` tells the user project's CMake where to find the installed C++ library. This argument can be skipped if the RDK library and its dependencies are installed to a globally discoverable location.

## Run example C++ programs

To run an example C++ program compiled during the previous step:

```
cd flexiv_rdk/example/build
./<example_name> [robot_serial_number]
```

For example:

```
./basics1_display_robot_states Rizon4-123456
```

NOTE: `sudo` is only required if the real-time scheduler API `flexiv::rdk::Scheduler` is used in the program.

# API Documentation

The complete and detailed API documentation of the **latest release** can be found at https://www.flexiv.com/software/rdk/api. The API documentation of a previous release can be generated manually using Doxygen. For example, on Linux:

```
sudo apt install doxygen-latex graphviz
cd flexiv_rdk
git checkout <previous_release_tag>
doxygen doc/Doxyfile.in
```

The generated API documentation is under `flexiv_rdk/doc/html/` directory. Open any html file with your browser to view it.

## Class List

Here are the classes, structs, unions and interfaces with brief descriptions:

[detail level 123]

| ▼flexiv                                                                                          |                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ▼rdk                                                                                             |                                                                                                                                                                                                                                                                                      |
| [RobotInfo](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_robot_info.html)         | General information about the connected robot                                                                                                                                                                                                                                        |
| [RobotStates](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_robot_states.html)     | Data structure containing the joint- and Cartesian-space robot states                                                                                                                                                                                                                |
| [PlanInfo](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_plan_info.html)           | Data structure containing information of the on-going primitive/plan                                                                                                                                                                                                                 |
| **C**[JPos](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_j_pos.html)        | Data structure representing the customized data type "JPOS" in Flexiv Elements                                                                                                                                                                                                       |
| [Coord](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_coord.html)                  | Data structure representing the customized data type "COORD" in Flexiv Elements                                                                                                                                                                                                      |
| [Device](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_device.html)                 | Interface with the robot device(s)                                                                                                                                                                                                                                                   |
| [FileIO](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_file_i_o.html)               | Interface for file transfer with the robot. The robot must be put into IDLE mode when transferring files                                                                                                                                                                             |
| [GripperParams](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_gripper_params.html) | Data structure containing the gripper parameters                                                                                                                                                                                                                                     |
| [GripperStates](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_gripper_states.html) | Data structure containing the gripper states                                                                                                                                                                                                                                         |
| [Gripper](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_gripper.html)               | Interface with the robot gripper. Because gripper is also a type of device, this API uses the same underlying infrastructure as[rdk::Device](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_device.html), but with functions tailored specifically for gripper controls |
| [Maintenance](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_maintenance.html)       | Interface to carry out robot maintenance operations. The robot must be in IDLE mode when triggering any operations                                                                                                                                                                   |
| [Model](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_model.html)                   | Interface to access certain robot kinematics and dynamics data                                                                                                                                                                                                                       |
| [Robot](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_robot.html)                   | Main interface with the robot, containing several function categories and background services                                                                                                                                                                                        |
| [SafetyLimits](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_safety_limits.html)   | Data structure containing configurable robot safety limits                                                                                                                                                                                                                           |
| [Safety](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_safety.html)                 | Interface to change robot safety settings. The robot must be in IDLE mode when applying any changes. A password is required to authenticate this interface                                                                                                                           |
| [Scheduler](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_scheduler.html)           | Real-time scheduler that can simultaneously run multiple periodic tasks. Parameters for each task are configured independently                                                                                                                                                       |
| [ToolParams](https://www.flexiv.com/software/rdk/api/structflexiv_1_1rdk_1_1_tool_params.html)       | Data structure containing robot tool parameters                                                                                                                                                                                                                                      |
| [Tool](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_tool.html)                     | Interface to online update and interact with the robot tools. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes                                                                                          |
| [WorkCoord](https://www.flexiv.com/software/rdk/api/classflexiv_1_1rdk_1_1_work_coord.html)          | Interface to online update and interact with the robot's work coordinates. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes                                                                             |

Here is a list of all documented class members with links to the class documentation for each member:

---

### - a -

* Add() : [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#a90f5e483f1ddcbbeb0e6c10a6b7d26c2) , [flexiv::rdk::WorkCoord](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_work_coord.html#a37528fc7804cc47d639a31b8ed194a1d)
* AddTask() : [flexiv::rdk::Scheduler](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_scheduler.html#a2a6ce7d7f0b20a7322d2292c3a7ff1c1)
* assigned_plan_name : [flexiv::rdk::PlanInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_plan_info.html#ac91733a0596f2a761fab7256133fcdf9)

### - b -

* Brake() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a3011ee926edc38c5a8b1fa871f73a9b8)
* busy() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#afa605417a7cb3fb748e6c9f0a5964cf2)

### - c -

* C() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a1aac904ea30ff904d23c5a3a7f78a2e1)
* c() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a8c9d6709cbf568909bf258d5bb8bf51d)
* CalibrateJointTorqueSensors() : [flexiv::rdk::Maintenance](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_maintenance.html#adaf43994fb74fee937186af8e133a69e)
* ClearFault() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#af772dc43163badf6bb63a6218c794c4d)
* CoM : [flexiv::rdk::ToolParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_tool_params.html#abc8d660a3ac5735da928888e1c0ceeb3)
* Command() : [flexiv::rdk::Device](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_device.html#a3bc65131576c6d3b6f43488c02d3c162)
* connected() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#aa5aeaf9f6f59ddb3ce0338a33c39c626)
* Coord() : [flexiv::rdk::Coord](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_coord.html#a6a05655e9e55b28a712ee1b6e8c8fc62)
* current_limits() : [flexiv::rdk::Safety](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_safety.html#a8cf795199cda6ae33ff504533778854b)

### - d -

* default_limits() : [flexiv::rdk::Safety](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_safety.html#a1de118eecab8aab69dda5f71697aba3b)
* Device() : [flexiv::rdk::Device](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_device.html#a5dbebfe18361322b559a41168a56024a)
* digital_inputs() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a73d2f20b5743451a8a8f07baf2d7fd0a)
* Disable() : [flexiv::rdk::Device](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_device.html#a97d9a3b516bae39ed258acc4190b2152) , [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#ab01f7b9d8963e0cad8ccd98f6cd2df51)
* dJ() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a2098039e9bce3a69df84be31dfab26a3)
* DoF : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#ab9e5d37f2052b4cca4d0d8c9a171a273)
* dq : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a7ff6b63a7cd63f549e2e842cc316f156)
* dq_e : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a28cad4fc635bed1a504febcb8f67649c)
* dq_max : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#a876fa1640592a862611f76e566334bd4)
* dq_max_normal : [flexiv::rdk::SafetyLimits](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_safety_limits.html#a72adc63caca8b6e9be3bc6ddc67833b3)
* dq_max_reduced : [flexiv::rdk::SafetyLimits](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_safety_limits.html#af7a88358343eebf49e24c583fc283348)
* dtheta : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a1d86ca8b034519e30f8150c7b66e41a9)

### - e -

* Enable() : [flexiv::rdk::Device](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_device.html#a015408140b4c9c94d776f54704ee8aa0) , [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#ab7b3ec7df09c53763ed230633512eb9f) , [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#af15c77d1f0f9ef6141f8b97cf1509d28)
* enabling_button_pressed() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#aacf929b548177d0df1907a72b1aed1df)
* estop_released() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#af89e04f10b65b914b2e4f915c049bfea)
* ExecutePlan() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a01009562046eb85f09abd01bcd9a9a6f)
* ExecutePrimitive() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a45abfb0a498bc89042f1be587ef73025)
* exist() : [flexiv::rdk::Device](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_device.html#af244e2727d42b38b8336a594b7509ddf) , [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#a4cd40eaab3c08b27c3da27811c525e5e) , [flexiv::rdk::WorkCoord](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_work_coord.html#af6d2380629c4d066ef85ef62e34e20b8)
* ext_wrench_in_tcp : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a4fb952caa57a7a09a393b789bdb16e42)
* ext_wrench_in_tcp_raw : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a7020046549f6b241535b30648b4add44)
* ext_wrench_in_world : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a1b8289bece7e5c117205877ee8d8b74d)
* ext_wrench_in_world_raw : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#ab422b5c890dbe530f3b903e3222a486c)

### - f -

* fault() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#af377371e11a8a242127b82466c2b3874)
* FileIO() : [flexiv::rdk::FileIO](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_file_i_o.html#a81f44df3684756c56e44ec8a1be7c02f)
* flange_pose : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#ae184167b05d32314c658c94c9978e3be)
* force : [flexiv::rdk::GripperStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_states.html#a7179829e3bce9bf8d29920a4faf77590)
* ft_sensor_raw : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a05721557ab36109c4d4b17f5237f14e2)

### - g -

* g() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a64319933137806d54fc6d414126325b5)
* global_variables() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a821816a133113446b263a2387d78ea00)
* Grasp() : [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#ae33ec54ff792e6c2b54d31442cb687ce)
* Gripper() : [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#aeda1f1ecb1879314b2550c2fb44ba97b)

### - i -

* inertia : [flexiv::rdk::ToolParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_tool_params.html#aca08d56b73c5046f726f108d80f2d243)
* info() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a4637e5ec1c7d4a612eceeeadbaf3f205)
* Init() : [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#aa250446ea90a0fae7a1a86434022de13)
* is_moving : [flexiv::rdk::GripperStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_states.html#a323e8eb2f8f4dc387e39e2fe4e10170b)

### - j -

* J() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a5ad5cff471e959517c175bb802b037f8)
* JPos() : [flexiv::rdk::JPos](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_j_pos.html#ad6250667721e15e4f3532d577582114e)

### - k -

* K_q_nom : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#aad7c4802118f38805367abc8623933b4)
* K_x_nom : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#a96023a0c08cb7e5fe042570212b15456)

### - l -

* license_type : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#a367ef0e3afb4fc49855a2e0aab113ff9)
* list() : [flexiv::rdk::Device](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_device.html#a053d65405ea1db47943a345ef0e0458c) , [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#a49c59324d02b71c555d29c4b9e6a59b7) , [flexiv::rdk::WorkCoord](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_work_coord.html#a650fc1eef5488d5a6920b3c409d34179)

### - m -

* M() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a24da0bc0e66fb0b793430d679b0d4663)
* Maintenance() : [flexiv::rdk::Maintenance](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_maintenance.html#acb4bc533df5c3ab8f71a67ef3081c059)
* mass : [flexiv::rdk::ToolParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_tool_params.html#a3702c840ee14a1295453899710326c47)
* max_force : [flexiv::rdk::GripperParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_params.html#aaf54269e1aa4a3f89d9df29cbbb0192d)
* max_priority() : [flexiv::rdk::Scheduler](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_scheduler.html#a17483a05e729ee64aed1741541bb4843)
* max_vel : [flexiv::rdk::GripperParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_params.html#a92fdb087c2d84eb48bc7044bc07f5579)
* max_width : [flexiv::rdk::GripperParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_params.html#ac9db37a4f36caf04f944acb4b989d5b2)
* min_force : [flexiv::rdk::GripperParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_params.html#a3edee9390be00f2232fc4cb50a98dcec)
* min_priority() : [flexiv::rdk::Scheduler](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_scheduler.html#a069d26ef2a2f65645798b06d1693a0c3)
* min_vel : [flexiv::rdk::GripperParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_params.html#a8cd53750c1c9b37aac4fad98efaf2b54)
* min_width : [flexiv::rdk::GripperParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_params.html#ac7f62241157e01194582f8cddd542df6)
* mode() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a477d2e65eef81bf810a8f0492e5fcf98)
* Model() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a2c8aa076a2a79481425f0c4fdcac66b2)
* model_name : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#a99bc2bfaa702ceaa7a75df6162c0999e)
* Move() : [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#aa034dfcfc37cfbfa1110031e7229a63b)
* mu_log() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a8080dd3e3c654820a68e4e34c5627ca5)

### - n -

* name : [flexiv::rdk::GripperParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_params.html#a87b8f2d00eea4e226ea2ccf3b2c64169) , [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#ad49965a0b43380d380bfbbe54a364407)
* node_name : [flexiv::rdk::PlanInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_plan_info.html#a1d42593d0bb46b2e57a351b76bc56bdd)
* node_path : [flexiv::rdk::PlanInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_plan_info.html#a756bf283df5c2cae6a853cb3a7c61782)
* node_path_number : [flexiv::rdk::PlanInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_plan_info.html#ad6e383df9414d7abc8c86ec7b39615c1)
* node_path_time_period : [flexiv::rdk::PlanInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_plan_info.html#a1d8cd3250aa3cdb7919a61de4f579cdf)
* num_tasks() : [flexiv::rdk::Scheduler](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_scheduler.html#a905ac761cf49ed52ccd478b1a488182c)

### - o -

* operational() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a4c614be4e7852f11521c459ba80b618e)
* operational_status() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a3413da28ed8e49771778845a9aa241a9)
* orientation : [flexiv::rdk::Coord](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_coord.html#a1034eccd0b826b10de7f874e2b38b89d)

### - p -

* params() : [flexiv::rdk::Device](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_device.html#a9ae18b6cbdadb47b21234cebf072176e) , [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#ab667b28bfe4bae5f6da1378afb541cd8) , [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#a6df53e07a72f4ec10fe5d9ed3024ad31)
* PausePlan() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a6c6724989a5f5df7b08e92764da2b276)
* plan_info() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#ae504eca3b5308443a3fca27e104f21b7)
* plan_list() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a17d5e3381f29a54ff3f0a76a8d3dd922)
* pose() : [flexiv::rdk::WorkCoord](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_work_coord.html#a47a76a59007b0b6936327c24fb633934)
* position : [flexiv::rdk::Coord](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_coord.html#a87170a117686b68e305d74b60ded208c)
* primitive_states() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#abf69439fbb018e09b32f1a282ac481dc)
* pt_name : [flexiv::rdk::PlanInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_plan_info.html#abba8e403699f34710b30d8c02c2ce482)

### - q -

* q : [flexiv::rdk::JPos](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_j_pos.html#a429899e8e58b7b5b9020cf92b909ddfe) , [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a21dec8a4f337c1c791caf9a450cc371e)
* q_e : [flexiv::rdk::JPos](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_j_pos.html#af9ff997aad0fda34520e6c34f2d31a78) , [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a40027b9eee706ad877e68b5660dd29e4)
* q_max : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#a2ff0ea9512a1af01803d38100aee9b82) , [flexiv::rdk::SafetyLimits](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_safety_limits.html#ab247cb84351adf7b783773174205fc49)
* q_min : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#acb3dca6a2a28b71312d4c1731a848047) , [flexiv::rdk::SafetyLimits](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_safety_limits.html#a7f4e354a0a80f33c7d0e8a43f79be3a8)

### - r -

* reachable() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a88e33a1c150fab82831a70097bf6a82c)
* recovery() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a2cbcf90791cbeffa5aa7ce8df79f1369)
* reduced() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a9a89a4c479f2f22efdf4bf42895176ab)
* ref_frame : [flexiv::rdk::Coord](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_coord.html#a7264c8d03a1f90a4e4f8960972d7196e)
* ref_q : [flexiv::rdk::Coord](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_coord.html#a968f41a3803cb3f00472cf9c9c33e67a)
* ref_q_e : [flexiv::rdk::Coord](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_coord.html#aad31370385bf6ba7f2567f88c911915c)
* Reload() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a5781c5ec334cc14835a3df688eb46dc4)
* Remove() : [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#a78f6f20d3ef11fb97bc2f3a489f3b55a) , [flexiv::rdk::WorkCoord](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_work_coord.html#a86962d6b5c25cb9d694879d33bd6f7a1)
* Robot() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a745fad45f76a11dcb97b4bc3a97070db)
* RunAutoRecovery() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#afb5c2bc93f081a3246e29f2c42e1a882)

### - s -

* Safety() : [flexiv::rdk::Safety](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_safety.html#a47d1a51cd9ef2e5c219b02f9caca4625)
* safety_inputs() : [flexiv::rdk::Safety](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_safety.html#a05bba5c1ecd58af143d1d1e4bedf0339)
* Scheduler() : [flexiv::rdk::Scheduler](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_scheduler.html#a6d7414ee130125d6f496bcbeab17c71b)
* SendCartesianMotionForce() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#ad65e38f8694b28d0704d29806f5d6d57)
* SendJointPosition() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a5b00a5ed07ac4595d8d63d8f02396c3b)
* serial_num : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#a59f4eb2ae4279049e47a70eaf274eafd)
* SetBreakpointMode() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#ac998e212916af429481620343539fe80)
* SetCartesianImpedance() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a929778ed475fd95e4f266caf470daaa2)
* SetDigitalOutputs() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a16e1c2e5a106805588ff31bdd871c7dd)
* SetForceControlAxis() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#abebcd7b8c4791f069f179be68319dd10)
* SetForceControlFrame() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a68c34a44811205797ddc1b6e67cf13c4)
* SetGlobalVariables() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a47260ffc8e48ae2c0449f5d180bbdd43)
* SetJointImpedance() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a2c895a57834cce602eef91275acc36ef)
* SetJointPositionLimits() : [flexiv::rdk::Safety](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_safety.html#a20651ac628855f3e30e98edf79f537c8)
* SetJointVelocityNormalLimits() : [flexiv::rdk::Safety](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_safety.html#a606845db1e5896de8f594d46ae153db2)
* SetJointVelocityReducedLimits() : [flexiv::rdk::Safety](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_safety.html#a5166d4fce9f41df75893fce28ba038e0)
* SetMaxContactWrench() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a0f3ac4119ce5f7b97ff55faa5d67e6ea)
* SetNullSpaceObjectives() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a07a497b2e8a21548a3fecec117539f40)
* SetNullSpacePosture() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#aff6e836bafd3c1bc624c46c6c91df802)
* SetPassiveForceControl() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#af65bbeabbba784d71f6b88b38021d311)
* SetVelocityScale() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a51dbb74cf1debeddcf02c38c1e8ee001)
* software_ver : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#a629c5c134df54e6ef316b63692b5878f)
* Start() : [flexiv::rdk::Scheduler](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_scheduler.html#aac277c2024a279082ff6dfdcad5f1bb3)
* states() : [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#a59c279bf4c867f3096edc3105a9e5d1a) , [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a1702778593ab37bd5229cff1530d7089)
* StepBreakpoint() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a3e56658cbb3288bafe30a1bf4b6c5739)
* Stop() : [flexiv::rdk::Gripper](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_gripper.html#a659e635a9d29b29655b9003feb12c530) , [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a6a8f36a745aa6ae002e212b78f997456) , [flexiv::rdk::Scheduler](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_scheduler.html#a2b13cecec3289d03668d9e9a61537ab4)
* stopped() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a42f6ec8c808ddebc8fd2801f7034dd59)
* str() : [flexiv::rdk::Coord](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_coord.html#aef16f47cdf96ef5086879fa760062775) , [flexiv::rdk::JPos](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_j_pos.html#af44a1a5999093020751f68177557fb02)
* StreamCartesianMotionForce() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a4ee5674bf7dde99d1285e9c358101033)
* StreamJointPosition() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#aefd3be3b2de0270977ed3267edd7cd45)
* StreamJointTorque() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a4d9c3131053c351e4e3f4b09316fe734)
* Switch() : [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#a2a648cd624a6fd96d5e3404c9b294396)
* SwitchMode() : [flexiv::rdk::Robot](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_robot.html#a81835116033c00bee2a588a8347fb105)
* SyncURDF() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#ae74c4f927c71fa71bc8ffa1671362e04)

### - t -

* tau : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#abc1df77da48a83010f18c32a3105c3db)
* tau_des : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a9a923d93324d69d6f262e57b343b590d)
* tau_dot : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a677acb4aff31cb8cc812e89476507ca5)
* tau_e : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#aebf0d6925ee3b487e7ae506ceddb4293)
* tau_ext : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a749119eae4fe44456fc7cefa0cb60dcd)
* tau_max : [flexiv::rdk::RobotInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_info.html#a230cce62f68662bb8a407bee2e5f6692)
* tcp_location : [flexiv::rdk::ToolParams](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_tool_params.html#a987a33115bc4eb3b64a23bdcab53661a)
* tcp_pose : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a783b9ef1901b69279b2cfae1ec539c18)
* tcp_vel : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a9946a146a2621dfad922bc15f3902a74)
* theta : [flexiv::rdk::RobotStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_robot_states.html#a7ecbf5c234a1924b1fc06ad10e7e6f5e)
* Tool() : [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#ad433ac63e7aa2d74cf7b16d5ec6c94df)

### - u -

* Update() : [flexiv::rdk::Model](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_model.html#a713721b10e8179d06c573b4bdbe6f0ad) , [flexiv::rdk::Tool](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_tool.html#a52e75d2fd49d683e71091149ea7b20d9) , [flexiv::rdk::WorkCoord](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_work_coord.html#a3ccdc730cabb5ee4007925642516fd8e)
* UploadTrajFile() : [flexiv::rdk::FileIO](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_file_i_o.html#a6af2d603410ce0fa3b75a11b19498318)

### - v -

* velocity_scale : [flexiv::rdk::PlanInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_plan_info.html#ac4430667e57f28a30de639c2995cff8f)

### - w -

* waiting_for_step : [flexiv::rdk::PlanInfo](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_plan_info.html#a3ff81a8fe57266a30738366159b85121)
* width : [flexiv::rdk::GripperStates](http://127.0.0.1:5500/doc/html/structflexiv_1_1rdk_1_1_gripper_states.html#a8ab42e30413a2d66b0cf2fedb8ddd357)
* WorkCoord() : [flexiv::rdk::WorkCoord](http://127.0.0.1:5500/doc/html/classflexiv_1_1rdk_1_1_work_coord.html#a1a35a1b563e7f5727d8451154394e47d)

File List

Here is a list of all documented files with brief descriptions:

[detail level 1234]

| ▼[example](https://www.flexiv.com/software/rdk/api/dir_cfafba98a580ce4b62f8a6fa96d7cbb0.html) |                                                                              |
| ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **basics10_logging_behavior.cpp**                                                     |                                                                              |
| **basics1_display_robot_states.cpp**                                                  |                                                                              |
| **basics2_clear_fault.cpp**                                                           |                                                                              |
| **basics3_primitive_execution.cpp**                                                   |                                                                              |
| **basics4_plan_execution.cpp**                                                        |                                                                              |
| **basics5_zero_force_torque_sensors.cpp**                                             |                                                                              |
| **basics6_gripper_control.cpp**                                                       |                                                                              |
| **basics7_auto_recovery.cpp**                                                         |                                                                              |
| **basics8_update_robot_tool.cpp**                                                     |                                                                              |
| **basics9_global_variables.cpp**                                                      |                                                                              |
| **intermediate1_realtime_joint_position_control.cpp**                                 |                                                                              |
| **intermediate2_realtime_joint_impedance_control.cpp**                                |                                                                              |
| **intermediate3_realtime_joint_torque_control.cpp**                                   |                                                                              |
| **intermediate4_realtime_joint_floating.cpp**                                         |                                                                              |
| **intermediate5_realtime_cartesian_pure_motion_control.cpp**                          |                                                                              |
| **intermediate6_realtime_cartesian_motion_force_control.cpp**                         |                                                                              |
| **intermediate7_robot_dynamics.cpp**                                                  |                                                                              |
| ▼[include](https://www.flexiv.com/software/rdk/api/dir_d44c64559bbebec7f509842c48db8b23.html) |                                                                              |
| ▼[flexiv](https://www.flexiv.com/software/rdk/api/dir_629c6833d5c9ae9060118730dacef252.html)  |                                                                              |
| ▼[rdk](https://www.flexiv.com/software/rdk/api/dir_77b19f718b0d8dab7d11aa4dfbb625d4.html)     |                                                                              |
| [data.hpp](https://www.flexiv.com/software/rdk/api/data_8hpp.html)                             | Header file containing various constant expressions, data structs, and enums |
| [device.hpp](https://www.flexiv.com/software/rdk/api/device_8hpp.html)                         |                                                                              |
| [file_io.hpp](https://www.flexiv.com/software/rdk/api/file__io_8hpp.html)                      |                                                                              |
| [gripper.hpp](https://www.flexiv.com/software/rdk/api/gripper_8hpp.html)                       |                                                                              |
| [maintenance.hpp](https://www.flexiv.com/software/rdk/api/maintenance_8hpp.html)               |                                                                              |
| [mode.hpp](https://www.flexiv.com/software/rdk/api/mode_8hpp.html)                             |                                                                              |
| [model.hpp](https://www.flexiv.com/software/rdk/api/model_8hpp.html)                           |                                                                              |
| [robot.hpp](https://www.flexiv.com/software/rdk/api/robot_8hpp.html)                           |                                                                              |
| [safety.hpp](https://www.flexiv.com/software/rdk/api/safety_8hpp.html)                         |                                                                              |
| [scheduler.hpp](https://www.flexiv.com/software/rdk/api/scheduler_8hpp.html)                   |                                                                              |
| [tool.hpp](https://www.flexiv.com/software/rdk/api/tool_8hpp.html)                             |                                                                              |
| [utility.hpp](https://www.flexiv.com/software/rdk/api/utility_8hpp.html)                       |                                                                              |
| [work_coord.hpp](https://www.flexiv.com/software/rdk/api/work__coord_8hpp.html)                |                                                                              |
| ▼[test](https://www.flexiv.com/software/rdk/api/dir_13e138d54eb8818da29c3992edef070a.html)    |                                                                              |
| **test_dynamics_engine.cpp**                                                          |                                                                              |
| **test_endurance.cpp**                                                                |                                                                              |
| **test_loop_latency.cpp**                                                             |                                                                              |
| **test_scheduler.cpp**                                                                |                                                                              |
| **test_timeliness_monitor.cpp**                                                       |                                                                              |

Examples

Here is a list of all examples:

- [basics10_logging_behavior.cpp](https://www.flexiv.com/software/rdk/api/basics10_logging_behavior_8cpp-example.html)
- [basics1_display_robot_states.cpp](https://www.flexiv.com/software/rdk/api/basics1_display_robot_states_8cpp-example.html)
- [basics2_clear_fault.cpp](https://www.flexiv.com/software/rdk/api/basics2_clear_fault_8cpp-example.html)
- [basics3_primitive_execution.cpp](https://www.flexiv.com/software/rdk/api/basics3_primitive_execution_8cpp-example.html)
- [basics4_plan_execution.cpp](https://www.flexiv.com/software/rdk/api/basics4_plan_execution_8cpp-example.html)
- [basics5_zero_force_torque_sensors.cpp](https://www.flexiv.com/software/rdk/api/basics5_zero_force_torque_sensors_8cpp-example.html)
- [basics6_gripper_control.cpp](https://www.flexiv.com/software/rdk/api/basics6_gripper_control_8cpp-example.html)
- [basics7_auto_recovery.cpp](https://www.flexiv.com/software/rdk/api/basics7_auto_recovery_8cpp-example.html)
- [basics8_update_robot_tool.cpp](https://www.flexiv.com/software/rdk/api/basics8_update_robot_tool_8cpp-example.html)
- [basics9_global_variables.cpp](https://www.flexiv.com/software/rdk/api/basics9_global_variables_8cpp-example.html)
- [intermediate1_realtime_joint_position_control.cpp](https://www.flexiv.com/software/rdk/api/intermediate1_realtime_joint_position_control_8cpp-example.html)
- [intermediate2_realtime_joint_impedance_control.cpp](https://www.flexiv.com/software/rdk/api/intermediate2_realtime_joint_impedance_control_8cpp-example.html)
- [intermediate3_realtime_joint_torque_control.cpp](https://www.flexiv.com/software/rdk/api/intermediate3_realtime_joint_torque_control_8cpp-example.html)
- [intermediate4_realtime_joint_floating.cpp](https://www.flexiv.com/software/rdk/api/intermediate4_realtime_joint_floating_8cpp-example.html)
- [intermediate5_realtime_cartesian_pure_motion_control.cpp](https://www.flexiv.com/software/rdk/api/intermediate5_realtime_cartesian_pure_motion_control_8cpp-example.html)
- [intermediate6_realtime_cartesian_motion_force_control.cpp](https://www.flexiv.com/software/rdk/api/intermediate6_realtime_cartesian_motion_force_control_8cpp-example.html)
- [intermediate7_robot_dynamics.cpp](https://www.flexiv.com/software/rdk/api/intermediate7_robot_dynamics_8cpp-example.html)




Class List
Here are the classes, structs, unions and interfaces with brief descriptions:
[detail level 123]
 Nflexiv	
 Nrdk	
 CCoord	Data structure representing the customized data type "COORD" in Flexiv Elements
 CDevice	Interface with the robot device(s)
 CFileIO	Interface for file transfer with the robot. The robot must be put into IDLE mode when transferring files
 CGripper	Interface with the robot gripper. Because gripper is also a type of device, this API uses the same underlying infrastructure as rdk::Device, but with functions tailored specifically for gripper controls
 CGripperParams	Data structure containing the gripper parameters
 CGripperStates	Data structure containing the gripper states
 CJPos	Data structure representing the customized data type "JPOS" in Flexiv Elements
 CMaintenance	Interface to carry out robot maintenance operations. The robot must be in IDLE mode when triggering any operations
 CModel	Interface to access certain robot kinematics and dynamics data
 CPlanInfo	Data structure containing information of the on-going primitive/plan
 CRobot	Main interface with the robot, containing several function categories and background services
 CRobotInfo	General information about the connected robot
 CRobotStates	Data structure containing the joint- and Cartesian-space robot states
 CSafety	Interface to change robot safety settings. The robot must be in IDLE mode when applying any changes. A password is required to authenticate this interface
 CSafetyLimits	Data structure containing configurable robot safety limits
 CScheduler	Real-time scheduler that can simultaneously run multiple periodic tasks. Parameters for each task are configured independently
 CTool	Interface to online update and interact with the robot tools. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes
 CToolParams	Data structure containing robot tool parameters
 CWorkCoord	Interface to online update and interact with the robot's work coordinates. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes
 CPose	
 CPose6D	
 CVector3	


 flexiv::rdk::Coord Struct Reference
Data structure representing the customized data type "COORD" in Flexiv Elements. More...

#include <data.hpp>

Public Member Functions
 	Coord (const std::array< double, kCartDoF/2 > &_position, const std::array< double, kCartDoF/2 > &_orientation, const std::array< std::string, 2 > &_ref_frame, const std::array< double, kSerialJointDoF > &_ref_q={}, const std::array< double, kMaxExtAxes > &_ref_q_e={})
 	Construct an instance of Coord. More...
 
std::string 	str () const
 
Public Attributes
std::array< double, kCartDoF/2 > 	position = {}
 
std::array< double, kCartDoF/2 > 	orientation = {}
 
std::array< std::string, 2 > 	ref_frame = {}
 
std::array< double, kSerialJointDoF > 	ref_q = {}
 
std::array< double, kMaxExtAxes > 	ref_q_e = {}
 
Detailed Description
Data structure representing the customized data type "COORD" in Flexiv Elements.

Warning
Here [m] is used as the unit of length, whereas [mm] is used in Flexiv Elements. The conversion is automatically done when exchanging "COORD" data type with the robot via functions like Robot::ExecutePrimitive(), Robot::SetGlobalVariables(), Robot::global_variables(), etc.
Examples
basics3_primitive_execution.cpp, and basics9_global_variables.cpp.
Definition at line 333 of file data.hpp.

Constructor & Destructor Documentation
◆ Coord()
flexiv::rdk::Coord::Coord	(	const std::array< double, kCartDoF/2 > & 	_position,
const std::array< double, kCartDoF/2 > & 	_orientation,
const std::array< std::string, 2 > & 	_ref_frame,
const std::array< double, kSerialJointDoF > & 	_ref_q = {},
const std::array< double, kMaxExtAxes > & 	_ref_q_e = {} 
)		
inline
Construct an instance of Coord.

Parameters
[in]	_position	Sets struct member [position].
[in]	_orientation	Sets struct member [orientation].
[in]	_ref_frame	Sets struct member [ref_frame].
[in]	_ref_q	Sets struct member [ref_q]. Leave empty to use default values.
[in]	_ref_q_e	Sets struct member [ref_q_e]. Leave empty if there's no external axis.
Definition at line 343 of file data.hpp.

Member Function Documentation
◆ str()
std::string flexiv::rdk::Coord::str	(		)	const
String representation of all data in the struct, separated by space

Member Data Documentation
◆ orientation
std::array<double, kCartDoF / 2> flexiv::rdk::Coord::orientation = {}
Orientation in terms of Euler angles in [ref_frame]. Unit: [degree]

Definition at line 361 of file data.hpp.

◆ position
std::array<double, kCartDoF / 2> flexiv::rdk::Coord::position = {}
Position in [ref_frame]. Unit: [m]

Definition at line 358 of file data.hpp.

◆ ref_frame
std::array<std::string, 2> flexiv::rdk::Coord::ref_frame = {}
Name of the reference frame "root::branch" represented as {"root", "branch"}. Refer to Flexiv Elements for available options. Some common ones are:

World origin: {"WORLD", "WORLD_ORIGIN"}
Current pose: {"TRAJ", "START"}
A work coordinate: {"WORK", "WorkCoord0"}
A global variable: {"GVAR", "MyCoord0"}
Definition at line 370 of file data.hpp.

◆ ref_q
std::array<double, kSerialJointDoF> flexiv::rdk::Coord::ref_q = {}
Reference joint positions of the arm. Only effective on robots with redundant degrees of freedom. Unit: [degree]

Note
Leave empty to use default values. However, this array cannot be empty if [ref_q_e] has values
Definition at line 376 of file data.hpp.

◆ ref_q_e
std::array<double, kMaxExtAxes> flexiv::rdk::Coord::ref_q_e = {}
Reference joint positions (linear or angular) of the external axes. Only effective on robots with redundant degrees of freedom and external axes. Unit: [m] or [degree]

Note
If the number of external axes ne<kMaxExtAxes, set the first ne elements and leave the rest 0. Leave the whole array empty if there's no external axis.
Definition at line 382 of file data.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/data.hpp

flexiv::rdk::Device Class Reference
Interface with the robot device(s). More...

#include <device.hpp>

Public Member Functions
 	Device (const Robot &robot)
 	[Non-blocking] Create an instance and initialize device control interface. More...
 
const std::map< std::string, bool > 	list () const
 	[Blocking] Get a list of existing devices and their status (enabled/disabled). More...
 
bool 	exist (const std::string &name) const
 	[Blocking] Whether the specified device already exists. More...
 
const std::map< std::string, std::variant< int, double, std::string, std::vector< double >, std::vector< std::string > > > 	params (const std::string &name) const
 	[Blocking] Get configuration parameters of the specified device. More...
 
void 	Enable (const std::string &name)
 	[Blocking] Enable the specified device. More...
 
void 	Disable (const std::string &name)
 	[Blocking] Disable the specified device. More...
 
void 	Command (const std::string &name, const std::map< std::string, std::variant< bool, int, double >> &commands)
 	[Blocking] Send command(s) for the specified device. More...
 
Detailed Description
Interface with the robot device(s).

Definition at line 19 of file device.hpp.

Constructor & Destructor Documentation
◆ Device()
flexiv::rdk::Device::Device	(	const Robot & 	robot	)	
[Non-blocking] Create an instance and initialize device control interface.

Parameters
[in]	robot	Reference to the instance of flexiv::rdk::Robot.
Exceptions
std::runtime_error	if the initialization sequence failed.
Member Function Documentation
◆ Command()
void flexiv::rdk::Device::Command	(	const std::string & 	name,
const std::map< std::string, std::variant< bool, int, double >> & 	commands 
)		
[Blocking] Send command(s) for the specified device.

Parameters
[in]	name	Name of the device to send command(s) to, must be an existing device.
[in]	commands	A map of {command_name, command_value}. For example, {{"setSpeed", 6000}, {"openLaser", true}}. All commands in the map will be sent to the device simultaneously. Make sure the command name(s) are valid and can be accepted by the specified device.
Exceptions
std::logic_error	if the specified device does not exist or not enabled yet.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
◆ Disable()
void flexiv::rdk::Device::Disable	(	const std::string & 	name	)	
[Blocking] Disable the specified device.

Parameters
[in]	name	Name of the device to disable, must be an existing device.
Exceptions
std::logic_error	if the specified device does not exist.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
◆ Enable()
void flexiv::rdk::Device::Enable	(	const std::string & 	name	)	
[Blocking] Enable the specified device.

Parameters
[in]	name	Name of the device to enable, must be an existing device.
Exceptions
std::logic_error	if the specified device does not exist.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
◆ exist()
bool flexiv::rdk::Device::exist	(	const std::string & 	name	)	const
[Blocking] Whether the specified device already exists.

Parameters
[in]	name	Name of the device to check.
Returns
True if the specified device exists.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ list()
const std::map<std::string, bool> flexiv::rdk::Device::list	(		)	const
[Blocking] Get a list of existing devices and their status (enabled/disabled).

Returns
A map of {device_name, is_enabled}. For example, {{"Mirka-AIROS-550CV", true}, {"LinearRail", false}}.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ params()
const std::map<std::string, std::variant<int, double, std::string, std::vector<double>, std::vector<std::string> > > flexiv::rdk::Device::params	(	const std::string & 	name	)	const
[Blocking] Get configuration parameters of the specified device.

Parameters
[in]	name	Name of the device to get parameters for, must be an existing one.
Returns
A map of {param_name, param_value}. Booleans are represented by int 1 and 0. For example, {{"maxVel", 0.5}, {"absolutePosition", {0.7, -0.4, 0.05}}, {"conveyorName", "conveyor0"}}.
Exceptions
std::logic_error	if the specified device does not exist.
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
The documentation for this class was generated from the following file:
include/flexiv/rdk/device.hpp


flexiv::rdk::FileIO Class Reference
Interface for file transfer with the robot. The robot must be put into IDLE mode when transferring files. More...

#include <file_io.hpp>

Public Member Functions
 	FileIO (const Robot &robot)
 	[Non-blocking] Create an instance and initialize file transfer interface. More...
 
void 	UploadTrajFile (const std::string &file_dir, const std::string &file_name)
 	[Blocking] Upload a trajectory file (.traj) to the robot. More...
 
Detailed Description
Interface for file transfer with the robot. The robot must be put into IDLE mode when transferring files.

Definition at line 19 of file file_io.hpp.

Constructor & Destructor Documentation
◆ FileIO()
flexiv::rdk::FileIO::FileIO	(	const Robot & 	robot	)	
[Non-blocking] Create an instance and initialize file transfer interface.

Parameters
[in]	robot	Reference to the instance of flexiv::rdk::Robot.
Exceptions
std::runtime_error	if the initialization sequence failed.
Member Function Documentation
◆ UploadTrajFile()
void flexiv::rdk::FileIO::UploadTrajFile	(	const std::string & 	file_dir,
const std::string & 	file_name 
)		
[Blocking] Upload a trajectory file (.traj) to the robot.

Parameters
[in]	file_dir	Relative or absolute path of the directory that contains the file to upload, e.g. /home/user/Documents/. Do not include the file name here.
[in]	file_name	Full name of the trajectory file to upload, including the suffix, e.g. PolishSpiral.traj. Do not include the directory path here.
Exceptions
std::invalid_argument	if failed to find or load the specified file.
std::logic_error	if robot is not in the correct control mode.
std::runtime_error	if failed to transfer the file.
Note
Applicable control modes: IDLE.
This function blocks until the file is successfully uploaded.
The documentation for this class was generated from the following file:
include/flexiv/rdk/file_io.hpp


flexiv::rdk::Gripper Class Reference
Interface with the robot gripper. Because gripper is also a type of device, this API uses the same underlying infrastructure as rdk::Device, but with functions tailored specifically for gripper controls. More...

#include <gripper.hpp>

Public Member Functions
 	Gripper (const Robot &robot)
 	[Non-blocking] Create an instance and initialize gripper control interface. More...
 
void 	Enable (const std::string &name)
 	[Blocking] Enable the specified gripper as a device, same as Device::Enable(). More...
 
void 	Disable ()
 	[Blocking] Disable the currently enabled gripper, similar to Device::Disable(). More...
 
void 	Init ()
 	[Blocking] Manually trigger the initialization of the enabled gripper. This step is not needed for grippers that automatically initialize upon power-on. More...
 
void 	Grasp (double force)
 	[Blocking] Grasp with direct force control. Requires the mounted gripper to support direct force control. More...
 
void 	Move (double width, double velocity, double force_limit=0)
 	[Blocking] Move the gripper fingers with position control. More...
 
void 	Stop ()
 	[Blocking] Stop the gripper and hold its current finger width. More...
 
const GripperParams 	params () const
 	[Non-blocking] Parameters of the currently enabled gripper. More...
 
const GripperStates 	states () const
 	[Non-blocking] Current states data of the enabled gripper. More...
 
Detailed Description
Interface with the robot gripper. Because gripper is also a type of device, this API uses the same underlying infrastructure as rdk::Device, but with functions tailored specifically for gripper controls.

Examples
basics6_gripper_control.cpp.
Definition at line 77 of file gripper.hpp.

Constructor & Destructor Documentation
◆ Gripper()
flexiv::rdk::Gripper::Gripper	(	const Robot & 	robot	)	
[Non-blocking] Create an instance and initialize gripper control interface.

Parameters
[in]	robot	Reference to the instance of flexiv::rdk::Robot.
Exceptions
std::runtime_error	if the initialization sequence failed.
Member Function Documentation
◆ Disable()
void flexiv::rdk::Gripper::Disable	(		)	
[Blocking] Disable the currently enabled gripper, similar to Device::Disable().

Exceptions
std::logic_error	if no gripper device is enabled.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
◆ Enable()
void flexiv::rdk::Gripper::Enable	(	const std::string & 	name	)	
[Blocking] Enable the specified gripper as a device, same as Device::Enable().

Parameters
[in]	name	Name of the gripper device to enable, must be an existing one.
Exceptions
std::logic_error	if the specified gripper device does not exist or a gripper is already enabled.
std::runtime_error	if failed to deliver the request to the connected robot or failed to sync gripper parameters.
Note
This function blocks until the request is successfully delivered.
There can only be one enabled gripper at a time, call Disable() on the currently enabled gripper before enabling another gripper.
Warning
There's no enforced check on whether the enabled device is a gripper or not. Using this API on a non-gripper device will likely lead to undefined behaviors.
Examples
basics6_gripper_control.cpp.
◆ Grasp()
void flexiv::rdk::Gripper::Grasp	(	double 	force	)	
[Blocking] Grasp with direct force control. Requires the mounted gripper to support direct force control.

Parameters
[in]	force	Target gripping force. Positive: closing force, negative: opening force [N].
Exceptions
std::logic_error	if no gripper device is enabled.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
Warning
Target inputs outside the valid range (see params()) will be saturated.
Examples
basics6_gripper_control.cpp.
◆ Init()
void flexiv::rdk::Gripper::Init	(		)	
[Blocking] Manually trigger the initialization of the enabled gripper. This step is not needed for grippers that automatically initialize upon power-on.

Exceptions
std::logic_error	if no gripper device is enabled.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
Warning
This function does not wait for the initialization sequence to finish, the user may need to implement wait after calling this function before commanding the gripper.
Examples
basics6_gripper_control.cpp.
◆ Move()
void flexiv::rdk::Gripper::Move	(	double 	width,
double 	velocity,
double 	force_limit = 0 
)		
[Blocking] Move the gripper fingers with position control.

Parameters
[in]	width	Target opening width [m].
[in]	velocity	Closing/opening velocity, cannot be 0 [m/s].
[in]	force_limit	Maximum output force during movement [N]. If not specified, default force limit of the mounted gripper will be used.
Exceptions
std::logic_error	if no gripper device is enabled.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
Warning
Target inputs outside the valid range (see params()) will be saturated.
Examples
basics6_gripper_control.cpp.
◆ params()
const GripperParams flexiv::rdk::Gripper::params	(		)	const
[Non-blocking] Parameters of the currently enabled gripper.

Returns
GripperParams value copy.
Examples
basics6_gripper_control.cpp.
◆ states()
const GripperStates flexiv::rdk::Gripper::states	(		)	const
[Non-blocking] Current states data of the enabled gripper.

Returns
GripperStates value copy.
Note
Real-time (RT).
Examples
basics6_gripper_control.cpp.
◆ Stop()
void flexiv::rdk::Gripper::Stop	(		)	
[Blocking] Stop the gripper and hold its current finger width.

Exceptions
std::logic_error	if no gripper device is enabled.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
Examples
basics6_gripper_control.cpp.
The documentation for this class was generated from the following file:
include/flexiv/rdk/gripper.hpp


flexiv::rdk::GripperParams Struct Reference
Data structure containing the gripper parameters. More...

#include <gripper.hpp>

Public Attributes
std::string 	name = {}
 
double 	max_width = {}
 
double 	min_width = {}
 
double 	max_force = {}
 
double 	min_force = {}
 
double 	max_vel = {}
 
double 	min_vel = {}
 
Detailed Description
Data structure containing the gripper parameters.

See also
Gripper::params().
Definition at line 20 of file gripper.hpp.

Member Data Documentation
◆ max_force
double flexiv::rdk::GripperParams::max_force = {}
Maximum grasping force [N]

Examples
basics6_gripper_control.cpp.
Definition at line 32 of file gripper.hpp.

◆ max_vel
double flexiv::rdk::GripperParams::max_vel = {}
Maximum finger moving velocity [m/s]

Examples
basics6_gripper_control.cpp.
Definition at line 38 of file gripper.hpp.

◆ max_width
double flexiv::rdk::GripperParams::max_width = {}
Maximum finger opening width [m]

Examples
basics6_gripper_control.cpp.
Definition at line 26 of file gripper.hpp.

◆ min_force
double flexiv::rdk::GripperParams::min_force = {}
Minimum grasping force [N]

Examples
basics6_gripper_control.cpp.
Definition at line 35 of file gripper.hpp.

◆ min_vel
double flexiv::rdk::GripperParams::min_vel = {}
Minimum finger moving velocity [m/s]

Examples
basics6_gripper_control.cpp.
Definition at line 41 of file gripper.hpp.

◆ min_width
double flexiv::rdk::GripperParams::min_width = {}
Minimum finger opening width [m]

Examples
basics6_gripper_control.cpp.
Definition at line 29 of file gripper.hpp.

◆ name
std::string flexiv::rdk::GripperParams::name = {}
Gripper name

Examples
basics6_gripper_control.cpp.
Definition at line 23 of file gripper.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/gripper.hpp

flexiv::rdk::GripperStates Struct Reference
Data structure containing the gripper states. More...

#include <gripper.hpp>

Public Attributes
double 	width = {}
 
double 	force = {}
 
bool 	is_moving = {}
 
Detailed Description
Data structure containing the gripper states.

See also
Gripper::states().
Definition at line 49 of file gripper.hpp.

Member Data Documentation
◆ force
double flexiv::rdk::GripperStates::force = {}
Measured finger force. Positive: opening force, negative: closing force. Reads 0 if the mounted gripper has no force sensing capability [N]

Examples
basics6_gripper_control.cpp.
Definition at line 56 of file gripper.hpp.

◆ is_moving
bool flexiv::rdk::GripperStates::is_moving = {}
Whether the gripper fingers are moving

Definition at line 59 of file gripper.hpp.

◆ width
double flexiv::rdk::GripperStates::width = {}
Measured finger opening width [m]

Definition at line 52 of file gripper.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/gripper.hpp


flexiv::rdk::JPos Struct Reference
Data structure representing the customized data type "JPOS" in Flexiv Elements. More...

#include <data.hpp>

Public Member Functions
 	JPos (const std::array< double, kSerialJointDoF > &_q, const std::array< double, kMaxExtAxes > &_q_e={})
 	Construct an instance of JPos. More...
 
std::string 	str () const
 
Public Attributes
std::array< double, kSerialJointDoF > 	q = {}
 
std::array< double, kMaxExtAxes > 	q_e = {}
 
Detailed Description
Data structure representing the customized data type "JPOS" in Flexiv Elements.

Warning
Here [m] is used as the unit of length, whereas [mm] is used in Flexiv Elements. The conversion is automatically done when exchanging "JPOS" data type with the robot via functions like Robot::ExecutePrimitive(), Robot::SetGlobalVariables(), etc.
Examples
basics3_primitive_execution.cpp.
Definition at line 299 of file data.hpp.

Constructor & Destructor Documentation
◆ JPos()
flexiv::rdk::JPos::JPos	(	const std::array< double, kSerialJointDoF > & 	_q,
const std::array< double, kMaxExtAxes > & 	_q_e = {} 
)		
inline
Construct an instance of JPos.

Parameters
[in]	_q	Sets struct member [q].
[in]	_q_e	Sets struct member [q_e]. Leave empty if there's no external axis.
Definition at line 306 of file data.hpp.

Member Function Documentation
◆ str()
std::string flexiv::rdk::JPos::str	(		)	const
String representation of all data in the struct, separated by space

Member Data Documentation
◆ q
std::array<double, kSerialJointDoF> flexiv::rdk::JPos::q = {}
Joint positions of the arm. Unit: [degree]

Definition at line 315 of file data.hpp.

◆ q_e
std::array<double, kMaxExtAxes> flexiv::rdk::JPos::q_e = {}
Joint positions (linear or angular) of the external axes. Unit: [m] or [degree]

Note
If the number of external axes ne<kMaxExtAxes, set the first ne elements and leave the rest 0. Leave the whole array empty if there's no external axis.
Definition at line 320 of file data.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/data.hpp


flexiv::rdk::Maintenance Class Reference
Interface to carry out robot maintenance operations. The robot must be in IDLE mode when triggering any operations. More...

#include <maintenance.hpp>

Public Member Functions
 	Maintenance (const Robot &robot)
 	[Non-blocking] Create an instance and initialize the interface. More...
 
void 	CalibrateJointTorqueSensors (const std::vector< double > &cali_posture={})
 	[Blocking] Calibrate all joint torque sensors. The robot will first move to a proper calibration posture, then start the low-level calibration of all joint torque sensors. Trigger this calibration if the sensed joint torques have noticeable deviations from true values. See below for more details. More...
 
Detailed Description
Interface to carry out robot maintenance operations. The robot must be in IDLE mode when triggering any operations.

Definition at line 19 of file maintenance.hpp.

Constructor & Destructor Documentation
◆ Maintenance()
flexiv::rdk::Maintenance::Maintenance	(	const Robot & 	robot	)	
[Non-blocking] Create an instance and initialize the interface.

Parameters
[in]	robot	Reference to the instance of flexiv::rdk::Robot.
Exceptions
std::runtime_error	if the initialization sequence failed.
Member Function Documentation
◆ CalibrateJointTorqueSensors()
void flexiv::rdk::Maintenance::CalibrateJointTorqueSensors	(	const std::vector< double > & 	cali_posture = {}	)	
[Blocking] Calibrate all joint torque sensors. The robot will first move to a proper calibration posture, then start the low-level calibration of all joint torque sensors. Trigger this calibration if the sensed joint torques have noticeable deviations from true values. See below for more details.

Parameters
[in]	cali_posture	Joint positions to move to before starting the calibration: qcali∈Rn×1. If left empty, the robot will use the recommended upright posture for calibration. Otherwise the specified posture will be used, which is NOT recommended. Valid range: [RobotInfo::q_min, RobotInfo::q_max]. Unit: [rad].
Exceptions
std::invalid_argument	if [cali_posture] contains any value outside the valid range, or its size does not match robot DoF.
std::logic_error	if robot is not in the correct control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the calibration is finished.
Warning
The robot needs to be rebooted for the calibration result to take effect.
How to determine when this calibration is needed?
When the robot is static and there's no payload or external force exerted on it, if RobotStates::ext_wrench_in_tcp still gives greater than 5N reading, then this calibration should be triggered once.
When running the "intermediate4_realtime_joint_floating.cpp" example, if the joints drift swiftly toward one direction, then this calibration should be triggered once.
The documentation for this class was generated from the following file:
include/flexiv/rdk/maintenance.hpp


flexiv::rdk::Model Class Reference
Interface to access certain robot kinematics and dynamics data. More...

#include <model.hpp>

Public Member Functions
 	Model (const Robot &robot, const Eigen::Vector3d &gravity_vector=Eigen::Vector3d(0.0, 0.0, -9.81))
 	[Non-blocking] Create an instance and initialize the integrated dynamics engine. More...
 
void 	Reload ()
 	[Blocking] Reload robot model using the latest data synced from the connected robot. Tool model is also synced. More...
 
void 	SyncURDF (const std::string &template_urdf_path)
 	[Blocking] Sync the actual kinematic parameters of the connected robot into the template URDF. More...
 
void 	Update (const std::vector< double > &positions, const std::vector< double > &velocities)
 	[Non-blocking] Update robot model using new joint states data. More...
 
const Eigen::MatrixXd 	J (const std::string &link_name)
 	[Non-blocking] Compute and get the Jacobian matrix at the frame of the specified link i, expressed in world frame. More...
 
const Eigen::MatrixXd 	dJ (const std::string &link_name)
 	[Non-blocking] Compute and get the time derivative of Jacobian matrix at the frame of the specified link i, expressed in world frame. More...
 
const Eigen::MatrixXd 	M ()
 	[Non-blocking] Compute and get the mass matrix for the generalized coordinates, i.e. joint space. More...
 
const Eigen::MatrixXd 	C ()
 	[Non-blocking] Compute and get the Coriolis/centripetal matrix for the generalized coordinates, i.e. joint space. More...
 
const Eigen::VectorXd 	g ()
 	[Non-blocking] Compute and get the gravity force vector for the generalized coordinates, i.e. joint space. More...
 
const Eigen::VectorXd 	c ()
 	[Non-blocking] Compute and get the Coriolis force vector for the generalized coordinates, i.e. joint space. More...
 
const std::pair< bool, std::vector< double > > 	reachable (const std::array< double, kPoseSize > &pose, const std::vector< double > &seed_positions, bool free_orientation)
 	[Blocking] Check if a Cartesian pose is reachable. If yes, also return an IK solution of the corresponding joint positions. More...
 
Detailed Description
Interface to access certain robot kinematics and dynamics data.

Examples
intermediate7_robot_dynamics.cpp.
Definition at line 20 of file model.hpp.

Constructor & Destructor Documentation
◆ Model()
flexiv::rdk::Model::Model	(	const Robot & 	robot,
const Eigen::Vector3d & 	gravity_vector = Eigen::Vector3d(0.0, 0.0, -9.81) 
)		
[Non-blocking] Create an instance and initialize the integrated dynamics engine.

Parameters
[in]	robot	Reference to the instance of flexiv::rdk::Robot.
[in]	gravity_vector	Earth's gravity vector in world frame. Default to [0.0,0.0,−9.81]T. Unit: [m/s2].
Exceptions
std::runtime_error	if the initialization sequence failed.
std::logic_error	if the connected robot does not have an RDK professional license; or the parsed robot model is not supported.
Member Function Documentation
◆ C()
const Eigen::MatrixXd flexiv::rdk::Model::C	(		)	
[Non-blocking] Compute and get the Coriolis/centripetal matrix for the generalized coordinates, i.e. joint space.

Returns
Coriolis/centripetal matrix: C(q,q˙)∈Rn×n.
Note
Call Update() before this function.
◆ c()
const Eigen::VectorXd flexiv::rdk::Model::c	(		)	
[Non-blocking] Compute and get the Coriolis force vector for the generalized coordinates, i.e. joint space.

Returns
Coriolis force vector: c(q,q˙)∈Rn×1. Unit: [Nm].
Note
Call Update() before this function.
◆ dJ()
const Eigen::MatrixXd flexiv::rdk::Model::dJ	(	const std::string & 	link_name	)	
[Non-blocking] Compute and get the time derivative of Jacobian matrix at the frame of the specified link i, expressed in world frame.

Parameters
[in]	link_name	Name of the link to get Jacobian derivative for.
Returns
Time derivative of the Jacobian matrix: 0Ji˙∈Rm×n.
Exceptions
std::out_of_range	if the specified link_name does not exist.
Note
Call Update() before this function.
Available links can be found in the provided URDF. They are {"base_link", "link1", "link2", "link3", "link4", "link5", "link6", "link7", "flange"}, plus "tool" if any flange tool is mounted.
◆ g()
const Eigen::VectorXd flexiv::rdk::Model::g	(		)	
[Non-blocking] Compute and get the gravity force vector for the generalized coordinates, i.e. joint space.

Returns
Gravity force vector: g(q)∈Rn×1. Unit: [Nm].
Note
Call Update() before this function.
◆ J()
const Eigen::MatrixXd flexiv::rdk::Model::J	(	const std::string & 	link_name	)	
[Non-blocking] Compute and get the Jacobian matrix at the frame of the specified link i, expressed in world frame.

Parameters
[in]	link_name	Name of the link to get Jacobian for.
Returns
Jacobian matrix: 0Ji∈Rm×n.
Exceptions
std::out_of_range	if the specified link_name does not exist.
Note
Call Update() before this function.
Available links can be found in the provided URDF. They are {"base_link", "link1", "link2", "link3", "link4", "link5", "link6", "link7", "flange"}, plus "tool" if any flange tool is mounted.
◆ M()
const Eigen::MatrixXd flexiv::rdk::Model::M	(		)	
[Non-blocking] Compute and get the mass matrix for the generalized coordinates, i.e. joint space.

Returns
Symmetric positive definite mass matrix: M(q)∈Sn×n++. Unit: [kgm2].
Note
Call Update() before this function.
◆ reachable()
const std::pair<bool, std::vector<double> > flexiv::rdk::Model::reachable	(	const std::array< double, kPoseSize > & 	pose,
const std::vector< double > & 	seed_positions,
bool 	free_orientation 
)		
[Blocking] Check if a Cartesian pose is reachable. If yes, also return an IK solution of the corresponding joint positions.

Parameters
[in]	pose	Cartesian pose to be checked.
[in]	seed_positions	Joint positions to be used as the seed for solving IK.
[in]	free_orientation	Only constrain position and allow orientation to move freely.
Returns
A pair of {is_reachable, ik_solution}.
Exceptions
std::invalid_argument	if size of [seed_positions] does not match robot DoF.
std::runtime_error	if failed to get a reply from the connected robot.
Note
Applicable control modes: All.
This function blocks until a reply is received.
◆ Reload()
void flexiv::rdk::Model::Reload	(		)	
[Blocking] Reload robot model using the latest data synced from the connected robot. Tool model is also synced.

Exceptions
std::runtime_error	if failed to sync model data.
std::logic_error	if the synced robot model contains invalid data.
Note
This function blocks until the model data is synced and the reloading is finished.
Call this function if the robot tool has changed.
◆ SyncURDF()
void flexiv::rdk::Model::SyncURDF	(	const std::string & 	template_urdf_path	)	
[Blocking] Sync the actual kinematic parameters of the connected robot into the template URDF.

Parameters
[in]	template_urdf_path	Path to the template URDF in [flexiv_rdk/resources] directory. This template URDF will be updated when the sync is finished.
Exceptions
std::invalid_argument	if failed to load the template URDF.
std::runtime_error	if failed to sync the URDF.
Note
This function blocks until the URDF syncing is finished.
Why is this function needed?
The URDFs in [flexiv_rdk/resources] directory contain kinematic parameters of the latest robot hardware version, which might be different from older versions. This function is therefore provided to sync the actual kinematic parameters of the connected robot into the template URDF.
◆ Update()
void flexiv::rdk::Model::Update	(	const std::vector< double > & 	positions,
const std::vector< double > & 	velocities 
)		
[Non-blocking] Update robot model using new joint states data.

Parameters
[in]	positions	Current joint positions: q∈Rn×1. Unit: [rad].
[in]	velocities	Current joint velocities: q˙∈Rn×1. Unit: [rad/s].
Exceptions
std::invalid_argument	if size of any input vector does not match robot DoF.
The documentation for this class was generated from the following file:
include/flexiv/rdk/model.hpp


flexiv::rdk::PlanInfo Struct Reference
Data structure containing information of the on-going primitive/plan. More...

#include <data.hpp>

Public Attributes
std::string 	pt_name = {}
 
std::string 	node_name = {}
 
std::string 	node_path = {}
 
std::string 	node_path_time_period = {}
 
std::string 	node_path_number = {}
 
std::string 	assigned_plan_name = {}
 
double 	velocity_scale = {}
 
bool 	waiting_for_step = {}
 
Detailed Description
Data structure containing information of the on-going primitive/plan.

See also
Robot::plan_info().
Definition at line 265 of file data.hpp.

Member Data Documentation
◆ assigned_plan_name
std::string flexiv::rdk::PlanInfo::assigned_plan_name = {}
Assigned plan name

Definition at line 283 of file data.hpp.

◆ node_name
std::string flexiv::rdk::PlanInfo::node_name = {}
Current node name

Definition at line 271 of file data.hpp.

◆ node_path
std::string flexiv::rdk::PlanInfo::node_path = {}
Current node path

Definition at line 274 of file data.hpp.

◆ node_path_number
std::string flexiv::rdk::PlanInfo::node_path_number = {}
Current node path number

Definition at line 280 of file data.hpp.

◆ node_path_time_period
std::string flexiv::rdk::PlanInfo::node_path_time_period = {}
Current node path time period

Definition at line 277 of file data.hpp.

◆ pt_name
std::string flexiv::rdk::PlanInfo::pt_name = {}
Current primitive name

Definition at line 268 of file data.hpp.

◆ velocity_scale
double flexiv::rdk::PlanInfo::velocity_scale = {}
Velocity scale

Definition at line 286 of file data.hpp.

◆ waiting_for_step
bool flexiv::rdk::PlanInfo::waiting_for_step = {}
Waiting for user signal to step the breakpoint

Definition at line 289 of file data.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/data.hpp


flexiv::rdk::Robot Class Reference
Main interface with the robot, containing several function categories and background services. More...

#include <robot.hpp>

Public Member Functions
 	Robot (const std::string &robot_sn, const std::vector< std::string > &network_interface_whitelist={})
 	[Blocking] Create an instance as the main robot control interface. RDK services will initialize and connection with the robot will be established. More...
 
bool 	connected () const
 	[Non-blocking] Whether the connection with the robot is established. More...
 
const RobotInfo 	info () const
 	[Non-blocking] General information about the connected robot. More...
 
Mode 	mode () const
 	[Non-blocking] Current control mode of the robot. More...
 
const RobotStates 	states () const
 	[Non-blocking] Current states data of the robot. More...
 
bool 	stopped () const
 	[Non-blocking] Whether the robot has come to a complete stop. More...
 
bool 	operational (bool verbose=true) const
 	[Non-blocking] Whether the robot is ready to be operated, which requires the following conditions to be met: enabled, brakes fully released, in auto mode, no fault, and not in reduced state. More...
 
OperationalStatus 	operational_status () const
 	[Non-blocking] Current operational status of the robot. More...
 
bool 	busy () const
 	[Non-blocking] Whether the robot is currently executing a task. This includes any user commanded operations that requires the robot to execute. For example, plans, primitives, Cartesian and joint motions, etc. More...
 
bool 	fault () const
 	[Non-blocking] Whether the robot is in fault state. More...
 
bool 	reduced () const
 	[Non-blocking] Whether the robot is in reduced state. More...
 
bool 	recovery () const
 	[Non-blocking] Whether the robot is in recovery state. More...
 
bool 	estop_released () const
 	[Non-blocking] Whether the emergency stop is released. More...
 
bool 	enabling_button_pressed () const
 	[Non-blocking] Whether the enabling button is pressed. More...
 
const std::vector< std::string > 	mu_log () const
 	[Non-blocking] Get multilingual log messages of the connected robot. More...
 
void 	Enable ()
 	[Blocking] Enable the robot, if E-stop is released and there's no fault, the robot will release brakes, and becomes operational a few seconds later. More...
 
void 	Brake (bool engage)
 	[Blocking] Force robot brakes to engage or release during normal operation. Restrictions apply, see warning. More...
 
void 	SwitchMode (Mode mode)
 	[Blocking] Switch to a new control mode and wait until mode transition is finished. More...
 
void 	Stop ()
 	[Blocking] Stop the robot and transit robot mode to IDLE. More...
 
bool 	ClearFault (unsigned int timeout_sec=30)
 	[Blocking] Try to clear minor or critical fault of the robot without a power cycle. More...
 
void 	RunAutoRecovery ()
 	[Blocking] Run automatic recovery to bring joints that are outside the allowed position range back into allowed range. More...
 
void 	SetGlobalVariables (const std::map< std::string, FlexivDataTypes > &global_vars)
 	[Blocking] Set values to global variables that already exist in the robot. More...
 
std::map< std::string, FlexivDataTypes > 	global_variables () const
 	[Blocking] Existing global variables and their current values. More...
 
void 	ExecutePlan (unsigned int index, bool continue_exec=false, bool block_until_started=true)
 	[Blocking] Execute a plan by specifying its index. More...
 
void 	ExecutePlan (const std::string &name, bool continue_exec=false, bool block_until_started=true)
 	[Blocking] Execute a plan by specifying its name. More...
 
void 	PausePlan (bool pause)
 	[Blocking] Pause or resume the execution of the current plan. More...
 
const std::vector< std::string > 	plan_list () const
 	[Blocking] Get a list of all available plans. More...
 
const PlanInfo 	plan_info () const
 	[Blocking] Get detailed information about the currently executing plan. Contains information like plan name, primitive name, node name, node path, node path time period, etc. More...
 
void 	SetBreakpointMode (bool is_enabled)
 	[Blocking] Enable or disable the breakpoint mode during plan execution. When enabled, the currently executing plan will pause at the pre-defined breakpoints. Use StepBreakpoint() to continue the execution and pause at the next breakpoint. More...
 
void 	StepBreakpoint ()
 	[Blocking] If breakpoint mode is enabled, step to the next breakpoint. The plan execution will continue and pause at the next breakpoint. More...
 
void 	SetVelocityScale (unsigned int velocity_scale)
 	[Blocking] Set overall velocity scale for robot motions during plan and primitive execution. More...
 
void 	ExecutePrimitive (const std::string &primitive_name, const std::map< std::string, FlexivDataTypes > &input_params, const std::map< std::string, FlexivDataTypes > &properties={}, bool block_until_started=true)
 	[Blocking] Execute a primitive by specifying its name and parameters, which can be found in the Flexiv Primitives documentation. More...
 
std::map< std::string, FlexivDataTypes > 	primitive_states () const
 	[Blocking] State parameters of the executing primitive and their current values. More...
 
void 	StreamJointTorque (const std::vector< double > &torques, bool enable_gravity_comp=true, bool enable_soft_limits=true)
 	[Non-blocking] Continuously stream joint torque command to the robot. More...
 
void 	StreamJointPosition (const std::vector< double > &positions, const std::vector< double > &velocities, const std::vector< double > &accelerations)
 	[Non-blocking] Continuously stream joint position, velocity, and acceleration command to the robot. The commands are tracked by either the joint impedance controller or the joint position controller, depending on the control mode. More...
 
void 	SendJointPosition (const std::vector< double > &positions, const std::vector< double > &velocities, const std::vector< double > &accelerations, const std::vector< double > &max_vel, const std::vector< double > &max_acc)
 	[Non-blocking] Discretely send joint position, velocity, and acceleration command to the robot. The robot's internal motion generator will smoothen the discrete commands, which are tracked by either the joint impedance controller or the joint position controller, depending on the control mode. More...
 
void 	SetJointImpedance (const std::vector< double > &K_q, const std::vector< double > &Z_q={0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7})
 	[Blocking] Set impedance properties of the robot's joint motion controller used in the joint impedance control modes. More...
 
void 	StreamCartesianMotionForce (const std::array< double, kPoseSize > &pose, const std::array< double, kCartDoF > &wrench={}, const std::array< double, kCartDoF > &velocity={}, const std::array< double, kCartDoF > &acceleration={})
 	[Non-blocking] Continuously stream Cartesian motion and/or force command for the robot to track using its unified motion-force controller, which allows doing force control in zero or more Cartesian axes and motion control in the rest axes. More...
 
void 	SendCartesianMotionForce (const std::array< double, kPoseSize > &pose, const std::array< double, kCartDoF > &wrench={}, double max_linear_vel=0.5, double max_angular_vel=1.0, double max_linear_acc=2.0, double max_angular_acc=5.0)
 	[Non-blocking] Discretely send Cartesian motion and/or force command for the robot to track using its unified motion-force controller, which allows doing force control in zero or more Cartesian axes and motion control in the rest axes. The robot's internal motion generator will smoothen the discrete commands. More...
 
void 	SetCartesianImpedance (const std::array< double, kCartDoF > &K_x, const std::array< double, kCartDoF > &Z_x={0.7, 0.7, 0.7, 0.7, 0.7, 0.7})
 	[Blocking] Set impedance properties of the robot's Cartesian motion controller used in the Cartesian motion-force control modes. More...
 
void 	SetMaxContactWrench (const std::array< double, kCartDoF > &max_wrench)
 	[Blocking] Set maximum contact wrench for the motion control part of the Cartesian motion-force control modes. The controller will regulate its output to maintain contact wrench (force and moment) with the environment under the set values. More...
 
void 	SetNullSpacePosture (const std::vector< double > &ref_positions)
 	[Blocking] Set reference joint positions for the null-space posture control module used in the Cartesian motion-force control modes. More...
 
void 	SetNullSpaceObjectives (double linear_manipulability=0.0, double angular_manipulability=0.0, double ref_positions_tracking=0.5)
 	[Blocking] Set weights of the three optimization objectives while computing the robot's null-space posture. Change the weights to optimize robot performance for different use cases. More...
 
void 	SetForceControlAxis (const std::array< bool, kCartDoF > &enabled_axes, const std::array< double, kCartDoF/2 > &max_linear_vel={1.0, 1.0, 1.0})
 	[Blocking] Set Cartesian axes to enable force control while in the Cartesian motion-force control modes. Axes not enabled for force control will be motion-controlled. More...
 
void 	SetForceControlFrame (CoordType root_coord, const std::array< double, kPoseSize > &T_in_root={0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0})
 	[Blocking] Set reference frame for force control while in the Cartesian motion-force control modes. The force control frame is defined by specifying its transformation with regard to the root coordinate. More...
 
void 	SetPassiveForceControl (bool is_enabled)
 	[Blocking] Enable or disable passive force control for the Cartesian motion-force control modes. When enabled, an open-loop force controller will be used to feed forward the target wrench, i.e. passive force control. When disabled, a closed-loop force controller will be used to track the target wrench, i.e. active force control. More...
 
void 	SetDigitalOutputs (const std::vector< unsigned int > &port_idx, const std::vector< bool > &values)
 	[Blocking] Set one or more digital output ports, including 16 on the control box plus 2 inside the wrist connector. More...
 
const std::array< bool, kIOPorts > 	digital_inputs () const
 	[Non-blocking] Current reading from all digital input ports, including 16 on the control box plus 2 inside the wrist connector. More...
 
Friends
class 	Device
 
class 	FileIO
 
class 	Gripper
 
class 	Maintenance
 
class 	Model
 
class 	Safety
 
class 	Tool
 
class 	WorkCoord
 
Detailed Description
Main interface with the robot, containing several function categories and background services.

Examples
basics10_logging_behavior.cpp, basics1_display_robot_states.cpp, basics2_clear_fault.cpp, basics3_primitive_execution.cpp, basics4_plan_execution.cpp, basics5_zero_force_torque_sensors.cpp, basics6_gripper_control.cpp, basics7_auto_recovery.cpp, basics8_update_robot_tool.cpp, basics9_global_variables.cpp, intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, intermediate6_realtime_cartesian_motion_force_control.cpp, and intermediate7_robot_dynamics.cpp.
Definition at line 24 of file robot.hpp.

Constructor & Destructor Documentation
◆ Robot()
flexiv::rdk::Robot::Robot	(	const std::string & 	robot_sn,
const std::vector< std::string > & 	network_interface_whitelist = {} 
)		
[Blocking] Create an instance as the main robot control interface. RDK services will initialize and connection with the robot will be established.

Parameters
[in]	robot_sn	Serial number of the robot to connect. The accepted formats are: "Rizon 4s-123456" and "Rizon4s-123456".
[in]	network_interface_whitelist	Limit the network interface(s) that can be used to try to establish connection with the specified robot. The whitelisted network interface is defined by its associated IPv4 address. For example, {"10.42.0.1", "192.168.2.102"}. If left empty, all available network interfaces will be tried when searching for the specified robot.
Exceptions
std::invalid_argument	if the format of [robot_sn] is invalid.
std::runtime_error	if the initialization sequence failed.
std::logic_error	if the connected robot does not have a valid RDK license; or this RDK library version is incompatible with the connected robot; or model of the connected robot is not supported.
Warning
This constructor blocks until the initialization sequence is successfully finished and connection with the robot is established.
Member Function Documentation
◆ Brake()
void flexiv::rdk::Robot::Brake	(	bool 	engage	)	
[Blocking] Force robot brakes to engage or release during normal operation. Restrictions apply, see warning.

Parameters
[in]	engage	True: engage brakes; false: release brakes.
Exceptions
std::logic_error	if the connected robot is not a medical one or the robot is moving.
std::runtime_error	if failed to engage/release the brakes.
Note
This function blocks until the brakes are successfully engaged/released.
Warning
This function is accessible only if a) the connected robot is a medical one AND b) the robot is not moving.
◆ busy()
bool flexiv::rdk::Robot::busy	(		)	const
[Non-blocking] Whether the robot is currently executing a task. This includes any user commanded operations that requires the robot to execute. For example, plans, primitives, Cartesian and joint motions, etc.

Returns
True: busy; false: idle.
Warning
Some exceptions exist for primitives, see ExecutePrimitive() for more details.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ ClearFault()
bool flexiv::rdk::Robot::ClearFault	(	unsigned int 	timeout_sec = 30	)	
[Blocking] Try to clear minor or critical fault of the robot without a power cycle.

Parameters
[in]	timeout_sec	Maximum time in seconds to wait for the fault to be successfully cleared. Normally, a minor fault should take no more than 3 seconds to clear, and a critical fault should take no more than 30 seconds to clear.
Returns
True: successfully cleared fault; false: failed to clear fault.
Exceptions
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the fault is successfully cleared or [timeout_sec] has elapsed.
Warning
Clearing a critical fault through this function without a power cycle requires a dedicated device, which may not be installed in older robot models.
Examples
basics1_display_robot_states.cpp, intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ connected()
bool flexiv::rdk::Robot::connected	(		)	const
[Non-blocking] Whether the connection with the robot is established.

Returns
True: connected; false: disconnected.
◆ digital_inputs()
const std::array<bool, kIOPorts> flexiv::rdk::Robot::digital_inputs	(		)	const
[Non-blocking] Current reading from all digital input ports, including 16 on the control box plus 2 inside the wrist connector.

Returns
A boolean array whose index corresponds to that of the digital input ports. True: port high; false: port low.
Examples
basics1_display_robot_states.cpp.
◆ Enable()
void flexiv::rdk::Robot::Enable	(		)	
[Blocking] Enable the robot, if E-stop is released and there's no fault, the robot will release brakes, and becomes operational a few seconds later.

Exceptions
std::logic_error	if the robot is not connected.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
Examples
basics1_display_robot_states.cpp, intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ enabling_button_pressed()
bool flexiv::rdk::Robot::enabling_button_pressed	(		)	const
[Non-blocking] Whether the enabling button is pressed.

Returns
True: pressed; false: released.
◆ estop_released()
bool flexiv::rdk::Robot::estop_released	(		)	const
[Non-blocking] Whether the emergency stop is released.

Returns
True: released; false: pressed.
◆ ExecutePlan() [1/2]
void flexiv::rdk::Robot::ExecutePlan	(	const std::string & 	name,
bool 	continue_exec = false,
bool 	block_until_started = true 
)		
[Blocking] Execute a plan by specifying its name.

Parameters
[in]	name	Name of the plan to execute, can be obtained via plan_list().
[in]	continue_exec	Whether to continue executing the plan when the RDK program is closed or the connection is lost.
[in]	block_until_started	Whether to wait for the commanded plan to finish loading and start execution before the function returns. Depending on the amount of computation needed to get the plan ready, the loading process typically takes no more than 200 ms.
Exceptions
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: NRT_PLAN_EXECUTION.
This function blocks until the request is successfully delivered if [block_until_started] is disabled, or until the plan has started execution if [block_until_started] is enabled.
busy() can be used to check if the plan has finished.
◆ ExecutePlan() [2/2]
void flexiv::rdk::Robot::ExecutePlan	(	unsigned int 	index,
bool 	continue_exec = false,
bool 	block_until_started = true 
)		
[Blocking] Execute a plan by specifying its index.

Parameters
[in]	index	Index of the plan to execute, can be obtained via plan_list().
[in]	continue_exec	Whether to continue executing the plan when the RDK program is closed or the connection is lost.
[in]	block_until_started	Whether to wait for the commanded plan to finish loading and start execution before the function returns. Depending on the amount of computation needed to get the plan ready, the loading process typically takes no more than 200 ms.
Exceptions
std::invalid_argument	if [index] is outside the valid range.
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: NRT_PLAN_EXECUTION.
This function blocks until the request is successfully delivered if [block_until_started] is disabled, or until the plan has started execution if [block_until_started] is enabled.
busy() can be used to check if the plan has finished.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ ExecutePrimitive()
void flexiv::rdk::Robot::ExecutePrimitive	(	const std::string & 	primitive_name,
const std::map< std::string, FlexivDataTypes > & 	input_params,
const std::map< std::string, FlexivDataTypes > & 	properties = {},
bool 	block_until_started = true 
)		
[Blocking] Execute a primitive by specifying its name and parameters, which can be found in the Flexiv Primitives documentation.

Parameters
[in]	primitive_name	Primitive name. For example, "Home", "MoveL", "ZeroFTSensor", etc.
[in]	input_params	Specify basic and advanced parameters of the primitive via a map of {input_parameter_name, input_parameter_value(s)}. Use int 1 and 0 to represent booleans. E.g. {{"target", rdk::Coord({0.65, -0.3, 0.2}, {180, 0, 180}, {"WORLD", "WORLD_ORIGIN"})}, {"vel", 0.6}, {"zoneRadius", "Z50"}}.
[in]	properties	Specify properties of the primitive via a map of {property_name, property_value(s)}. Use int 1 and 0 to represent booleans. E.g. {{"lockExternalAxes", 0}}.
[in]	block_until_started	Whether to wait for the commanded primitive to finish loading and start execution before the function returns. Depending on the amount of computation needed to get the primitive ready, the loading process typically takes no more than 200 ms.
Exceptions
std::length_error	if [input_params] is too long to transmit in one request.
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: NRT_PRIMITIVE_EXECUTION.
This function blocks until the request is successfully delivered if [block_until_started] is disabled, or until the primitive has started execution if [block_until_started] is enabled.
Warning
The primitive input parameters may not use SI units, please refer to the Flexiv Primitives documentation for exact unit definition.
Most primitives won't exit by themselves and require users to explicitly trigger transitions based on specific primitive states. In such case, busy() will stay true even if it seems everything is done for that primitive.
Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ fault()
bool flexiv::rdk::Robot::fault	(		)	const
[Non-blocking] Whether the robot is in fault state.

Returns
True: robot has fault; false: robot normal.
Examples
basics1_display_robot_states.cpp, intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ global_variables()
std::map<std::string, FlexivDataTypes> flexiv::rdk::Robot::global_variables	(		)	const
[Blocking] Existing global variables and their current values.

Returns
A map of {global_var_name, global_var_value(s)}. Booleans are represented by int 1 and 0. For example, {{"camera_offset", {0.1, -0.2, 0.3}}, {"start_plan", 1}}.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
See also
SetGlobalVariables().
◆ info()
const RobotInfo flexiv::rdk::Robot::info	(		)	const
[Non-blocking] General information about the connected robot.

Returns
RobotInfo value copy.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, and intermediate5_realtime_cartesian_pure_motion_control.cpp.
◆ mode()
Mode flexiv::rdk::Robot::mode	(		)	const
[Non-blocking] Current control mode of the robot.

Returns
flexiv::rdk::Mode enum.
◆ mu_log()
const std::vector<std::string> flexiv::rdk::Robot::mu_log	(		)	const
[Non-blocking] Get multilingual log messages of the connected robot.

Returns
Robot log messages stored since the last successful instantiation of this class. Each element in the string list corresponds to one message with timestamp and log level added. New message is pushed to the back of the vector.
Note
Possible log level tags are: [info], [warning], [error], and [critical].
Warning
Messages before the last successful instantiation of this class are not available.
◆ operational()
bool flexiv::rdk::Robot::operational	(	bool 	verbose = true	)	const
[Non-blocking] Whether the robot is ready to be operated, which requires the following conditions to be met: enabled, brakes fully released, in auto mode, no fault, and not in reduced state.

Parameters
[in]	verbose	Whether to print warning message indicating why the robot is not operational when this function returns false.
Returns
True: operational (operational_status() == READY); false: not operational.
Warning
The robot won't execute any user command until it's ready to be operated.
Examples
basics1_display_robot_states.cpp, intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ operational_status()
OperationalStatus flexiv::rdk::Robot::operational_status	(		)	const
[Non-blocking] Current operational status of the robot.

Returns
OperationalStatus enum.
◆ PausePlan()
void flexiv::rdk::Robot::PausePlan	(	bool 	pause	)	
[Blocking] Pause or resume the execution of the current plan.

Parameters
[in]	pause	True: pause plan; false: resume plan.
Exceptions
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: NRT_PLAN_EXECUTION.
This function blocks until the request is successfully delivered.
Warning
Internal plans (not created by user) cannot be resumed due to safety concerns.
◆ plan_info()
const PlanInfo flexiv::rdk::Robot::plan_info	(		)	const
[Blocking] Get detailed information about the currently executing plan. Contains information like plan name, primitive name, node name, node path, node path time period, etc.

Returns
PlanInfo data struct.
Exceptions
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to get a reply from the connected robot.
Note
Applicable control modes: NRT_PLAN_EXECUTION.
This function blocks until a reply is received.
◆ plan_list()
const std::vector<std::string> flexiv::rdk::Robot::plan_list	(		)	const
[Blocking] Get a list of all available plans.

Returns
Available plans in the format of a string list.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ primitive_states()
std::map<std::string, FlexivDataTypes> flexiv::rdk::Robot::primitive_states	(		)	const
[Blocking] State parameters of the executing primitive and their current values.

Returns
A map of {pt_state_name, pt_state_value(s)}. Booleans are represented by int 1 and 0. For example, {{"reachedTarget", 1}, {"timePeriod", 5.6}, {"forceOffset", {0.1, 0.2, -1.3}}}.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ recovery()
bool flexiv::rdk::Robot::recovery	(		)	const
[Non-blocking] Whether the robot is in recovery state.

Returns
True: in recovery state; false: not in recovery state.
Note
Use RunAutoRecovery() to execute automatic recovery operation.
Recovery state
The robot will enter recovery state if it needs to recover from joint position limit violation (a critical system fault that requires a recovery operation, during which the joints that moved outside the allowed position range will need to move very slowly back into the allowed range). Please refer to the robot user manual for more details about system recovery state.
◆ reduced()
bool flexiv::rdk::Robot::reduced	(		)	const
[Non-blocking] Whether the robot is in reduced state.

Returns
True: in reduced state; false: not in reduced state.
Reduced state
The robot will enter reduced state if a) the safety input for reduced state goes low or b) robot TCP passes through any safety plane. The safety limits are lowered in reduced state compared to normal state. Specific values for the safety limits can be configured in Flexiv Elements under Settings -> Safety Configuration. Please refer to the robot user manual for more details about system reduced state.
◆ RunAutoRecovery()
void flexiv::rdk::Robot::RunAutoRecovery	(		)	
[Blocking] Run automatic recovery to bring joints that are outside the allowed position range back into allowed range.

Exceptions
std::runtime_error	if failed to enter automatic recovery mode.
Note
Refer to user manual for more details.
This function blocks until the automatic recovery process is finished.
See also
recovery().
◆ SendCartesianMotionForce()
void flexiv::rdk::Robot::SendCartesianMotionForce	(	const std::array< double, kPoseSize > & 	pose,
const std::array< double, kCartDoF > & 	wrench = {},
double 	max_linear_vel = 0.5,
double 	max_angular_vel = 1.0,
double 	max_linear_acc = 2.0,
double 	max_angular_acc = 5.0 
)		
[Non-blocking] Discretely send Cartesian motion and/or force command for the robot to track using its unified motion-force controller, which allows doing force control in zero or more Cartesian axes and motion control in the rest axes. The robot's internal motion generator will smoothen the discrete commands.

Parameters
[in]	pose	Target TCP pose in world frame: OTTCPd∈R7×1. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[].
[in]	wrench	Target TCP wrench (force and moment) in the force control reference frame (configured by SetForceControlFrame()): 0Fd∈R6×1. The robot will track the target wrench using an explicit force controller. Consists of R3×1 force and R3×1 moment: [fx,fy,fz,mx,my,mz]T. Unit: [N]:[Nm].
[in]	max_linear_vel	Maximum Cartesian linear velocity when moving to the target pose. A safe value is provided as default. Unit: [m/s].
[in]	max_angular_vel	Maximum Cartesian angular velocity when moving to the target pose. A safe value is provided as default. Unit: [rad/s].
[in]	max_linear_acc	Maximum Cartesian linear acceleration when moving to the target pose. A safe value is provided as default. Unit: [m/s2].
[in]	max_angular_acc	Maximum Cartesian angular acceleration when moving to the target pose. A safe value is provided as default. Unit: [rad/s2].
Exceptions
std::invalid_argument	if any of the last 4 input parameters is negative.
std::logic_error	if robot is not in an applicable control mode.
Note
Applicable control modes: NRT_CARTESIAN_MOTION_FORCE.
Warning
Same as Flexiv Elements, the target wrench is expressed as wrench sensed at TCP instead of wrench exerted by TCP. E.g. commanding f_z = +5 N will make the end-effector move towards -Z direction, so that upon contact, the sensed force will be +5 N.
How to achieve pure motion control?
Use SetForceControlAxis() to disable force control for all Cartesian axes to achieve pure motion control. This function does pure motion control by default.
How to achieve pure force control?
Use SetForceControlAxis() to enable force control for all Cartesian axes to achieve pure force control, active or passive.
How to achieve unified motion-force control?
Use SetForceControlAxis() to enable force control for one or more Cartesian axes and leave the rest axes motion-controlled, then provide target pose for the motion-controlled axes and target wrench for the force-controlled axes.
See also
SetCartesianImpedance(), SetMaxContactWrench(), SetNullSpacePosture(), SetForceControlAxis(), SetForceControlFrame(), SetPassiveForceControl().
Examples
intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ SendJointPosition()
void flexiv::rdk::Robot::SendJointPosition	(	const std::vector< double > & 	positions,
const std::vector< double > & 	velocities,
const std::vector< double > & 	accelerations,
const std::vector< double > & 	max_vel,
const std::vector< double > & 	max_acc 
)		
[Non-blocking] Discretely send joint position, velocity, and acceleration command to the robot. The robot's internal motion generator will smoothen the discrete commands, which are tracked by either the joint impedance controller or the joint position controller, depending on the control mode.

Parameters
[in]	positions	Target joint positions: qd∈Rn×1. Unit: [rad].
[in]	velocities	Target joint velocities: q˙d∈Rn×1. Each joint will maintain this amount of velocity when it reaches the target position. Unit: [rad/s].
[in]	accelerations	Target joint accelerations: q¨d∈Rn×1. Each joint will maintain this amount of acceleration when it reaches the target position. Unit: [rad/s2].
[in]	max_vel	Maximum joint velocities for the planned trajectory: q˙max∈Rn×1. Unit: [rad/s].
[in]	max_acc	Maximum joint accelerations for the planned trajectory: q¨max∈Rn×1. Unit: [rad/s2].
Exceptions
std::invalid_argument	if size of any input vector does not match robot DoF.
std::logic_error	if robot is not in an applicable control mode.
Note
Applicable control modes: NRT_JOINT_IMPEDANCE, NRT_JOINT_POSITION.
Warning
Calling this function a second time while the motion from the previous call is still ongoing will trigger an online re-planning of the joint trajectory, such that the previous command is aborted and the new command starts to execute.
See also
SetJointImpedance().
◆ SetBreakpointMode()
void flexiv::rdk::Robot::SetBreakpointMode	(	bool 	is_enabled	)	
[Blocking] Enable or disable the breakpoint mode during plan execution. When enabled, the currently executing plan will pause at the pre-defined breakpoints. Use StepBreakpoint() to continue the execution and pause at the next breakpoint.

Parameters
[in]	is_enabled	True: enable; false: disable. By default, breakpoint mode is disabled.
Exceptions
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: NRT_PLAN_EXECUTION.
This function blocks until the request is successfully delivered.
◆ SetCartesianImpedance()
void flexiv::rdk::Robot::SetCartesianImpedance	(	const std::array< double, kCartDoF > & 	K_x,
const std::array< double, kCartDoF > & 	Z_x = {0.7, 0.7, 0.7, 0.7, 0.7, 0.7} 
)		
[Blocking] Set impedance properties of the robot's Cartesian motion controller used in the Cartesian motion-force control modes.

Parameters
[in]	K_x	Cartesian motion stiffness: Kx∈R6×1. Setting motion stiffness of a motion-controlled Cartesian axis to 0 will make this axis free-floating. Consists of R3×1 linear stiffness and R3×1 angular stiffness: [kx,ky,kz,kRx,kRy,kRz]T. Valid range: [0, RobotInfo::K_x_nom]. Unit: [N/m]:[Nm/rad].
[in]	Z_x	Cartesian motion damping ratio: Zx∈R6×1. Consists of R3×1 linear damping ratio and R3×1 angular damping ratio: [ζx,ζy,ζz,ζRx,ζRy,ζRz]T. Valid range: [0.3, 0.8]. The nominal (safe) value is provided as default.
Exceptions
std::invalid_argument	if [K_x] or [Z_x] contains any value outside the valid range.
std::logic_error	if robot is not in an applicable control mode.
Note
Applicable control modes: RT_CARTESIAN_MOTION_FORCE, NRT_CARTESIAN_MOTION_FORCE.
This function blocks until the request is successfully delivered.
Warning
Changing damping ratio [Z_x] to a non-nominal value may lead to performance and stability issues, please use with caution.
Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp.
◆ SetDigitalOutputs()
void flexiv::rdk::Robot::SetDigitalOutputs	(	const std::vector< unsigned int > & 	port_idx,
const std::vector< bool > & 	values 
)		
[Blocking] Set one or more digital output ports, including 16 on the control box plus 2 inside the wrist connector.

Parameters
[in]	port_idx	Index of port(s) to set, can be a single port or multiple ports. E.g. {0, 5, 7, 15} or {1, 3, 10} or {8}. Valid range of the index number is [0–17].
[in]	values	Corresponding values to set to the specified ports. True: set port high, false: set port low. Vector size must match the size of port_idx.
Exceptions
std::invalid_argument	if [port_idx] contains any index number outside the valid range.
std::length_error	if the two input vectors have different sizes.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the request is successfully delivered.
◆ SetForceControlAxis()
void flexiv::rdk::Robot::SetForceControlAxis	(	const std::array< bool, kCartDoF > & 	enabled_axes,
const std::array< double, kCartDoF/2 > & 	max_linear_vel = {1.0, 1.0, 1.0} 
)		
[Blocking] Set Cartesian axes to enable force control while in the Cartesian motion-force control modes. Axes not enabled for force control will be motion-controlled.

Parameters
[in]	enabled_axes	Flags to enable/disable force control for certain Cartesian axes in the force control reference frame (configured by SetForceControlFrame()). The axis order is [X,Y,Z,Rx,Ry,Rz].
[in]	max_linear_vel	For linear Cartesian axes that are enabled for force control, limit the moving velocity to these values as a protection mechanism in case of contact loss. The axis order is [X,Y,Z]. Valid range: [0.005, 2.0]. Unit: [m/s].
Exceptions
std::invalid_argument	if [max_linear_vel] contains any value outside the valid range.
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: RT_CARTESIAN_MOTION_FORCE, NRT_CARTESIAN_MOTION_FORCE.
This function blocks until the request is successfully delivered.
If not set, force control is disabled for all Cartesian axes by default.
Warning
The maximum linear velocity protection for force control axes is only effective under active force control (i.e. passive force control disabled), see SetPassiveForceControl().
Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ SetForceControlFrame()
void flexiv::rdk::Robot::SetForceControlFrame	(	CoordType 	root_coord,
const std::array< double, kPoseSize > & 	T_in_root = {0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0} 
)		
[Blocking] Set reference frame for force control while in the Cartesian motion-force control modes. The force control frame is defined by specifying its transformation with regard to the root coordinate.

Parameters
[in]	root_coord	Reference coordinate of [T_in_root].
[in]	T_in_root	Transformation from [root_coord] to the user-defined force control frame: rootTforce∈R7×1. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[]. If root coordinate is a fixed one (e.g. WORLD), then the force control frame will also be fixed; if root coordinate is a moving one (e.g. TCP), then the force control frame will also be moving with the root coordinate. An identity transformation is provided as default.
Exceptions
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: RT_CARTESIAN_MOTION_FORCE, NRT_CARTESIAN_MOTION_FORCE.
This function blocks until the request is successfully delivered.
If not set, the robot will use WORLD origin as the force control frame by default.
Force control frame
In Cartesian motion-force control modes, the reference frame of motion control is always the world frame, but the reference frame of force control can be an arbitrary one. While the world frame is the commonly used global coordinate, the current TCP frame is a dynamic local coordinate whose transformation with regard to the world frame changes as the robot TCP moves. When using world frame with no transformation as the force control frame, the force-controlled axes and motion-controlled axes are guaranteed to be orthogonal. Otherwise, the force-controlled axes and motion-controlled axes are NOT guaranteed to be orthogonal because different reference frames are used. In this case, it's recommended but not required to set the target pose such that the actual robot motion direction(s) are orthogonal to force direction(s). If they are not orthogonal, the motion control's vector component(s) in the force direction(s) will be eliminated.
Examples
intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ SetGlobalVariables()
void flexiv::rdk::Robot::SetGlobalVariables	(	const std::map< std::string, FlexivDataTypes > & 	global_vars	)	
[Blocking] Set values to global variables that already exist in the robot.

Parameters
[in]	global_vars	A map of {global_var_name, global_var_value(s)}. Use int 1 and 0 to represent booleans. For example, {{"camera_offset", {0.1, -0.2, 0.3}}, {"start_plan", 1}}.
Exceptions
std::length_error	if [global_vars] is empty or too long to transmit in one request.
std::logic_error	if any of the specified global variables does not exist.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
This function blocks until the global variables are successfully set.
Warning
The specified global variables need to be created first using Flexiv Elements.
See also
global_variables().
◆ SetJointImpedance()
void flexiv::rdk::Robot::SetJointImpedance	(	const std::vector< double > & 	K_q,
const std::vector< double > & 	Z_q = {0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7} 
)		
[Blocking] Set impedance properties of the robot's joint motion controller used in the joint impedance control modes.

Parameters
[in]	K_q	Joint motion stiffness: Kq∈Rn×1. Setting motion stiffness of a joint axis to 0 will make this axis free-floating. Valid range: [0, RobotInfo::K_q_nom]. Unit: [Nm/rad].
[in]	Z_q	Joint motion damping ratio: Zq∈Rn×1. Valid range: [0.3, 0.8]. The nominal (safe) value is provided as default.
Exceptions
std::invalid_argument	if [K_q] or [Z_q] contains any value outside the valid range or size of any input vector does not match robot DoF.
std::logic_error	if robot is not in an applicable control mode.
Note
Applicable control modes: RT_JOINT_IMPEDANCE, NRT_JOINT_IMPEDANCE.
This function blocks until the request is successfully delivered.
Warning
Changing damping ratio [Z_q] to a non-nominal value may lead to performance and stability issues, please use with caution.
Examples
intermediate2_realtime_joint_impedance_control.cpp.
◆ SetMaxContactWrench()
void flexiv::rdk::Robot::SetMaxContactWrench	(	const std::array< double, kCartDoF > & 	max_wrench	)	
[Blocking] Set maximum contact wrench for the motion control part of the Cartesian motion-force control modes. The controller will regulate its output to maintain contact wrench (force and moment) with the environment under the set values.

Parameters
[in]	max_wrench	Maximum contact wrench (force and moment): Fmax∈R6×1. Consists of R3×1 maximum force and R3×1 maximum moment: [fx,fy,fz,mx,my,mz]T. Unit: [N]:[Nm].
Exceptions
std::invalid_argument	if [max_wrench] contains any negative value.
std::logic_error	if robot is not in an applicable control mode.
Note
The maximum contact wrench regulation only applies to the motion control part.
Applicable control modes: RT_CARTESIAN_MOTION_FORCE, NRT_CARTESIAN_MOTION_FORCE.
This function blocks until the request is successfully delivered.
Warning
The maximum contact wrench regulation cannot be enabled if any of the rotational Cartesian axes is enabled for moment control.
Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ SetNullSpaceObjectives()
void flexiv::rdk::Robot::SetNullSpaceObjectives	(	double 	linear_manipulability = 0.0,
double 	angular_manipulability = 0.0,
double 	ref_positions_tracking = 0.5 
)		
[Blocking] Set weights of the three optimization objectives while computing the robot's null-space posture. Change the weights to optimize robot performance for different use cases.

Parameters
[in]	linear_manipulability	Increase this weight to improve the robot's capability to translate freely in Cartesian space, i.e. a broader range of potential translation movements. Valid range: [0.0, 1.0].
[in]	angular_manipulability	Increase this weight to improve the robot's capability to rotate freely in Cartesian space, i.e. a broader range of potential rotation movements. Valid range: [0.0, 1.0].
[in]	ref_positions_tracking	Increase this weight to make the robot track closer to the reference joint positions specified using SetNullSpacePosture(). Valid range: [0.1, 1.0].
Exceptions
std::invalid_argument	if any of the input parameters is outside its valid range.
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
The default value is provided for each parameter.
Applicable control modes: RT_CARTESIAN_MOTION_FORCE, NRT_CARTESIAN_MOTION_FORCE.
This function blocks until the request is successfully delivered.
Warning
The optimization weights will be automatically reset to the provided default values upon re-entering the applicable control modes.
◆ SetNullSpacePosture()
void flexiv::rdk::Robot::SetNullSpacePosture	(	const std::vector< double > & 	ref_positions	)	
[Blocking] Set reference joint positions for the null-space posture control module used in the Cartesian motion-force control modes.

Parameters
[in]	ref_positions	Reference joint positions for the null-space posture control: qns∈Rn×1. Valid range: [RobotInfo::q_min, RobotInfo::q_max]. Unit: [rad].
Exceptions
std::invalid_argument	if [ref_positions] contains any value outside the valid range or size of any input vector does not match robot DoF.
std::logic_error	if robot is not in an applicable control mode.
Note
Applicable control modes: RT_CARTESIAN_MOTION_FORCE, NRT_CARTESIAN_MOTION_FORCE.
This function blocks until the request is successfully delivered.
Warning
The reference joint positions will be automatically reset to the robot's current joint positions upon re-entering the applicable control modes.
Null-space posture control
Similar to human arm, a robotic arm with redundant joint-space degree(s) of freedom (DoF > 6) can change its overall posture without affecting the ongoing primary task. This is achieved through a technique called "null-space control". After the reference joint positions of a desired robot posture are set using this function, the robot's null-space control module will try to pull the arm as close to this posture as possible without affecting the primary Cartesian motion-force control task.
Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp.
◆ SetPassiveForceControl()
void flexiv::rdk::Robot::SetPassiveForceControl	(	bool 	is_enabled	)	
[Blocking] Enable or disable passive force control for the Cartesian motion-force control modes. When enabled, an open-loop force controller will be used to feed forward the target wrench, i.e. passive force control. When disabled, a closed-loop force controller will be used to track the target wrench, i.e. active force control.

Parameters
[in]	is_enabled	True: enable; false: disable. By default, passive force control is disabled and active force control is used.
Exceptions
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
If not set, the passive force control is disabled by default.
Difference between active and passive force control
Active force control uses a feedback loop to reduce the error between target wrench and measured wrench. This method results in better force tracking performance, but at the cost of additional Cartesian damping which could potentially decrease motion tracking performance. On the other hand, passive force control simply feeds forward the target wrench. This methods results in worse force tracking performance, but is more robust and does not introduce additional Cartesian damping. The choice of active or passive force control depends on the actual application.
◆ SetVelocityScale()
void flexiv::rdk::Robot::SetVelocityScale	(	unsigned int 	velocity_scale	)	
[Blocking] Set overall velocity scale for robot motions during plan and primitive execution.

Parameters
[in]	velocity_scale	Percentage scale to adjust the overall velocity of robot motions. Valid range: [0, 100]. Setting to 100 means to move with 100% of specified motion velocity, and 0 means not moving at all.
Exceptions
std::invalid_argument	if [velocity_scale] is outside the valid range.
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: NRT_PLAN_EXECUTION, NRT_PRIMITIVE_EXECUTION.
This function blocks until the request is successfully delivered.
◆ states()
const RobotStates flexiv::rdk::Robot::states	(		)	const
[Non-blocking] Current states data of the robot.

Returns
RobotStates value copy.
Note
Real-time (RT).
Examples
basics1_display_robot_states.cpp, intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ StepBreakpoint()
void flexiv::rdk::Robot::StepBreakpoint	(		)	
[Blocking] If breakpoint mode is enabled, step to the next breakpoint. The plan execution will continue and pause at the next breakpoint.

Exceptions
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: NRT_PLAN_EXECUTION.
This function blocks until the request is successfully delivered.
Use PlanInfo::waiting_for_step to check if the plan is currently waiting for user signal to step the breakpoint.
◆ Stop()
void flexiv::rdk::Robot::Stop	(		)	
[Blocking] Stop the robot and transit robot mode to IDLE.

Exceptions
std::runtime_error	if failed to stop the robot.
Note
This function blocks until the robot comes to a complete stop.
Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp.
◆ stopped()
bool flexiv::rdk::Robot::stopped	(		)	const
[Non-blocking] Whether the robot has come to a complete stop.

Returns
True: stopped; false: still moving.
◆ StreamCartesianMotionForce()
void flexiv::rdk::Robot::StreamCartesianMotionForce	(	const std::array< double, kPoseSize > & 	pose,
const std::array< double, kCartDoF > & 	wrench = {},
const std::array< double, kCartDoF > & 	velocity = {},
const std::array< double, kCartDoF > & 	acceleration = {} 
)		
[Non-blocking] Continuously stream Cartesian motion and/or force command for the robot to track using its unified motion-force controller, which allows doing force control in zero or more Cartesian axes and motion control in the rest axes.

Parameters
[in]	pose	Target TCP pose in world frame: OTTCPd∈R7×1. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[].
[in]	wrench	Target TCP wrench (force and moment) in the force control reference frame (configured by SetForceControlFrame()): 0Fd∈R6×1. The robot will track the target wrench using an explicit force controller. Consists of R3×1 force and R3×1 moment: [fx,fy,fz,mx,my,mz]T. Unit: [N]:[Nm].
[in]	velocity	Target TCP velocity (linear and angular) in world frame: 0x˙d∈R6×1. Providing properly calculated target velocity can improve the robot's overall tracking performance at the cost of reduced robustness. Leaving this input 0 can maximize robustness at the cost of reduced tracking performance. Consists of R3×1 linear and R3×1 angular velocity. Unit: [m/s]:[rad/s].
[in]	acceleration	Target TCP acceleration (linear and angular) in world frame: 0x¨d∈R6×1. Feeding forward target acceleration can improve the robot's tracking performance for highly dynamic motions, but it's also okay to leave this input 0. Consists of R3×1 linear and R3×1 angular acceleration. Unit: [m/s2]:[rad/s2].
Exceptions
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if number of timeliness failures has reached limit.
Note
Applicable control modes: RT_CARTESIAN_MOTION_FORCE.
Real-time (RT).
Warning
Always stream smooth and continuous motion commands to avoid sudden movements. The force commands don't need to be continuous.
Same as Flexiv Elements, the target wrench is expressed as wrench sensed at TCP instead of wrench exerted by TCP. E.g. commanding f_z = +5 N will make the end-effector move towards -Z direction, so that upon contact, the sensed force will be +5 N.
How to achieve pure motion control?
Use SetForceControlAxis() to disable force control for all Cartesian axes to achieve pure motion control. This function does pure motion control by default.
How to achieve pure force control?
Use SetForceControlAxis() to enable force control for all Cartesian axes to achieve pure force control, active or passive.
How to achieve unified motion-force control?
Use SetForceControlAxis() to enable force control for one or more Cartesian axes and leave the rest axes motion-controlled, then provide target pose for the motion-controlled axes and target wrench for the force-controlled axes.
See also
SetCartesianImpedance(), SetMaxContactWrench(), SetNullSpacePosture(), SetForceControlAxis(), SetForceControlFrame(), SetPassiveForceControl().
Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ StreamJointPosition()
void flexiv::rdk::Robot::StreamJointPosition	(	const std::vector< double > & 	positions,
const std::vector< double > & 	velocities,
const std::vector< double > & 	accelerations 
)		
[Non-blocking] Continuously stream joint position, velocity, and acceleration command to the robot. The commands are tracked by either the joint impedance controller or the joint position controller, depending on the control mode.

Parameters
[in]	positions	Target joint positions: qd∈Rn×1. Unit: [rad].
[in]	velocities	Target joint velocities: q˙d∈Rn×1. Unit: [rad/s].
[in]	accelerations	Target joint accelerations: q¨d∈Rn×1. Unit: [rad/s2].
Exceptions
std::invalid_argument	if size of any input vector does not match robot DoF.
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if number of timeliness failures has reached limit.
Note
Applicable control modes: RT_JOINT_IMPEDANCE, RT_JOINT_POSITION.
Real-time (RT).
Warning
Always stream smooth and continuous commands to avoid sudden movements.
See also
SetJointImpedance().
Examples
intermediate1_realtime_joint_position_control.cpp, and intermediate2_realtime_joint_impedance_control.cpp.
◆ StreamJointTorque()
void flexiv::rdk::Robot::StreamJointTorque	(	const std::vector< double > & 	torques,
bool 	enable_gravity_comp = true,
bool 	enable_soft_limits = true 
)		
[Non-blocking] Continuously stream joint torque command to the robot.

Parameters
[in]	torques	Target joint torques: τJd∈Rn×1. Unit: [Nm].
[in]	enable_gravity_comp	Enable/disable robot gravity compensation.
[in]	enable_soft_limits	Enable/disable soft limits to keep the joints from moving outside allowed position range, which will trigger a safety fault that requires recovery operation.
Exceptions
std::invalid_argument	if size of any input vector does not match robot DoF.
std::logic_error	if robot is not in an applicable control mode.
std::runtime_error	if number of timeliness failures has reached limit.
Note
Applicable control modes: RT_JOINT_TORQUE.
Real-time (RT).
Warning
Always stream smooth and continuous commands to avoid sudden movements.
Examples
intermediate3_realtime_joint_torque_control.cpp, and intermediate4_realtime_joint_floating.cpp.
◆ SwitchMode()
void flexiv::rdk::Robot::SwitchMode	(	Mode 	mode	)	
[Blocking] Switch to a new control mode and wait until mode transition is finished.

Parameters
[in]	mode	flexiv::rdk::Mode enum.
Exceptions
std::invalid_argument	if the requested mode is invalid or unlicensed.
std::logic_error	if robot is in an unknown control mode or is not operational.
std::runtime_error	if failed to transit the robot into the specified control mode after several attempts.
Note
This function blocks until the robot has successfully transited into the specified control mode.
Warning
If the robot is still moving when this function is called, it will automatically stop then make the mode transition.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
The documentation for this class was generated from the following file:
include/flexiv/rdk/robot.hpp


flexiv::rdk::RobotInfo Struct Reference
General information about the connected robot. More...

#include <data.hpp>

Public Attributes
std::string 	serial_num = {}
 
std::string 	software_ver = {}
 
std::string 	model_name = {}
 
std::string 	license_type = {}
 
size_t 	DoF = {}
 
std::array< double, kCartDoF > 	K_x_nom = {}
 
std::vector< double > 	K_q_nom = {}
 
std::vector< double > 	q_min = {}
 
std::vector< double > 	q_max = {}
 
std::vector< double > 	dq_max = {}
 
std::vector< double > 	tau_max = {}
 
Detailed Description
General information about the connected robot.

See also
Robot::info().
Definition at line 68 of file data.hpp.

Member Data Documentation
◆ DoF
size_t flexiv::rdk::RobotInfo::DoF = {}
Joint-space degrees of freedom: n.

Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, and intermediate4_realtime_joint_floating.cpp.
Definition at line 83 of file data.hpp.

◆ dq_max
std::vector<double> flexiv::rdk::RobotInfo::dq_max = {}
Upper software limits of joint velocities: q˙max∈Rn×1. Unit: [rad/s].

Definition at line 115 of file data.hpp.

◆ K_q_nom
std::vector<double> flexiv::rdk::RobotInfo::K_q_nom = {}
Nominal motion stiffness of the joint impedance control modes: Knomq∈Rn×1. Unit: [Nm/rad].

Examples
intermediate2_realtime_joint_impedance_control.cpp.
Definition at line 97 of file data.hpp.

◆ K_x_nom
std::array<double, kCartDoF> flexiv::rdk::RobotInfo::K_x_nom = {}
Nominal motion stiffness of the Cartesian motion-force control modes: Knomx∈R6×1. Consists of R3×1 linear stiffness and R3×1 angular stiffness: [kx,ky,kz,kRx,kRy,kRz]T. Unit: [N/m]:[Nm/rad].

Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp.
Definition at line 91 of file data.hpp.

◆ license_type
std::string flexiv::rdk::RobotInfo::license_type = {}
Type of license

Definition at line 80 of file data.hpp.

◆ model_name
std::string flexiv::rdk::RobotInfo::model_name = {}
Robot model name, e.g. Rizon4, Rizon10, Moonlight, etc.

Definition at line 77 of file data.hpp.

◆ q_max
std::vector<double> flexiv::rdk::RobotInfo::q_max = {}
Upper software limits of joint positions: qmax∈Rn×1. Unit: [rad].

Definition at line 109 of file data.hpp.

◆ q_min
std::vector<double> flexiv::rdk::RobotInfo::q_min = {}
Lower software limits of joint positions: qmin∈Rn×1. Unit: [rad].

Definition at line 103 of file data.hpp.

◆ serial_num
std::string flexiv::rdk::RobotInfo::serial_num = {}
Robot serial number.

Definition at line 71 of file data.hpp.

◆ software_ver
std::string flexiv::rdk::RobotInfo::software_ver = {}
Robot software version.

Definition at line 74 of file data.hpp.

◆ tau_max
std::vector<double> flexiv::rdk::RobotInfo::tau_max = {}
Upper software limits of joint torques: τmax∈Rn×1. Unit: [Nm].

Definition at line 121 of file data.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/data.hpp


flexiv::rdk::RobotStates Struct Reference
Data structure containing the joint- and Cartesian-space robot states. More...

#include <data.hpp>

Public Attributes
std::vector< double > 	q = {}
 
std::vector< double > 	theta = {}
 
std::vector< double > 	dq = {}
 
std::vector< double > 	dtheta = {}
 
std::vector< double > 	tau = {}
 
std::vector< double > 	tau_des = {}
 
std::vector< double > 	tau_dot = {}
 
std::vector< double > 	tau_ext = {}
 
std::vector< double > 	q_e = {}
 
std::vector< double > 	dq_e = {}
 
std::vector< double > 	tau_e = {}
 
std::array< double, kPoseSize > 	tcp_pose = {}
 
std::array< double, kCartDoF > 	tcp_vel = {}
 
std::array< double, kPoseSize > 	flange_pose = {}
 
std::array< double, kCartDoF > 	ft_sensor_raw = {}
 
std::array< double, kCartDoF > 	ext_wrench_in_tcp = {}
 
std::array< double, kCartDoF > 	ext_wrench_in_world = {}
 
std::array< double, kCartDoF > 	ext_wrench_in_tcp_raw = {}
 
std::array< double, kCartDoF > 	ext_wrench_in_world_raw = {}
 
Detailed Description
Data structure containing the joint- and Cartesian-space robot states.

See also
Robot::states().
Definition at line 129 of file data.hpp.

Member Data Documentation
◆ dq
std::vector<double> flexiv::rdk::RobotStates::dq = {}
Measured joint velocities of the arm using link-side encoder: q˙∈Rn×1. This is the direct but more noisy measurement of joint velocities. Unit: [rad/s].

Definition at line 151 of file data.hpp.

◆ dq_e
std::vector<double> flexiv::rdk::RobotStates::dq_e = {}
Measured joint velocities of the external axes (if any): q˙e∈Rne×1. Unit: [rad/s].

Definition at line 195 of file data.hpp.

◆ dtheta
std::vector<double> flexiv::rdk::RobotStates::dtheta = {}
Measured joint velocities of the arm using motor-side encoder: θ˙∈Rn×1. This is the indirect but less noisy measurement of joint velocities, preferred for most cases. Unit: [rad/s].

Examples
intermediate3_realtime_joint_torque_control.cpp, and intermediate4_realtime_joint_floating.cpp.
Definition at line 158 of file data.hpp.

◆ ext_wrench_in_tcp
std::array<double, kCartDoF> flexiv::rdk::RobotStates::ext_wrench_in_tcp = {}
Estimated external wrench applied on TCP and expressed in TCP frame: TCPFext∈R6×1. Consists of R3×1 force and R3×1 moment: [fx,fy,fz,mx,my,mz]T. Unit: [N]:[Nm].

Definition at line 239 of file data.hpp.

◆ ext_wrench_in_tcp_raw
std::array<double, kCartDoF> flexiv::rdk::RobotStates::ext_wrench_in_tcp_raw = {}
Unfiltered version of ext_wrench_in_tcp. The data is more noisy but has no filter latency.

Definition at line 252 of file data.hpp.

◆ ext_wrench_in_world
std::array<double, kCartDoF> flexiv::rdk::RobotStates::ext_wrench_in_world = {}
Estimated external wrench applied on TCP and expressed in world frame: 0Fext∈R6×1. Consists of R3×1 force and R3×1 moment: [fx,fy,fz,mx,my,mz]T. Unit: [N]:[Nm].

Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
Definition at line 247 of file data.hpp.

◆ ext_wrench_in_world_raw
std::array<double, kCartDoF> flexiv::rdk::RobotStates::ext_wrench_in_world_raw = {}
Unfiltered version of ext_wrench_in_world The data is more noisy but has no filter latency.

Definition at line 257 of file data.hpp.

◆ flange_pose
std::array<double, kPoseSize> flexiv::rdk::RobotStates::flange_pose = {}
Measured flange pose expressed in world frame: OTflange∈R7×1. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[].

Definition at line 223 of file data.hpp.

◆ ft_sensor_raw
std::array<double, kCartDoF> flexiv::rdk::RobotStates::ft_sensor_raw = {}
Force-torque (FT) sensor raw reading in flange frame: flangeFraw∈R6×1. The value is 0 if no FT sensor is installed. Consists of R3×1 force and R3×1 moment: [fx,fy,fz,mx,my,mz]T. Unit: [N]:[Nm].

Definition at line 231 of file data.hpp.

◆ q
std::vector<double> flexiv::rdk::RobotStates::q = {}
Measured joint positions of the arm using link-side encoder: q∈Rn×1. This is the direct measurement of joint positions, preferred for most cases. Unit: [rad].

Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, and intermediate5_realtime_cartesian_pure_motion_control.cpp.
Definition at line 136 of file data.hpp.

◆ q_e
std::vector<double> flexiv::rdk::RobotStates::q_e = {}
Measured joint positions of the external axes (if any): qe∈Rne×1. Unit: [rad].

Definition at line 189 of file data.hpp.

◆ tau
std::vector<double> flexiv::rdk::RobotStates::tau = {}
Measured joint torques of the arm: τ∈Rn×1. Unit: [Nm].

Definition at line 164 of file data.hpp.

◆ tau_des
std::vector<double> flexiv::rdk::RobotStates::tau_des = {}
Desired joint torques of the arm: τd∈Rn×1. Compensation of nonlinear dynamics (gravity, centrifugal, and Coriolis) is excluded. Unit: [Nm].

Definition at line 170 of file data.hpp.

◆ tau_dot
std::vector<double> flexiv::rdk::RobotStates::tau_dot = {}
Numerical derivative of measured joint torques of the arm: τ˙∈Rn×1. Unit: [Nm/s].

Definition at line 176 of file data.hpp.

◆ tau_e
std::vector<double> flexiv::rdk::RobotStates::tau_e = {}
Measured joint torques of the external axes (if any): τe∈Rne×1. Unit: [Nm].

Definition at line 201 of file data.hpp.

◆ tau_ext
std::vector<double> flexiv::rdk::RobotStates::tau_ext = {}
Estimated external joint torques of the arm: τ^ext∈Rn×1. Produced by any external contact (with robot body or end-effector) that does not belong to the known robot model. Unit: [Nm].

Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp.
Definition at line 183 of file data.hpp.

◆ tcp_pose
std::array<double, kPoseSize> flexiv::rdk::RobotStates::tcp_pose = {}
Measured TCP pose expressed in world frame: OTTCP∈R7×1. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[].

Examples
intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
Definition at line 208 of file data.hpp.

◆ tcp_vel
std::array<double, kCartDoF> flexiv::rdk::RobotStates::tcp_vel = {}
Measured TCP velocity expressed in world frame: OX˙∈R6×1. Consists of R3×1 linear velocity and R3×1 angular velocity: [vx,vy,vz,ωx,ωy,ωz]T. Unit: [m/s]:[rad/s].

Definition at line 216 of file data.hpp.

◆ theta
std::vector<double> flexiv::rdk::RobotStates::theta = {}
Measured joint positions of the arm using motor-side encoder: θ∈Rn×1. This is the indirect measurement of joint positions. θ=q+Δ, where Δ is the joint's internal deflection between motor and link. Unit: [rad].

Definition at line 144 of file data.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/data.hpp



flexiv::rdk::Safety Class Reference
Interface to change robot safety settings. The robot must be in IDLE mode when applying any changes. A password is required to authenticate this interface. More...

#include <safety.hpp>

Public Member Functions
 	Safety (const Robot &robot, const std::string &password)
 	[Non-blocking] Create an instance and initialize the interface. More...
 
const SafetyLimits 	default_limits () const
 	[Non-blocking] Default values of the safety limits of the connected robot. More...
 
const SafetyLimits 	current_limits () const
 	[Non-blocking] Current values of the safety limits of the connected robot. More...
 
const std::array< bool, kSafetyIOPorts > 	safety_inputs () const
 	[Non-blocking] Current reading from all safety input ports. More...
 
void 	SetJointPositionLimits (const std::vector< double > &min_positions, const std::vector< double > &max_positions)
 	[Blocking] Set new joint position safety limits to the connected robot, which will honor this setting when making movements. More...
 
void 	SetJointVelocityNormalLimits (const std::vector< double > &max_velocities)
 	[Blocking] Set new joint velocity safety limits to the connected robot, which will honor this setting when making movements under the normal state. More...
 
void 	SetJointVelocityReducedLimits (const std::vector< double > &max_velocities)
 	[Blocking] Set new joint velocity safety limits to the connected robot, which will honor this setting when making movements under the reduced state. More...
 
Detailed Description
Interface to change robot safety settings. The robot must be in IDLE mode when applying any changes. A password is required to authenticate this interface.

Definition at line 46 of file safety.hpp.

Constructor & Destructor Documentation
◆ Safety()
flexiv::rdk::Safety::Safety	(	const Robot & 	robot,
const std::string & 	password 
)		
[Non-blocking] Create an instance and initialize the interface.

Parameters
[in]	robot	Reference to the instance of flexiv::rdk::Robot.
[in]	password	Password to authorize making changes to the robot's safety settings.
Exceptions
std::invalid_argument	if the provided password is incorrect.
std::runtime_error	if the initialization sequence failed.
Member Function Documentation
◆ current_limits()
const SafetyLimits flexiv::rdk::Safety::current_limits	(		)	const
[Non-blocking] Current values of the safety limits of the connected robot.

Returns
SafetyLimits value copy.
◆ default_limits()
const SafetyLimits flexiv::rdk::Safety::default_limits	(		)	const
[Non-blocking] Default values of the safety limits of the connected robot.

Returns
SafetyLimits value copy.
◆ safety_inputs()
const std::array<bool, kSafetyIOPorts> flexiv::rdk::Safety::safety_inputs	(		)	const
[Non-blocking] Current reading from all safety input ports.

Returns
A boolean array whose index corresponds to that of the safety input ports. True: port high; false: port low.
◆ SetJointPositionLimits()
void flexiv::rdk::Safety::SetJointPositionLimits	(	const std::vector< double > & 	min_positions,
const std::vector< double > & 	max_positions 
)		
[Blocking] Set new joint position safety limits to the connected robot, which will honor this setting when making movements.

Parameters
[in]	min_positions	Minimum joint positions: qmin∈Rn×1. Valid range: [default_min_joint_positions, default_max_joint_positions]. Unit: [rad].
[in]	max_positions	Maximum joint positions: qmax∈Rn×1. Valid range: [default_min_joint_positions, default_max_joint_positions]. Unit: [rad].
Exceptions
std::invalid_argument	if [min_positions] or [max_positions] contains any value outside the valid range, or size of any input vector does not match robot DoF.
std::logic_error	if robot is not in the correct control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
Warning
A reboot is required for the updated safety settings to take effect.
◆ SetJointVelocityNormalLimits()
void flexiv::rdk::Safety::SetJointVelocityNormalLimits	(	const std::vector< double > & 	max_velocities	)	
[Blocking] Set new joint velocity safety limits to the connected robot, which will honor this setting when making movements under the normal state.

Parameters
[in]	max_velocities	Maximum joint velocities for normal state: dqmax∈Rn×1. Valid range: [0.8727, joint_velocity_normal_limits]. Unit: [rad/s].
Exceptions
std::invalid_argument	if [max_velocities] contains any value outside the valid range, or its size does not match robot DoF.
std::logic_error	if robot is not in the correct control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
Warning
A reboot is required for the updated safety settings to take effect.
◆ SetJointVelocityReducedLimits()
void flexiv::rdk::Safety::SetJointVelocityReducedLimits	(	const std::vector< double > & 	max_velocities	)	
[Blocking] Set new joint velocity safety limits to the connected robot, which will honor this setting when making movements under the reduced state.

Parameters
[in]	max_velocities	Maximum joint velocities for reduced state: dqmax∈Rn×1. Valid range: [0.8727, joint_velocity_normal_limits]. Unit: [rad/s].
Exceptions
std::invalid_argument	if [max_velocities] contains any value outside the valid range, or its size does not match robot DoF.
std::logic_error	if robot is not in the correct control mode.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
Warning
A reboot is required for the updated safety settings to take effect.
The documentation for this class was generated from the following file:
include/flexiv/rdk/safety.hpp


flexiv::rdk::SafetyLimits Struct Reference
Data structure containing configurable robot safety limits. More...

#include <safety.hpp>

Public Attributes
std::vector< double > 	q_min = {}
 
std::vector< double > 	q_max = {}
 
std::vector< double > 	dq_max_normal = {}
 
std::vector< double > 	dq_max_reduced = {}
 
Detailed Description
Data structure containing configurable robot safety limits.

Definition at line 21 of file safety.hpp.

Member Data Documentation
◆ dq_max_normal
std::vector<double> flexiv::rdk::SafetyLimits::dq_max_normal = {}
Upper safety limits of joint velocities when the robot is in normal state: q˙normalmax∈Rn×1. Unit: [rad/s].

Definition at line 33 of file safety.hpp.

◆ dq_max_reduced
std::vector<double> flexiv::rdk::SafetyLimits::dq_max_reduced = {}
Upper safety limits of joint velocities when the robot is in reduced state: q˙reducedmax∈Rn×1. Unit: [rad/s].

See also
Robot::reduced()
Definition at line 38 of file safety.hpp.

◆ q_max
std::vector<double> flexiv::rdk::SafetyLimits::q_max = {}
Upper safety limits of joint positions: qmax∈Rn×1. Unit: [rad].

Definition at line 29 of file safety.hpp.

◆ q_min
std::vector<double> flexiv::rdk::SafetyLimits::q_min = {}
Lower safety limits of joint positions: qmin∈Rn×1. Unit: [rad].

Definition at line 25 of file safety.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/safety.hpp


flexiv::rdk::Scheduler Class Reference
Real-time scheduler that can simultaneously run multiple periodic tasks. Parameters for each task are configured independently. More...

#include <scheduler.hpp>

Public Member Functions
 	Scheduler ()
 	[Blocking] Create an instance and initialize the real-time scheduler. More...
 
void 	AddTask (std::function< void(void)> &&callback, const std::string &task_name, int interval, int priority, int cpu_affinity=-1)
 	[Non-blocking] Add a new periodic task to the scheduler's task pool. Each task in the pool is assigned to a dedicated thread with independent thread configuration. More...
 
void 	Start ()
 	[Blocking] Start all added tasks. A dedicated thread will be created for each added task and the periodic execution will begin. More...
 
void 	Stop ()
 	[Blocking] Stop all added tasks. The periodic execution will stop and all task threads will be closed with the resources released. More...
 
int 	max_priority () const
 	[Non-blocking] Get maximum available priority for user tasks. More...
 
int 	min_priority () const
 	[Non-blocking] Get minimum available priority for user tasks. More...
 
size_t 	num_tasks () const
 	[Non-blocking] Get number of tasks added to the scheduler. More...
 
Detailed Description
Real-time scheduler that can simultaneously run multiple periodic tasks. Parameters for each task are configured independently.

Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
Definition at line 21 of file scheduler.hpp.

Constructor & Destructor Documentation
◆ Scheduler()
flexiv::rdk::Scheduler::Scheduler	(		)	
[Blocking] Create an instance and initialize the real-time scheduler.

Exceptions
std::runtime_error	if the initialization sequence failed.
Warning
This constructor blocks until the initialization sequence is successfully finished.
Member Function Documentation
◆ AddTask()
void flexiv::rdk::Scheduler::AddTask	(	std::function< void(void)> && 	callback,
const std::string & 	task_name,
int 	interval,
int 	priority,
int 	cpu_affinity = -1 
)		
[Non-blocking] Add a new periodic task to the scheduler's task pool. Each task in the pool is assigned to a dedicated thread with independent thread configuration.

Parameters
[in]	callback	Callback function of user task.
[in]	task_name	A unique name for this task.
[in]	interval	Execution interval of this periodic task [ms]. The minimum available interval is 1 ms, equivalent to 1 kHz loop frequency.
[in]	priority	Priority for this task thread, can be set to min_priority()–max_priority() for real-time scheduling, or 0 for non-real-time scheduling. When the priority is set to use real-time scheduling, this thread becomes a real-time thread and can only be interrupted by threads with higher priority. When the priority is set to use non-real-time scheduling (i.e. 0), this thread becomes a non-real-time thread and can be interrupted by any real-time threads. The common practice is to set priority of the most critical tasks to max_priority() or near, and set priority of other non-critical tasks to 0 or near. To avoid race conditions, the same priority should be assigned to only one task.
[in]	cpu_affinity	CPU core for this task thread to bind to, can be set to 2–(num_cores
1). This task thread will only run on the specified CPU core. If left with the default value (-1), then this task thread will not bind to any CPU core, and the system will decide which core to run this task thread on according to the system's own strategy. The common practice is to bind the high-priority task to a dedicated spare core, and bind low-priority tasks to other cores or just leave them unbound (cpu_affinity = -1).
Exceptions
std::logic_error	if the scheduler is already started or is not fully initialized yet.
std::invalid_argument	if the specified interval/priority/affinity is invalid or the specified task name is duplicate.
std::runtime_error	if an error is triggered by the client computer.
Note
Setting CPU affinity on macOS has no effect, as its Mach kernel takes full control of thread placement so CPU binding is not supported.
Warning
Calling this function after start() is not allowed.
For maximum scheduling performance, setting CPU affinity to 0 or 1 is not allowed: core 0 is usually the default core for system processes and can be crowded; core 1 is reserved for the scheduler itself.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ max_priority()
int flexiv::rdk::Scheduler::max_priority	(		)	const
[Non-blocking] Get maximum available priority for user tasks.

Returns
The maximum priority that can be set for a user task with real-time scheduling policy when calling AddTask().
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ min_priority()
int flexiv::rdk::Scheduler::min_priority	(		)	const
[Non-blocking] Get minimum available priority for user tasks.

Returns
The minimum priority that can be set for a user task with real-time scheduling policy when calling AddTask().
◆ num_tasks()
size_t flexiv::rdk::Scheduler::num_tasks	(		)	const
[Non-blocking] Get number of tasks added to the scheduler.

Returns
Number of added tasks.
◆ Start()
void flexiv::rdk::Scheduler::Start	(		)	
[Blocking] Start all added tasks. A dedicated thread will be created for each added task and the periodic execution will begin.

Exceptions
std::logic_error	if the scheduler is not initialized yet.
std::runtime_error	if failed to start the tasks.
Note
This function blocks until all added tasks are started.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ Stop()
void flexiv::rdk::Scheduler::Stop	(		)	
[Blocking] Stop all added tasks. The periodic execution will stop and all task threads will be closed with the resources released.

Exceptions
std::logic_error	if the scheduler is not initialized or the tasks are not started yet.
std::runtime_error	if failed to stop the tasks.
Note
Calling start() again can restart the added tasks.
This function blocks until all task threads have exited and resources are released.
Warning
This function cannot be called from within a task thread.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
The documentation for this class was generated from the following file:
include/flexiv/rdk/scheduler.hpp



flexiv::rdk::Scheduler Class Reference
Real-time scheduler that can simultaneously run multiple periodic tasks. Parameters for each task are configured independently. More...

#include <scheduler.hpp>

Public Member Functions
 	Scheduler ()
 	[Blocking] Create an instance and initialize the real-time scheduler. More...
 
void 	AddTask (std::function< void(void)> &&callback, const std::string &task_name, int interval, int priority, int cpu_affinity=-1)
 	[Non-blocking] Add a new periodic task to the scheduler's task pool. Each task in the pool is assigned to a dedicated thread with independent thread configuration. More...
 
void 	Start ()
 	[Blocking] Start all added tasks. A dedicated thread will be created for each added task and the periodic execution will begin. More...
 
void 	Stop ()
 	[Blocking] Stop all added tasks. The periodic execution will stop and all task threads will be closed with the resources released. More...
 
int 	max_priority () const
 	[Non-blocking] Get maximum available priority for user tasks. More...
 
int 	min_priority () const
 	[Non-blocking] Get minimum available priority for user tasks. More...
 
size_t 	num_tasks () const
 	[Non-blocking] Get number of tasks added to the scheduler. More...
 
Detailed Description
Real-time scheduler that can simultaneously run multiple periodic tasks. Parameters for each task are configured independently.

Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
Definition at line 21 of file scheduler.hpp.

Constructor & Destructor Documentation
◆ Scheduler()
flexiv::rdk::Scheduler::Scheduler	(		)	
[Blocking] Create an instance and initialize the real-time scheduler.

Exceptions
std::runtime_error	if the initialization sequence failed.
Warning
This constructor blocks until the initialization sequence is successfully finished.
Member Function Documentation
◆ AddTask()
void flexiv::rdk::Scheduler::AddTask	(	std::function< void(void)> && 	callback,
const std::string & 	task_name,
int 	interval,
int 	priority,
int 	cpu_affinity = -1 
)		
[Non-blocking] Add a new periodic task to the scheduler's task pool. Each task in the pool is assigned to a dedicated thread with independent thread configuration.

Parameters
[in]	callback	Callback function of user task.
[in]	task_name	A unique name for this task.
[in]	interval	Execution interval of this periodic task [ms]. The minimum available interval is 1 ms, equivalent to 1 kHz loop frequency.
[in]	priority	Priority for this task thread, can be set to min_priority()–max_priority() for real-time scheduling, or 0 for non-real-time scheduling. When the priority is set to use real-time scheduling, this thread becomes a real-time thread and can only be interrupted by threads with higher priority. When the priority is set to use non-real-time scheduling (i.e. 0), this thread becomes a non-real-time thread and can be interrupted by any real-time threads. The common practice is to set priority of the most critical tasks to max_priority() or near, and set priority of other non-critical tasks to 0 or near. To avoid race conditions, the same priority should be assigned to only one task.
[in]	cpu_affinity	CPU core for this task thread to bind to, can be set to 2–(num_cores
1). This task thread will only run on the specified CPU core. If left with the default value (-1), then this task thread will not bind to any CPU core, and the system will decide which core to run this task thread on according to the system's own strategy. The common practice is to bind the high-priority task to a dedicated spare core, and bind low-priority tasks to other cores or just leave them unbound (cpu_affinity = -1).
Exceptions
std::logic_error	if the scheduler is already started or is not fully initialized yet.
std::invalid_argument	if the specified interval/priority/affinity is invalid or the specified task name is duplicate.
std::runtime_error	if an error is triggered by the client computer.
Note
Setting CPU affinity on macOS has no effect, as its Mach kernel takes full control of thread placement so CPU binding is not supported.
Warning
Calling this function after start() is not allowed.
For maximum scheduling performance, setting CPU affinity to 0 or 1 is not allowed: core 0 is usually the default core for system processes and can be crowded; core 1 is reserved for the scheduler itself.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ max_priority()
int flexiv::rdk::Scheduler::max_priority	(		)	const
[Non-blocking] Get maximum available priority for user tasks.

Returns
The maximum priority that can be set for a user task with real-time scheduling policy when calling AddTask().
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ min_priority()
int flexiv::rdk::Scheduler::min_priority	(		)	const
[Non-blocking] Get minimum available priority for user tasks.

Returns
The minimum priority that can be set for a user task with real-time scheduling policy when calling AddTask().
◆ num_tasks()
size_t flexiv::rdk::Scheduler::num_tasks	(		)	const
[Non-blocking] Get number of tasks added to the scheduler.

Returns
Number of added tasks.
◆ Start()
void flexiv::rdk::Scheduler::Start	(		)	
[Blocking] Start all added tasks. A dedicated thread will be created for each added task and the periodic execution will begin.

Exceptions
std::logic_error	if the scheduler is not initialized yet.
std::runtime_error	if failed to start the tasks.
Note
This function blocks until all added tasks are started.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
◆ Stop()
void flexiv::rdk::Scheduler::Stop	(		)	
[Blocking] Stop all added tasks. The periodic execution will stop and all task threads will be closed with the resources released.

Exceptions
std::logic_error	if the scheduler is not initialized or the tasks are not started yet.
std::runtime_error	if failed to stop the tasks.
Note
Calling start() again can restart the added tasks.
This function blocks until all task threads have exited and resources are released.
Warning
This function cannot be called from within a task thread.
Examples
intermediate1_realtime_joint_position_control.cpp, intermediate2_realtime_joint_impedance_control.cpp, intermediate3_realtime_joint_torque_control.cpp, intermediate4_realtime_joint_floating.cpp, intermediate5_realtime_cartesian_pure_motion_control.cpp, and intermediate6_realtime_cartesian_motion_force_control.cpp.
The documentation for this class was generated from the following file:
include/flexiv/rdk/scheduler.hpp


flexiv::rdk::Tool Class Reference
Interface to online update and interact with the robot tools. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes. More...

#include <tool.hpp>

Public Member Functions
 	Tool (const Robot &robot)
 	[Non-blocking] Create an instance and initialize the interface. More...
 
const std::vector< std::string > 	list () const
 	[Blocking] Get a name list of all configured tools. More...
 
const std::string 	name () const
 	[Blocking] Get name of the tool that the robot is currently using. More...
 
bool 	exist (const std::string &name) const
 	[Blocking] Whether the specified tool already exists. More...
 
const ToolParams 	params () const
 	[Blocking] Get parameters of the tool that the robot is currently using. More...
 
const ToolParams 	params (const std::string &name) const
 	[Blocking] Get parameters of the specified tool. More...
 
void 	Add (const std::string &name, const ToolParams &params)
 	[Blocking] Add a new tool with user-specified parameters. More...
 
void 	Switch (const std::string &name)
 	[Blocking] Switch to an existing tool. All following robot operations will default to use this tool. More...
 
void 	Update (const std::string &name, const ToolParams &params)
 	[Blocking] Update the parameters of an existing tool. More...
 
void 	Remove (const std::string &name)
 	[Blocking] Remove an existing tool. More...
 
Detailed Description
Interface to online update and interact with the robot tools. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes.

Examples
basics6_gripper_control.cpp, and basics8_update_robot_tool.cpp.
Definition at line 41 of file tool.hpp.

Constructor & Destructor Documentation
◆ Tool()
flexiv::rdk::Tool::Tool	(	const Robot & 	robot	)	
[Non-blocking] Create an instance and initialize the interface.

Parameters
[in]	robot	Reference to the instance of flexiv::rdk::Robot.
Exceptions
std::runtime_error	if the initialization sequence failed.
Member Function Documentation
◆ Add()
void flexiv::rdk::Tool::Add	(	const std::string & 	name,
const ToolParams & 	params 
)		
[Blocking] Add a new tool with user-specified parameters.

Parameters
[in]	name	Name of the new tool, must be unique.
[in]	params	Parameters of the new tool.
Exceptions
std::logic_error	if robot is not in the correct control mode or the specified tool already exists.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
◆ exist()
bool flexiv::rdk::Tool::exist	(	const std::string & 	name	)	const
[Blocking] Whether the specified tool already exists.

Parameters
[in]	name	Name of the tool to check.
Returns
True if the specified tool exists.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ list()
const std::vector<std::string> flexiv::rdk::Tool::list	(		)	const
[Blocking] Get a name list of all configured tools.

Returns
Tool names as a string list.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ name()
const std::string flexiv::rdk::Tool::name	(		)	const
[Blocking] Get name of the tool that the robot is currently using.

Returns
Name of the current tool. Return "Flange" if there's no active tool.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ params() [1/2]
const ToolParams flexiv::rdk::Tool::params	(		)	const
[Blocking] Get parameters of the tool that the robot is currently using.

Returns
ToolParams value copy.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ params() [2/2]
const ToolParams flexiv::rdk::Tool::params	(	const std::string & 	name	)	const
[Blocking] Get parameters of the specified tool.

Parameters
[in]	name	Name of the tool to get parameters for, must be an existing one.
Returns
ToolParams value copy.
Exceptions
std::logic_error	if the specified tool does not exist.
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ Remove()
void flexiv::rdk::Tool::Remove	(	const std::string & 	name	)	
[Blocking] Remove an existing tool.

Parameters
[in]	name	Name of the tool to remove, must be an existing one but cannot be "Flange".
Exceptions
std::logic_error	if robot is not in the correct control mode or the specified tool does not exist or trying to remove "Flange".
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
◆ Switch()
void flexiv::rdk::Tool::Switch	(	const std::string & 	name	)	
[Blocking] Switch to an existing tool. All following robot operations will default to use this tool.

Parameters
[in]	name	Name of the tool to switch to, must be an existing one.
Exceptions
std::logic_error	if robot is not in the correct control mode or the specified tool does not exist.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
◆ Update()
void flexiv::rdk::Tool::Update	(	const std::string & 	name,
const ToolParams & 	params 
)		
[Blocking] Update the parameters of an existing tool.

Parameters
[in]	name	Name of the tool to update, must be an existing one.
[in]	params	New parameters for the specified tool.
Exceptions
std::logic_error	if robot is not in the correct control mode or the specified tool does not exist.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
The documentation for this class was generated from the following file:
include/flexiv/rdk/tool.hpp


flexiv::rdk::ToolParams Struct Reference
Data structure containing robot tool parameters. More...

#include <tool.hpp>

Public Attributes
double 	mass = 0.0
 
std::array< double, 3 > 	CoM = {}
 
std::array< double, 6 > 	inertia = {}
 
std::array< double, kPoseSize > 	tcp_location = {}
 
Detailed Description
Data structure containing robot tool parameters.

See also
Tool::params().
Examples
basics8_update_robot_tool.cpp.
Definition at line 19 of file tool.hpp.

Member Data Documentation
◆ CoM
std::array<double, 3> flexiv::rdk::ToolParams::CoM = {}
Center of mass in robot flange frame: [x,y,z]. Unit: [m]

Examples
basics8_update_robot_tool.cpp.
Definition at line 25 of file tool.hpp.

◆ inertia
std::array<double, 6> flexiv::rdk::ToolParams::inertia = {}
Inertia at center of mass: [Ixx,Iyy,Izz,Ixy,Ixz,Iyz]. Unit: [kgm2]

Examples
basics8_update_robot_tool.cpp.
Definition at line 28 of file tool.hpp.

◆ mass
double flexiv::rdk::ToolParams::mass = 0.0
Total mass. Unit: [kg]

Examples
basics8_update_robot_tool.cpp.
Definition at line 22 of file tool.hpp.

◆ tcp_location
std::array<double, kPoseSize> flexiv::rdk::ToolParams::tcp_location = {}
Position and orientation of the tool center point (TCP) in flange frame. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[]

Examples
basics8_update_robot_tool.cpp.
Definition at line 33 of file tool.hpp.

The documentation for this struct was generated from the following file:
include/flexiv/rdk/tool.hpp


flexiv::rdk::WorkCoord Class Reference
Interface to online update and interact with the robot's work coordinates. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes. More...

#include <work_coord.hpp>

Public Member Functions
 	WorkCoord (const Robot &robot)
 	[Non-blocking] Create an instance and initialize the interface. More...
 
const std::vector< std::string > 	list () const
 	[Blocking] Get a name list of all configured work coordinates. More...
 
bool 	exist (const std::string &name) const
 	[Blocking] Whether the specified work coordinate already exists. More...
 
const std::array< double, kPoseSize > 	pose (const std::string &name) const
 	[Blocking] Get pose of an existing work coordinate. More...
 
void 	Add (const std::string &name, const std::array< double, kPoseSize > &pose)
 	[Blocking] Add a new work coordinate with user-specified parameters. More...
 
void 	Update (const std::string &name, const std::array< double, kPoseSize > &pose)
 	[Blocking] Update the pose of an existing work coordinate. More...
 
void 	Remove (const std::string &name)
 	[Blocking] Remove an existing work coordinate. More...
 
Detailed Description
Interface to online update and interact with the robot's work coordinates. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes.

Definition at line 20 of file work_coord.hpp.

Constructor & Destructor Documentation
◆ WorkCoord()
flexiv::rdk::WorkCoord::WorkCoord	(	const Robot & 	robot	)	
[Non-blocking] Create an instance and initialize the interface.

Parameters
[in]	robot	Reference to the instance of flexiv::rdk::Robot.
Exceptions
std::runtime_error	if the initialization sequence failed.
Member Function Documentation
◆ Add()
void flexiv::rdk::WorkCoord::Add	(	const std::string & 	name,
const std::array< double, kPoseSize > & 	pose 
)		
[Blocking] Add a new work coordinate with user-specified parameters.

Parameters
[in]	name	Name of the new work coordinate, must be unique.
[in]	pose	Pose of the new work coordinate in world frame: OTwork∈R7×1. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[].
Exceptions
std::logic_error	if robot is not in the correct control mode or the specified work coordinate already exists.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
◆ exist()
bool flexiv::rdk::WorkCoord::exist	(	const std::string & 	name	)	const
[Blocking] Whether the specified work coordinate already exists.

Parameters
[in]	name	Name of the tool to check.
Returns
True if the specified tool exists.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ list()
const std::vector<std::string> flexiv::rdk::WorkCoord::list	(		)	const
[Blocking] Get a name list of all configured work coordinates.

Returns
Work coordinate names as a string list.
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ pose()
const std::array<double, kPoseSize> flexiv::rdk::WorkCoord::pose	(	const std::string & 	name	)	const
[Blocking] Get pose of an existing work coordinate.

Parameters
[in]	name	Name of the work coordinate to get pose for, must be an existing one.
Returns
Pose of the work coordinate in world frame: OTwork∈R7×1. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[].
Exceptions
std::runtime_error	if failed to get a reply from the connected robot.
Note
This function blocks until a reply is received.
◆ Remove()
void flexiv::rdk::WorkCoord::Remove	(	const std::string & 	name	)	
[Blocking] Remove an existing work coordinate.

Parameters
[in]	name	Name of the work coordinate to remove, must be an existing one.
Exceptions
std::logic_error	if robot is not in the correct control mode or the specified work coordinate does not exist.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
◆ Update()
void flexiv::rdk::WorkCoord::Update	(	const std::string & 	name,
const std::array< double, kPoseSize > & 	pose 
)		
[Blocking] Update the pose of an existing work coordinate.

Parameters
[in]	name	Name of the work coordinate to update, must be an existing one.
[in]	pose	New pose for the specified work coordinate in world frame: OTwork∈R7×1. Consists of R3×1 position and R4×1 quaternion: [x,y,z,qw,qx,qy,qz]T. Unit: [m]:[].
Exceptions
std::logic_error	if robot is not in the correct control mode or the specified work coordinate does not exist.
std::runtime_error	if failed to deliver the request to the connected robot.
Note
Applicable control modes: IDLE.
This function blocks until the request is successfully delivered.
The documentation for this class was generated from the following file:
include/flexiv/rdk/work_coord.hpp



Pose Struct Reference
Public Attributes
double 	x
 
double 	y
 
double 	z
 
double 	roll
 
double 	pitch
 
double 	yaw
 
Detailed Description
Definition at line 27 of file Demo.cpp.

The documentation for this struct was generated from the following file:
example/Demo.cpp



Pose6D Struct Reference
Collaboration graph
[legend]
Public Attributes
Vector3 	position
 
Vector3 	rotation
 
Detailed Description
Definition at line 45 of file DemoReal.cpp.

The documentation for this struct was generated from the following file:
example/DemoReal.cpp


Vector3 Struct Reference
Public Member Functions
Vector3 	operator- (const Vector3 &other) const
 
double 	dot (const Vector3 &other) const
 
Vector3 	cross (const Vector3 &other) const
 
Vector3 	normalized () const
 
Public Attributes
double 	x
 
double 	y
 
double 	z
 
Detailed Description
Definition at line 15 of file DemoReal.cpp.

The documentation for this struct was generated from the following file:
example/DemoReal.cpp
