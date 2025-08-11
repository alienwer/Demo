---
title: Flexiv RDK Manual
date: 2025-03-25T14:08:48Z
lastmod: 2025-03-25T14:28:39Z
---
# Flexiv RDK Manual

[[RDK Home Page]](https://www.flexiv.com/software/rdk/)

Flexiv RDK (Robotic Development Kit), a key component of the Flexiv Robotic Software Platform, is a powerful development toolkit that enables the users to create complex and customized robotic applications using APIs that provide both low-level real-time (RT) and high-level non-real-time (NRT) access to Flexiv robots.

All functionalities of Flexiv RDK are packed into the [[flexiv_rdk] repository](https://github.com/flexivrobotics/flexiv_rdk/).

Important

Before using the robot with Flexiv RDK, you must carefully read through all documents shipped with the robot as well as this manual, and strictly follow **all safety instructions** detailed in these documents.

## Table of contents

Overview

* [What Is Flexiv RDK?](https://www.flexiv.com/software/rdk/manual/what_is_rdk.html)

  * [Example workflow of a complex user application](https://www.flexiv.com/software/rdk/manual/what_is_rdk.html#example-workflow-of-a-complex-user-application)
* [Key Features](https://www.flexiv.com/software/rdk/manual/key_features.html)
* [Environment Compatibility](https://www.flexiv.com/software/rdk/manual/environment_compatibility.html)
* [System Requirements](https://www.flexiv.com/software/rdk/manual/system_requirements.html)
* [Robot Software Compatibility](https://www.flexiv.com/software/rdk/manual/robot_software_compatibility.html)

  * [RDK v1.x](https://www.flexiv.com/software/rdk/manual/robot_software_compatibility.html#rdk-v1-x)
  * [RDK v0.x](https://www.flexiv.com/software/rdk/manual/robot_software_compatibility.html#rdk-v0-x)
* [Release Notes](https://www.flexiv.com/software/rdk/manual/release_notes.html)

Installation

* [Download Flexiv RDK](https://www.flexiv.com/software/rdk/manual/download_rdk.html)
* [Install for C++](https://www.flexiv.com/software/rdk/manual/install_for_cpp.html)

  * [Prepare build tools](https://www.flexiv.com/software/rdk/manual/install_for_cpp.html#prepare-build-tools)
  * [Install dependencies](https://www.flexiv.com/software/rdk/manual/install_for_cpp.html#install-dependencies)
  * [Install RDK library](https://www.flexiv.com/software/rdk/manual/install_for_cpp.html#install-rdk-library)
  * [Use the installed library](https://www.flexiv.com/software/rdk/manual/install_for_cpp.html#use-the-installed-library)
* [Install for Python](https://www.flexiv.com/software/rdk/manual/install_for_python.html)

  * [Install dependencies](https://www.flexiv.com/software/rdk/manual/install_for_python.html#install-dependencies)
  * [Install RDK library](https://www.flexiv.com/software/rdk/manual/install_for_python.html#install-rdk-library)
  * [Use the installed library](https://www.flexiv.com/software/rdk/manual/install_for_python.html#use-the-installed-library)
  * [Reference - Install multiple versions of Python](https://www.flexiv.com/software/rdk/manual/install_for_python.html#reference-install-multiple-versions-of-python)
* [Real-time Ubuntu (optional)](https://www.flexiv.com/software/rdk/manual/realtime_ubuntu.html)

  * [Do I need a real-time OS?](https://www.flexiv.com/software/rdk/manual/realtime_ubuntu.html#do-i-need-a-real-time-os)
  * [Ubuntu 22.04/24.04 - Enable via Pro subscription](https://www.flexiv.com/software/rdk/manual/realtime_ubuntu.html#ubuntu-22-04-24-04-enable-via-pro-subscription)
  * [Ubuntu 20.04 - Manually patch the real-time kernel](https://www.flexiv.com/software/rdk/manual/realtime_ubuntu.html#ubuntu-20-04-manually-patch-the-real-time-kernel)

First Time Setup

* [Set Up the Robot](https://www.flexiv.com/software/rdk/manual/set_up_the_robot.html)

  * [Light it up!](https://www.flexiv.com/software/rdk/manual/set_up_the_robot.html#light-it-up)
  * [Connect the UI tablet](https://www.flexiv.com/software/rdk/manual/set_up_the_robot.html#connect-the-ui-tablet)
* [Activate RDK Server](https://www.flexiv.com/software/rdk/manual/activate_rdk_server.html)

  * [Configure license](https://www.flexiv.com/software/rdk/manual/activate_rdk_server.html#configure-license)
  * [Enable Remote mode for RDK](https://www.flexiv.com/software/rdk/manual/activate_rdk_server.html#enable-remote-mode-for-rdk)
* [Enter and Exit Remote Mode](https://www.flexiv.com/software/rdk/manual/enter_and_exit_remote_mode.html)

  * [Enter Remote mode](https://www.flexiv.com/software/rdk/manual/enter_and_exit_remote_mode.html#enter-remote-mode)
  * [Exit Remote mode](https://www.flexiv.com/software/rdk/manual/enter_and_exit_remote_mode.html#exit-remote-mode)
* [Establish Connection](https://www.flexiv.com/software/rdk/manual/establish_connection.html)
* [Verify with Example Programs](https://www.flexiv.com/software/rdk/manual/verify_with_example_programs.html)

  * [Run an example C++ program](https://www.flexiv.com/software/rdk/manual/verify_with_example_programs.html#run-an-example-c-program)
  * [Run an example Python program](https://www.flexiv.com/software/rdk/manual/verify_with_example_programs.html#run-an-example-python-program)

Flexiv RDK

* [API Overview](https://www.flexiv.com/software/rdk/manual/api_overview.html)

  * [Available APIs](https://www.flexiv.com/software/rdk/manual/api_overview.html#available-apis)
  * [Access by OS and programming language](https://www.flexiv.com/software/rdk/manual/api_overview.html#access-by-os-and-programming-language)
  * [API documentation](https://www.flexiv.com/software/rdk/manual/api_overview.html#api-documentation)
* [Control Modes](https://www.flexiv.com/software/rdk/manual/control_modes.html)

  * [Real-time (RT) modes](https://www.flexiv.com/software/rdk/manual/control_modes.html#real-time-rt-modes)
  * [Non-real-time (NRT) modes](https://www.flexiv.com/software/rdk/manual/control_modes.html#non-real-time-nrt-modes)
  * [Idle mode (](https://www.flexiv.com/software/rdk/manual/control_modes.html#idle-mode)[`Mode::IDLE`](https://www.flexiv.com/software/rdk/manual/control_modes.html#idle-mode)[)](https://www.flexiv.com/software/rdk/manual/control_modes.html#idle-mode)
  * [Switch control modes](https://www.flexiv.com/software/rdk/manual/control_modes.html#switch-control-modes)
* [Robot States](https://www.flexiv.com/software/rdk/manual/robot_states.html)
* [Robot Description (URDF)](https://www.flexiv.com/software/rdk/manual/robot_description.html)
* [Digital I/O Control](https://www.flexiv.com/software/rdk/manual/digital_io_control.html)
* [Loss of Connection](https://www.flexiv.com/software/rdk/manual/loss_of_connection.html)

  * [Automatic stop](https://www.flexiv.com/software/rdk/manual/loss_of_connection.html#automatic-stop)
  * [Hot reconnection](https://www.flexiv.com/software/rdk/manual/loss_of_connection.html#hot-reconnection)
* [Free Drive](https://www.flexiv.com/software/rdk/manual/free_drive.html)

  * [Invoke directly from RDK](https://www.flexiv.com/software/rdk/manual/free_drive.html#invoke-directly-from-rdk)
  * [Invoke from Flexiv Elements](https://www.flexiv.com/software/rdk/manual/free_drive.html#invoke-from-flexiv-elements)

Troubleshooting

* [Frequently Asked Questions](https://www.flexiv.com/software/rdk/manual/faq.html)

  * [Where can I download Flexiv RDK?](https://www.flexiv.com/software/rdk/manual/faq.html#where-can-i-download-flexiv-rdk)
  * [What OS and programming languages does RDK support?](https://www.flexiv.com/software/rdk/manual/faq.html#what-os-and-programming-languages-does-rdk-support)
  * [Where can I see which version of robot software is compatible with a given RDK version?](https://www.flexiv.com/software/rdk/manual/faq.html#where-can-i-see-which-version-of-robot-software-is-compatible-with-a-given-rdk-version)
  * [What features are available in the current version of RDK?](https://www.flexiv.com/software/rdk/manual/faq.html#what-features-are-available-in-the-current-version-of-rdk)
  * [It seems something was wrong and the robot is not doing what I commanded, how can I check what happened?](https://www.flexiv.com/software/rdk/manual/faq.html#it-seems-something-was-wrong-and-the-robot-is-not-doing-what-i-commanded-how-can-i-check-what-happened)
  * [Can I clear robot faults via RDK?](https://www.flexiv.com/software/rdk/manual/faq.html#can-i-clear-robot-faults-via-rdk)
  * [How can I access the external force and moment applied to the end-effector?](https://www.flexiv.com/software/rdk/manual/faq.html#how-can-i-access-the-external-force-and-moment-applied-to-the-end-effector)
  * [How can I free drive the robot when using RDK?](https://www.flexiv.com/software/rdk/manual/faq.html#how-can-i-free-drive-the-robot-when-using-rdk)
  * [I toggled the Auto/Manual slide switch on the motion bar, and now RDK is not working, how to solve this?](https://www.flexiv.com/software/rdk/manual/faq.html#i-toggled-the-auto-manual-slide-switch-on-the-motion-bar-and-now-rdk-is-not-working-how-to-solve-this)
  * [Where can I find the robot kinematics?](https://www.flexiv.com/software/rdk/manual/faq.html#where-can-i-find-the-robot-kinematics)
* [Error Handling](https://www.flexiv.com/software/rdk/manual/error_handling.html)

  * [Robot fault and error messages](https://www.flexiv.com/software/rdk/manual/error_handling.html#robot-fault-and-error-messages)
  * [Robot operational](https://www.flexiv.com/software/rdk/manual/error_handling.html#robot-operational)
  * [Critical fault](https://www.flexiv.com/software/rdk/manual/error_handling.html#critical-fault)
  * [Minor fault](https://www.flexiv.com/software/rdk/manual/error_handling.html#minor-fault)
  * [Recover from joint position limit violation](https://www.flexiv.com/software/rdk/manual/error_handling.html#recover-from-joint-position-limit-violation)

ROS Bridges

* [ROS 2 Bridge](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html)

  * [Compatibility](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html#compatibility)
  * [Overview](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html#overview)
  * [Environment setup](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html#environment-setup)
  * [Packages](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html#packages)
  * [MoveIt](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html#moveit)
  * [Demos](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html#demos)
* [ROS 1 Bridge](https://www.flexiv.com/software/rdk/manual/ros1_bridge.html)

‍

# What Is Flexiv RDK?

Flexiv RDK is a software development kit (SDK) that enables the users to create their own C++ or Python programs to integrate Flexiv robots with external software and hardware modules, such as additional sensors, industrial control systems, vision and perception units, digital I/O devices, other software libraries, etc.

![_images/rdk_overview.png](https://www.flexiv.com/software/rdk/manual/_images/rdk_overview.png)[https://www.flexiv.com/software/rdk/manual/_images/rdk_overview.png](https://www.flexiv.com/software/rdk/manual/_images/rdk_overview.png)

## Example workflow of a complex user application

A complex and highly customized user application usually requires a series of different operations from one or more robots and a user-defined state machine to manage the operations. This process can be achieved through the combination of various RDK APIs.

Using information obtained from sources like external sensors, digital inputs, robot states, etc. of one or more robots, check conditions can be created to trigger transitions in the user state machine, which will then put the robot(s) into suitable modes and issue commands accordingly. Below is an example workflow:

1. In one user program, two RDK library instances are initialized to establish connection with robot A and B respectively via two network cards, and both robots are enabled and operational.
2. Robot A task 1: go home. This is a unit skill (primitive) that the robot already knows, then [Primitive execution mode (Mode::NRT_PRIMITIVE_EXECUTION)](https://www.flexiv.com/software/rdk/manual/control_modes.html#primitive-mode) can be used here. When the termination condition is met for this task, the user state machine commands robot A to stop and wait for further instruction.
3. Robot B task 1: when robot A is stopped, compliantly follow the output from a user-defined real-time trajectory generator with user-specified stiffness. A tray is mounted on the end effector, and a cube with an april tag on it is in the tray. For this task, it’s best to use the [RT Cartesian motion-force control mode (Mode::RT_CARTESIAN_MOTION_FORCE)](https://www.flexiv.com/software/rdk/manual/control_modes.html#cart-motion-force-mode). Thus the user state machine will first set robot B into this mode, then continuously command target pose to it.
4. Robot A task 2: assuming a camera is mounted on robot A and the user has implemented an april tag tracker program that can provide RDK with the grasping pose based on the estimated tag pose, when the camera on robot A sees the cube with april tag from robot B, the user state machine commands robot B to stop, then commands robot A to grasp that cube. In this case, the `MoveL` primitive can be used to command robot A to smoothly move to the grasping pose, then use methods from the `flexiv::Gripper` API to control a gripper to finish the grasping.
5. Robot B task 2: …

‍

# Key Features

Flexiv RDK is feature-rich and provides a wide variety of functionalities. Below is a list of key features and descriptions. Keep exploring to harness the full potential of RDK.

| Feature                        | Summary                                                                                                                                    |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| RT operations                  | The robot can execute low-level commands like joint torques, joint positions, Cartesian pose, etc. at 1kHz.                                |
| NRT operations                 | The robot can execute high-level commands like plans, primitives, digital IO, etc. as well as NRT motion commands.                         |
| RT states feedback             | The robot sends back states data at 1kHz no matter what control mode is being used.                                                        |
| Gripper control                | Control any supported gripper connected to the robot.                                                                                      |
| Device interface               | Enable, disable, and send generic commands to any supported device connected to the robot.                                                 |
| Tool interface                 | Add, remove, edit, switch, and get parameters of robot end-effector tools.                                                                 |
| Timeliness monitor             | When in a RT control mode, the robot server automatically checks if the user command arrives in time at 1kHz.                              |
| Unix real-time scheduler       | User tasks added to this scheduler are executed periodically with adjustable execution interval and priority.                              |
| Kinematics and dynamics engine | Provide users with run-time access to important robot kinematics and dynamics data like Jacobian, mass matrix, gravity, reachability, etc. |
| Portable libraries             | Self-contained C++ and Python libraries for various OS and CPU platforms, compatible with other third-party libraries.                     |
| Example pool                   | Plenty of informative and instructive examples covering almost every aspect of Flexiv RDK to help users get started quickly.               |
| Robot description              | Kinematics-only URDF and 3D mesh files of the robot for visualizers and simulators.                                                        |
| Cross-platform                 | Besides Linux, RDK also supports Windows and macOS.                                                                                        |
| ARM processor support          | Besides x86\_64, RDK also supports arm64 processors.                                                                                       |

(RT: real-time, NRT: non-real-time)

‍

# Environment Compatibility

The following computer environments are supported to run Flexiv RDK.

| OS                             | Platform       | C++ compiler kit | Python interpreter |
| ------------------------------ | -------------- | ---------------- | ------------------ |
| Linux (Ubuntu 20.04 and above) | x86\_64, arm64 | GCC v9.4+        | 3.8, 3.10, 3.12    |
| macOS 12 and above             | arm64          | Clang v14.0+     | 3.10, 3.12         |
| Windows 10 and above           | x86\_64        | MSVC v14.2+      | 3.8, 3.10, 3.12    |

‍

# System Requirements

Minimum requirements for **real-time** controls of the robot:

| **Workstation PC** |                                                |
| ------------------------ | ---------------------------------------------- |
| Operating system         | macOS or Linux (real-time kernel optional\*)   |
| CPU platform             | x86\_64 or arm64                               |
| CPU performance          | Depends on computation load of user program    |
| **Network**        |                                                |
| Nodes                    | 1 workstation PC and 1 or more robot server(s) |
| Connection               | Wired LAN                                      |
| Latency                  | Round trip\< 1 ms                              |
| Bandwidth                | Send/receive both ways\> 5.0 MiB/s             |

\*See details in section [Real-time Ubuntu (optional)](https://www.flexiv.com/software/rdk/manual/realtime_ubuntu.html).

Minimum requirements for **non-real-time** controls of the robot:

| **Workstation PC** |                                                |
| ------------------------ | ---------------------------------------------- |
| Operating system         | All supported OS                               |
| CPU platform             | x86\_64 or arm64                               |
| CPU performance          | Depends on computation load of user program    |
| **Network**        |                                                |
| Nodes                    | 1 workstation PC and 1 or more robot server(s) |
| Connection               | Wired or wireless LAN                          |
| Latency                  | Round trip\< 1000 ms                           |
| Bandwidth                | Send/receive both ways\> 1.0 MiB/s             |

‍

‍

# Robot Software Compatibility

During initialization, Flexiv RDK will check compatibility with the connected robot. An error will occur if software version of the connected robot is incompatible with RDK version. The tables below show the compatible robot software version for a given RDK version.

## RDK v1.x

| RDK version | Robot software version | Release date |
| ----------- | ---------------------- | ------------ |
| v1.6        | v3.8                   | 2025-01-09   |
| v1.5.1      | v3.7.1                 | 2024-12-06   |
| v1.5        | v3.7                   | 2024-11-13   |
| v1.4        | v3.6                   | 2024-07-15   |

## RDK v0.x

| RDK version | Robot software version | Release date |
| ----------- | ---------------------- | ------------ |
| v0.10       | v2.11.5                | 2024-04-30   |
| v0.9.1      | v2.11.3                | 2024-01-06   |
| v0.9        | v2.11.3                | 2023-11-28   |
| v0.8        | v2.10.5                | 2023-05-02   |
| v0.7        | v2.10.3, v2.10.4       | 2023-01-11   |
| v0.6.1      | v2.10.1, v2.10.2       | 2022-10-02   |
| v0.6        | v2.10                  | 2022-08-16   |
| v0.5.1      | v2.9                   | 2022-04-29   |
| v0.5        | v2.9                   | 2022-04-13   |
| v0.4        | v2.8.1                 | 2022-01-17   |
| v0.3.1      | v2.8                   | 2021-12-17   |
| v0.2        | v2.7                   | 2021-09-09   |

‍

# Release Notes

The full release notes (changelog) of Flexiv RDK can be found at [https://github.com/flexivrobotics/flexiv_rdk/releases/](https://github.com/flexivrobotics/flexiv_rdk/releases/).

‍

# Download Flexiv RDK

It is recommended to git clone the GitHub repo and checkout to the desired version tag:

```
git clone https://github.com/flexivrobotics/flexiv_rdk.git
git checkout v1.5
```

Alternatively, you can download a zip file from flexiv.com [[download page]](https://www.flexiv.com/software/rdk/updates).

Important

Please refer to [Robot Software Compatibility](https://www.flexiv.com/software/rdk/manual/robot_software_compatibility.html) to confirm the RDK version that’s compatible with the software currently installed in the robot.

‍

# Install for C++

The RDK C++ library is packed into a modern CMake project named `flexiv_rdk`, which can be configured and installed using CMake on all supported platforms.

## Prepare build tools

### Linux

1. Install GCC compiler kit using package manager:

   ```
   sudo apt install build-essential
   ```
2. Install CMake using package manager:

   ```
   sudo apt install cmake
   ```

### macOS

1. Install Clang compiler kit using xcode tool:

   ```
   xcode-select
   ```

   This will invoke the installation of Xcode Command Line Tools, then follow the prompted window to finish the installation.
2. Install CMake using package manager:

   ```
   brew install cmake
   ```

### Windows

1. Install compiler kit: Download and install Microsoft Visual Studio 2019 (MSVC v14.2) or above. Choose “Desktop development with C++” under the *Workloads* tab during installation. You only need to keep the following components for the selected workload:

   > * MSVC … C++ x64/x86 build tools (Latest)
   > * C++ CMake tools for Windows
   > * Windows 10 SDK or Windows 11 SDK, depending on your actual Windows version
   >
2. Install CMake (with GUI): Download `cmake-3.x.x-windows-x86_64.msi` from [CMake download page](https://cmake.org/download/) and install the msi file. The minimum required version is 3.16.3. **Add CMake to system PATH** when prompted, so that `cmake` and `cmake-gui` command can be used from Command Prompt or a bash emulator.
3. Install bash emulator: Download and install [Git for Windows](https://git-scm.com/download/win/), which comes with a bash emulator Git Bash. The following steps are to be carried out in this bash emulator.

## Install dependencies

1. Clone or download `flexiv_rdk` repo following instructions in [Download Flexiv RDK](https://www.flexiv.com/software/rdk/manual/download_rdk.html).
2. Choose a directory for installing RDK C++ library and all its dependencies. This directory can be under system path or not, depending on whether you want RDK to be globally discoverable by CMake. For example, a new folder named `rdk_install` under the home directory.
3. In a new Terminal, run the provided script to compile and install all C++ dependencies to the installation directory chosen in step 2:
   解释

   ```
   cd flexiv_rdk/thirdparty
   bash build_and_install_dependencies.sh ~/rdk_install
   ```

> Note
>
> Internet connection is required for this step.

## Install RDK library

1. After all dependencies are installed, open a new Terminal and configure the `flexiv_rdk` CMake project:

   ```
   cd flexiv_rdk
   mkdir build && cd build
   cmake .. -DCMAKE_INSTALL_PREFIX=~/rdk_install
   ```

> Note
>
> `-D` followed by `CMAKE_INSTALL_PREFIX` sets the absolute path of the installation directory, which should be the one chosen in step 2 above.

2. Install `flexiv_rdk` C++ library to `CMAKE_INSTALL_PREFIX` path, which may or may not be globally discoverable by CMake:

   ```
   cd flexiv_rdk/build
   cmake --build . --target install --config Release
   ```
3. If the installation was successful, the following directories should appear in the `rdk_install` folder:

> * include/flexiv/rdk/
> * lib/cmake/flexiv\_rdk/

## Use the installed library

After the library is installed as `flexiv_rdk` CMake target, it can be linked from any other CMake projects. Using the provided ``flexiv_rdk-examples` `` project for instance:

```
cd flexiv_rdk/example
mkdir build && cd build
cmake .. -DCMAKE_PREFIX_PATH=~/rdk_install
cmake --build . --config Release -j 4
```

Note

`-D` followed by `CMAKE_PREFIX_PATH` tells the user project’s CMake where to find the installed C++ library. This argument can be skipped if the RDK library and its dependencies are installed to a globally discoverable location.

‍

# Install for Python

The RDK Python library is packed into a Python package named `flexivrdk`, which can be installed using `pip` on all supported platforms.

## Install dependencies

Use `pip` module to install the required dependencies for a specific version of Python:

```
python3.x -m pip install numpy spdlog
```

Replace `3.x` with a specific Python version, e.g. 3.10.

## Install RDK library

Use `pip` module to install RDK library for a specific version of Python:

```
python3.x -m pip install flexivrdk
```

## Use the installed library

After the library is installed as `flexivrdk` Python package, it can be imported from any Python script. Test with the following commands in a new Terminal, which should start Flexiv RDK:

```
python3.x
import flexivrdk
robot = flexivrdk.Robot("Rizon4-123456")
```

The program will start searching for a robot with serial number `Rizon4-123456`, and will exit after a couple of seconds if the specified robot is not found in the local network.

## Reference - Install multiple versions of Python

### Linux

To install different versions of Python alongside the system’s native Python, add and use a personal package archive (PPA):

```
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.x
```

When done, this specific version of Python can be invoked from Terminal using `python3.x`:

```
python3.x --version
```

However, the commands above do not install the `pip` package manager for this Python 3.x and it needs to be manually installed:

```
wget https://bootstrap.pypa.io/get-pip.py
python3.x get-pip.py
```

Once it’s finished, you can install a Python package discoverable by the PPA-installed Python 3.x via:

```
python3.x -m pip install <package_name>
```

Warning

The `sudo apt install python3-pip` command only installs `pip` for the system’s native Python, and Python packages installed using this `pip` is not discoverable by other versions of Python.

### macOS

To install different versions of Python alongside the system’s native Python, use Homebrew package manager:

```
brew install python@3.x
```

Replace “3.x” with the actual Python3 version you wish to use. When done, this specific version of Python can be invoked from Terminal using `python3.x`:

```
python3.x --version
```

The package manager module `pip` for this version of Python will also be installed automatically.

### Windows

To install different versions of Python alongside each other, use Microsoft Store. When done, a specific version of Python can be invoked from Terminal using `python3.x`:

```
python3.x --version
```

The package manager module `pip` for this version of Python will also be installed automatically.

‍

# Real-time Ubuntu (optional)

Important

Not all use cases require a real-time OS, please read below to determine if you need it.

## Do I need a real-time OS?

### Yes

Linux real-time kernel is recommended if you require **hard real-time** performance, which means:

* No missed cycle.
* Minimal and stable whole-loop latency (from sending out command to receiving feedback: \~2ms).
* Deterministic program execution with stable cycle time.

But do note that:

* The patching process is tedious and may take hours.
* Successful patching is not guaranteed since some computers may be incompatible with the real-time kernel.

Note

Ubuntu 22.04 users can take advantage of its native real-time kernel support and skip the following manual patching process. To activate the native real-time kernel, follow [this tutorial](https://ubuntu.com/blog/real-time-ubuntu-released).

### No

You can skip the patching and use the generic kernel shipped natively with Linux installation if you only require **soft real-time** performance, which means:

* A small number of missed cycles can be tolerated.
* Relatively greater and less stable whole-loop latency (from sending out command to receiving feedback: 4\~10ms).
* Less deterministic program execution with less stable cycle time.

Or, you only need **non-real-time** access to the robot.

## Ubuntu 22.04/24.04 - Enable via Pro subscription

Ubuntu releases listed in [this page](https://documentation.ubuntu.com/real-time/en/latest/reference/releases/) have native real-time kernel support, and can be easily enabled via a few commands, see full tutorial at [https://ubuntu.com/real-time](https://ubuntu.com/real-time).

Note

Ubuntu Pro subscription is required to enable real-time kernel. The subscription is free for personal use.

## Ubuntu 20.04 - Manually patch the real-time kernel

### Prepare files

In order to control the robot using RDK, the controller program on the workstation PC must run as a *real-time process* under a real-time kernel. We suggest the *PREEMPT_RT* kernel for this purpose due to its balance between ease of use and real-time performance.

Note

There has been reports on issues with NVIDIA graphics card drivers when used with *PREEMPT_RT* kernel. Please refer to NVIDIA’s support forums for installing a driver patch.

Install dependencies:

```
sudo apt install -y git build-essential cmake ncurses-dev xz-utils libssl-dev bc flex libelf-dev bison curl gnupg2
```

A standard Ubuntu installation comes with a generic kernel, you can check the version of your kernel using `uname -r`. It should appear as `x.y.z` where x, y and z are the major, minor and patch digits. In the following, we use Ubuntu 20.04 machine with a `5.11.4` kernel as example.

Real-time kernel patches are only available for selected versions. Please visit [https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/](https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/) to make sure the kernel source named `linux-5.11.4.tar.xz` is available. Then visit [https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/](https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/) to make sure the real-time patch corresponding to the kernel source you are going to use is also available. The version of the kernel source should be the same as the version indicated on the patch. For example, we need to make sure `patch-5.11.4-rt11.patch.xz` is available.

When decided which version to use, download both the source and patch files using:

```
curl -LO https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.11.4.tar.xz
curl -LO https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.11.4.tar.sign
curl -LO https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/5.11/patch-5.11.4-rt11.patch.xz
curl -LO https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/5.11/patch-5.11.4-rt11.patch.sign
```

Unzip the xz packages:

```
xz -dk linux-5.11.4.tar.xz
xz -dk patch-5.11.4-rt11.patch.xz
```

### Verify downloaded files (optional)

To verify the signature of kernel sources, run the following:

```
gpg2 --locate-keys torvalds@kernel.org gregkh@kernel.org
gpg2 --verify linux-5.11.4.tar.sign
```

To verify the patches, please visit [the Linux Foundation Wiki](https://wiki.linuxfoundation.org/realtime/preempt_rt_versions) to search for a key of the author, then run the following:

```
gpg2 --verify patch-5.11.4-rt11.patch.sign
```

### Compile and install real-time kernel

Before compiling the sources, we have to apply the patches:

```
tar xf linux-5.11.4.tar
cd linux-5.11.4
patch -p1 < ../patch-5.11.4-rt11.patch
```

Next, we configure our kernel:

```
make oldconfig
```

A series of questions will pop up, you can select the default option. When asked for the Preemption Model, choose the `Fully Preemptible Kernel`:

```
Preemption Model
1. No Forced Preemption (Server) (PREEMPT_NONE)
> 2. Voluntary Kernel Preemption (Desktop) (PREEMPT_VOLUNTARY)
3. Preemptible Kernel (Low-Latency Desktop) (PREEMPT)
4. Fully Preemptible Kernel (Real-Time) (PREEMPT_RT) (NEW)
choice[1-4?]: 4
```

For all the other questions, press enter to select the default option. Note you can long-press enter to fast-forward all questions with the default option. When done, a file called “.config” will be generated. Before we can compile the kernel, open the “.config” file, find and set the following configuration parameters:

```
CONFIG_SYSTEM_TRUSTED_KEYS = ""
CONFIG_SYSTEM_REVOCATION_KEYS = ""
```

Now, we are ready to compile our new kernel:

```
make -j `getconf _NPROCESSORS_ONLN` deb-pkg
```

After the build is finished check the debian packages:

```
ls ../*deb
```

Then we install all compiled kernel debian packages:

```
sudo dpkg -i ../*.deb
```

### Set user privileges to use real-time scheduling

To be able to schedule threads with user privileges, we will need to change the user’s limits by modifying `/etc/security/limits.conf`. To do so, we create a group named *realtime* and add the user operating the robot to this group:

```
sudo groupadd realtime
sudo usermod -aG realtime $(whoami)
```

Next, make sure `/etc/security/limits.conf` contains the following:

```
@realtime soft rtprio 99
@realtime soft priority 99
@realtime soft memlock 102400
@realtime hard rtprio 99
@realtime hard priority 99
@realtime hard memlock 102400
```

### Set GRUB to boot with real-time kernel

We will use grub-customizer to configure grub. To install for Ubuntu 20.04:

```
sudo apt install grub-customizer -y
```

To install for Ubuntu 18.04:

```
sudo add-apt-repository ppa:danielrichter2007/grub-customizer -y
sudo apt update -y
sudo apt install grub-customizer -y
```

Simply follow the instructions in this [It’s FOSS tutorial](https://itsfoss.com/grub-customizer-ubuntu/) to update your grub settings.

Now reboot the system and select the `PREEMPT_RT` kernel. Once booted, run `uname -a` command in Terminal. If everything is done correctly, the command will return a string with `PREEMPT_RT` keyword.

### Disable CPU speed scaling (optional)

Modern CPUs are able to dynamically scale their frequency depending on operating conditions. In some cases, this can lead to uneven processing speed that in turn interrupts execution. These fluctuations in processing speed can affect the overall performance of the real-time processes.

To disable speed scaling, we will use `cpufrequtils` to disable power saving mode:

```
sudo apt install cpufrequtils
```

Running `cpufreq-info` shows you the available cpufreq governors. The standard setting is `performance, powersave`. We will switch all governers to `performance`:

```
sudo systemctl disable ondemand
sudo systemctl enable cpufrequtils
sudo sh -c 'echo "GOVERNOR=performance" > /etc/default/cpufrequtils'
sudo systemctl daemon-reload && sudo systemctl restart cpufrequtils
```

‍

# Set Up the Robot

## Light it up!

Follow instructions in the provided Quick Start Guide (printed or electronic) to complete hardware setup and boot up the robot.

Caution

Before proceeding, make sure the robot is securely mounted onto a steady base and won’t topple over when moving at a high speed with sudden stops.

## Connect the UI tablet

Follow instructions in the Quick Start Guide to connect the UI tablet (teach pendant) to the robot. Make sure you can use the Flexiv Elements software pre-installed in the UI tablet to enable (servo on) the robot and see the sensor data.

Note

When using RDK, Flexiv Elements is still needed to take care of some auxiliary operations.

Operations that are done in Flexiv Elements when using RDK:

1. Enable/disable Remote mode for RDK.
2. Enable free drive, see [Free Drive](https://www.flexiv.com/software/rdk/manual/free_drive.html).
3. Confirm the switch from Manual to Auto or Auto (Remote) mode, see [Enter Remote mode](https://www.flexiv.com/software/rdk/manual/enter_and_exit_remote_mode.html#enter-remote-mode).

‍

# Activate RDK Server

To control the robot via Flexiv RDK library, the RDK server, managed by the robot’s **Remote mode** module, must be activated first. Follow the instructions below to enable Remote mode for RDK so the RDK server is activated.

## Configure license

A license is required to use Flexiv RDK and can be installed using Flexiv Elements. Please contact your sales representative to purchase and install the license.

There are two types of RDK licenses:

* **Standard** license: provides access to essential and non-real-time functionalities such as reading robot states, sending plan/primitive commands, etc.
* **Professional** license: provides access to everything included with the standard license, plus robot dynamics and real-time functionalities such as joint torque/position streaming, Cartesian motion/force streaming, etc.

## Enable Remote mode for RDK

After RDK license is installed, follow the steps below to enable Remote mode for RDK using Flexiv Elements:

1. Boot up the robot and connect to Flexiv Elements.
2. In Flexiv Elements, navigate to Settings -\> Remote Mode.
   ![_images/enable_rdk_1.jpg](https://www.flexiv.com/software/rdk/manual/_images/enable_rdk_1.jpg)[https://www.flexiv.com/software/rdk/manual/_images/enable_rdk_1.jpg](https://www.flexiv.com/software/rdk/manual/_images/enable_rdk_1.jpg)
3. Toggle on Remote Mode and select “RDK” from the drop-down menu, then save the configuration.
   ![_images/enable_rdk_2.jpg](https://www.flexiv.com/software/rdk/manual/_images/enable_rdk_2.jpg)[https://www.flexiv.com/software/rdk/manual/_images/enable_rdk_2.jpg](https://www.flexiv.com/software/rdk/manual/_images/enable_rdk_2.jpg)
4. Power cycle the robot.

‍

# Enter and Exit Remote Mode

Following [Activate RDK Server](https://www.flexiv.com/software/rdk/manual/activate_rdk_server.html), the Remote mode for RDK should have been enabled by now in robot settings. By design, Flexiv Elements and Flexiv RDK cannot control the robot at the same time. Thus, to facilitate switching control between Elements and RDK, the robot can quickly **enter** and **exit** Remote mode without a power cycle.

## Enter Remote mode

The robot must enter Remote mode before it can be controlled by RDK. There are two ways to do this:

### Boot into Auto mode

1. Enable Remote mode for RDK in settings following [Activate RDK Server](https://www.flexiv.com/software/rdk/manual/activate_rdk_server.html).
2. Power off the robot, do not power on yet.
3. Toggle the *Auto/Manual Slide Switch* on the motion bar to the **upper** position, which corresponds to **Auto** mode.
   ![_images/motion_bar.png](https://www.flexiv.com/software/rdk/manual/_images/motion_bar.png)[https://www.flexiv.com/software/rdk/manual/_images/motion_bar.png](https://www.flexiv.com/software/rdk/manual/_images/motion_bar.png)
4. Power on the robot, which will boot up and automatically enter **Auto (Remote)**  mode. RDK can be used after the robot is fully booted.
   Note

   * All Remote modes have the same safety constraints as the normal Auto mode, thus “Auto (Remote)” is used to denote the Remote mode.
   * The difference between Auto and Manual mode can be found in the robot’s user manual.

### Use Flexiv Elements

With the Remote mode for RDK enabled in settings, if the robot has booted into Manual mode instead of Auto mode, it can still enter Remote mode with the help of Flexiv Elements:

1. Make sure Flexiv Elements is connected to the robot.
2. Toggle the *Auto/Manual Slide Switch* on the motion bar to the **upper** position, a prompt will pop up in Flexiv Elements.

> ![_images/enter_remote_mode.jpg](https://www.flexiv.com/software/rdk/manual/_images/enter_remote_mode.jpg)[https://www.flexiv.com/software/rdk/manual/_images/enter_remote_mode.jpg](https://www.flexiv.com/software/rdk/manual/_images/enter_remote_mode.jpg)

3. Select **AUTO (REMOTE)**  and the robot will enter Remote mode. RDK can now be used.

Important

After the robot has entered Remote mode, Flexiv Elements cannot issue any task commands such as executing a project or invoking free drive, but it can still read data from the robot and display them.

## Exit Remote mode

The robot needs to exit Remote mode before Flexiv Elements can issue commands to it, and it can exit to Manual mode or Auto mode:

### Exit to Manual mode

1. Toggle the *Auto/Manual Slide Switch* on the motion bar to the **lower** position, which corresponds to **Manual** mode. The robot will exit Remote mode and enter Manual mode. Flexiv Elements can now be used to issue commands.

### Exit to Auto mode

1. Toggle the *Auto/Manual Slide Switch* on the motion bar to the **lower** position, which corresponds to **Manual** mode. The robot will exit Remote mode, but has not entered Auto mode yet.
2. Toggle the slide switch back to the **upper** position, a prompt will pop up in Flexiv Elements.

> ![_images/enter_auto_mode.jpg](https://www.flexiv.com/software/rdk/manual/_images/enter_auto_mode.jpg)[https://www.flexiv.com/software/rdk/manual/_images/enter_auto_mode.jpg](https://www.flexiv.com/software/rdk/manual/_images/enter_auto_mode.jpg)

3. Select **AUTO** and the robot will enter Auto mode. Flexiv Elements can now be used to issue commands.

‍

‍

# Establish Connection

After Remote mode for RDK is enabled and entered on the robot, a connection between the user’s workstation PC and the robot can be established following steps below:

1. Use an Ethernet cable to connect the Ethernet port on the workstation PC to any of the LAN ports on the robot’s control box.
   ![_images/control_box_panel.png](https://www.flexiv.com/software/rdk/manual/_images/control_box_panel.png)[https://www.flexiv.com/software/rdk/manual/_images/control_box_panel.png](https://www.flexiv.com/software/rdk/manual/_images/control_box_panel.png)

   Important

   For **real-time** controls of the robot, a direct wired connection between the workstation PC and the robot is required. Going through additional network devices or wireless connection can result in failed timeliness check. However, this restriction does not apply to **non-real-time** controls.
2. Check that *E-Stop* (emergency stop) on the motion bar is pressed **down**.
3. Follow [Enter Remote mode](https://www.flexiv.com/software/rdk/manual/enter_and_exit_remote_mode.html#enter-remote-mode) to boot the robot and enter Remote mode for RDK.
4. Verify the robot is working normally by using Flexiv Elements to enable (servo on) it.
5. Now the connection between the workstation PC and the robot should be established. Check the connection by pinging the robot from the workstation PC:

   ```
   ping <robot_ip>
   ```

   `robot_ip` is `192.168.2.100` by default. The *time* value from the ping command denotes the round trip latency. Make sure this latency complies with the requirement listed in [System Requirements](https://www.flexiv.com/software/rdk/manual/system_requirements.html).
   Note

   The workstation PC and the robot must be under the same subnet to connect. This happens automatically if the two are connected to the same network router that has an active DHCP server.

‍

# Verify with Example Programs

Run some example programs to verify that everything is working.

## Run an example C++ program

1. Compile example C++ programs following [Use the installed library](https://www.flexiv.com/software/rdk/manual/install_for_cpp.html#link-rdk-cpp-lib).
2. Release (pull **up**) E-stop on the motion bar. The robot will have no action because an enabling method must be called to actually enable the robot.
3. Run the most basic example program `basics1_display_robot_states` to check the RDK connection can be established and the robot is normally operational. This example program will first enable the robot, then hold the robot while printing out all received robot states. For Linux and macOS:

   ```
   cd flexiv_rdk/example/build
   ./basics1_display_robot_states [robot_serial_number]
   ```

> Note
>
> * `robot_serial_number` is imprinted near the base of the robot. When providing it to the program, replace space with dash or underscore, for example, Rizon4s-123456.
> * `sudo` is only required if the real-time scheduler API `flexiv::rdk::Scheduler` is used.
>
> For Windows:
>
> ```
> cd flexiv_rdk\example\build\Release
> basics1_display_robot_states.exe [robot_serial_number]
> ```

4. The robot will be enabled and release the joint brakes, which will make some audible crispy sound. After a few seconds, when the enabling process is done and the robot becomes operational, robot states data will be obtained from the server and gets printed in the Terminal. An excerpt of the output is as follows:

   ```
   {
   "q": [0.000, -0.712, -0.000, 1.576, 0.002, 0.696, 0.000],
   "theta": [0.000, -0.710, -0.000, 1.575, 0.001, 0.697, 0.000],
   "dq": [-0.000, -0.000, 0.000, -0.000, -0.000, -0.000, -0.000],
   "dtheta": [0.000, -0.000, -0.000, -0.000, -0.000, -0.000, 0.000],
   "tau": [0.000, 46.733, 1.100, -19.021, -2.010, 2.292, -0.000],
   "tau_des": [-0.000, 0.000, 0.000, -0.000, 0.000, -0.000, -0.000],
   "tau_dot": [0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
   "tau_ext": [0.000, -0.000, 0.000, 0.000, 0.000, -0.000, 0.000],
   "tcp_pose": [0.683, -0.110, 0.275, -0.010, 0.001, 1.000, 0.000],
   "tcp_pose_d": [0.000, 0.000, 0.000, 1.000, 0.000, 0.000, 0.000],
   "tcp_velocity": [0.000, -0.000, 0.000, -0.000, -0.000, 0.000],
   "flange_pose": [0.683, -0.110, 0.275, -0.010, 0.001, 1.000, 0.000],
   "FT_sensor_raw_reading": [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
   "F_ext_tcp_frame": [0.000, 0.000, 0.000, 0.000, -0.000, 0.000],
   "F_ext_world_frame": [-0.000, 0.000, -0.000, -0.000, -0.000, -0.000]
   }
   ```
5. To close the running example program, simply press `Ctrl+C`.

## Run an example Python program

Running en example Python program is similar to running the C++ example program, but without the need for any compilation:

```
cd flexiv_rdk/example_py
python3 basics1_display_robot_states.py [robot_serial_number]
```

Note

Replace `python3` with `python3.x` to explicitly invoke a specific version of Python.

‍

# API Overview

## Available APIs

| API                          | Brief                                                                                                                                                                                                                                    |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `flexiv::rdk::Device`      | Interface with the robot device(s).                                                                                                                                                                                                      |
| `flexiv::rdk::FileIO`      | Interface for file transfer with the robot. The robot must be put into IDLE mode when transferring files.                                                                                                                                |
| `flexiv::rdk::Gripper`     | Interface with the robot gripper.                                                                                                                                                                                                        |
| `flexiv::rdk::Maintenance` | Interface to carry out robot maintenance operations. The robot must be in IDLE mode when triggering any operations.                                                                                                                      |
| `flexiv::rdk::Model`       | Interface to access certain robot kinematics and dynamics data.                                                                                                                                                                          |
| `flexiv::rdk::Robot`       | Main interface with the robot, containing several function categories and background services.                                                                                                                                           |
| `flexiv::rdk::Safety`      | Interface to change robot safety settings. The robot must be in IDLE mode when applying any changes. A password is required to authenticate this interface.                                                                              |
| `flexiv::rdk::Scheduler`   | Real-time scheduler that can simultaneously run multiple periodic tasks. Parameters for each task are configured independently.                                                                                                          |
| `flexiv::rdk::Tool`        | Interface to online update and interact with the robot tools. All changes made to the robot tool system will take effect immediately without needing to reboot. However, the robot must be put into IDLE mode when making these changes. |
| `flexiv::rdk::WorkCoord`   | Interface to online update and interact with the robot’s work coordinates. All updates will take effect immediately without a power cycle. However, the robot must be in IDLE mode when applying changes.                               |

## Access by OS and programming language

The supported OS and programming languages can form various *OS-language* combinations like *Linux-C++* , *Windows-Python*, etc. In RDK, API access varies by such combination: *Linux-C++*  and *macOS-C++*  have full access to all APIs, while the other combinations have partial access as listed below:

| API                          | Unix-C++ | Windows-C++    | Any-Python                                                       |
| ---------------------------- | -------- | -------------- | ---------------------------------------------------------------- |
| `flexiv::rdk::Device`      | Full     | Full           | Full                                                             |
| `flexiv::rdk::FileIO`      | Full     | Full           | Full                                                             |
| `flexiv::rdk::Gripper`     | Full     | Full           | Full                                                             |
| `flexiv::rdk::Maintenance` | Full     | Full           | Full                                                             |
| `flexiv::rdk::Model`       | Full     | Full           | Full                                                             |
| `flexiv::rdk::Robot`       | Full     | Full           | **Partial** (exclusion: functions marked as “Real-time”) |
| `flexiv::rdk::Safety`      | Full     | Full           | Full                                                             |
| `flexiv::rdk::Scheduler`   | Full     | **None** | **None**                                                   |
| `flexiv::rdk::Tool`        | Full     | Full           | Full                                                             |
| `flexiv::rdk::WorkCoord`   | Full     | Full           | Full                                                             |

Besides APIs, access to data structures and enums also varies by the *OS-language* combination:

| Data Structures / Enums            | Unix-C++ | Windows-C++ | Any-Python                                     |
| ---------------------------------- | -------- | ----------- | ---------------------------------------------- |
| `flexiv::rdk::RobotInfo`         | Full     | Full        | Full                                           |
| `flexiv::rdk::RobotStates`       | Full     | Full        | Full                                           |
| `flexiv::rdk::PlanInfo`          | Full     | Full        | Full                                           |
| `flexiv::rdk::JPos`              | Full     | Full        | Full                                           |
| `flexiv::rdk::Coord`             | Full     | Full        | Full                                           |
| `flexiv::rdk::GripperParams`     | Full     | Full        | Full                                           |
| `flexiv::rdk::GripperStates`     | Full     | Full        | Full                                           |
| `flexiv::rdk::SafetyLimits`      | Full     | Full        | Full                                           |
| `flexiv::rdk::ToolParams`        | Full     | Full        | Full                                           |
| `flexiv::rdk::CoordType`         | Full     | Full        | Full                                           |
| `flexiv::rdk::OperationalStatus` | Full     | Full        | Full                                           |
| `flexiv::rdk::Mode`              | Full     | Full        | **Partial** (exclusion: real-time modes) |

Note

*Unix* means Linux and macOS.

## API documentation

The complete and detailed API documentation of the **latest release** can be found at [https://www.flexiv.com/software/rdk/api](https://www.flexiv.com/software/rdk/api). The API documentation of a previous release can be generated manually using Doxygen. For example, on Linux:

```
sudo apt install doxygen-latex graphviz
cd flexiv_rdk
git checkout <previous_release_tag>
doxygen doc/Doxyfile.in
```

The generated API documentation is under `flexiv_rdk/doc/html/` directory. Open any html file with your browser to view it.

‍

# Control Modes

The robot can be put into different control modes to execute various types of commands. Depending on network conditions and programming language used, Flexiv RDK provides users the flexibility to choose between real-time (**RT**) control modes and non-real-time (**NRT**) control modes. The enumeration of all control modes is defined by `flexiv::rdk::Mode` in header file `flexiv/rdk/mode.hpp`.

Important

Most command-transmission functions require the robot to be switched into the corresponding control mode before the commands can be transmitted.

## Real-time (RT) modes

Under RT control modes, user commands and robot states are exchanged between the workstation PC and the robot at 1kHz with less than 1ms latency, enabling the users to gain low-level controls of the robot. The available real-time controls are:

* Joint-space motion and torque controls
* Cartesian-space motion and force controls

Note

All controls above include compensation for nonlinear dynamics, including gravitational, frictional, centrifugal, and Coriolis force or torque.

Detailed description of each RT control mode is listed below.

### RT joint torque control mode (`Mode::RT_JOINT_TORQUE`)

The robot receives **joint torque** commands streamed at 1kHz, and execute them immediately using a built-in joint torque controller. Gravity, friction, and other nonlinear dynamics are compensated. The command-transmission function of this mode is `Robot::StreamJointTorque()`.

### RT joint impedance control mode (`Mode::RT_JOINT_IMPEDANCE`)

The robot receives **joint position** commands streamed at 1kHz, and execute them immediately using a built-in joint impedance controller. Gravity, friction, and other nonlinear dynamics are compensated. The command-transmission function of this mode is `Robot::StreamJointPosition()`.

### RT joint position control mode (`Mode::RT_JOINT_POSITION`)

Same as RT joint impedance control mode, except that the commands are executed using a joint position controller instead, which is much less compliant. The command-transmission function of this mode is also `Robot::StreamJointPosition()`.

### RT Cartesian motion-force control mode (`Mode::RT_CARTESIAN_MOTION_FORCE`)

The robot receives **Cartesian motion and/or force** commands streamed at 1kHz, and execute them immediately using a built-in unified motion-force controller. Gravity, friction, and other nonlinear dynamics are compensated. The command-transmission function of this mode is `Robot::StreamCartesianMotionForce()`.

## Non-real-time (NRT) modes

Under NRT control modes, users can send high-level operation instructions like plans and primitives pool, or discrete motion commands that are automatically interpolated and smoothened by the robot’s internal motion generator. In such case, all real-time computations are done by the robot, thus the requirements on network latency and the workstation PC’s performance can be relaxed. The available non-real-time controls are:

* Discrete joint-space motion controls
* Discrete Cartesian-space motion and force controls
* Plan execution
* Primitive execution

Note

The above joint and Cartesian controls include internal motion generation plus compensation for nonlinear dynamics.

Detailed description of each NRT control mode is listed below.

### NRT joint impedance control mode (`Mode::NRT_JOINT_IMPEDANCE`)

The robot receives **joint position** commands in a one-shot or slow-periodic manner. A built-in motion generator will produce smooth joint-space trajectories based on the discrete commands, then the trajectories are executed using a built-in joint impedance controller. Gravity, friction, and other nonlinear dynamics are compensated. The command-transmission function of this mode is `Robot::SendJointPosition()`.

### NRT joint position control mode (`Mode::NRT_JOINT_POSITION`)

Same as NRT joint impedance control mode, except that the commands are executed using a joint position controller instead, which is much less compliant. The command-transmission function of this mode is also `Robot::SendJointPosition()`.

### NRT Cartesian motion-force control mode (`Mode::NRT_CARTESIAN_MOTION_FORCE`)

The robot receives **Cartesian motion and/or force** commands in a one-shot or slow-periodic manner. A built-in motion generator will produce smooth Cartesian-space trajectories based on the discrete commands, then the trajectories are executed using a built-in Cartesian unified motion-force controller. Gravity, friction, and other nonlinear dynamics are compensated. The command-transmission function of this mode is `Robot::SendCartesianMotionForce()`.

### Primitive execution mode (`Mode::NRT_PRIMITIVE_EXECUTION`)

The robot receives and executes primitives specified by the user. The command-transmission function of this mode is `Robot::ExecutePrimitive()`. Current states of the running primitive can be obtained via `Robot::primitive_states()`.

Note

Primitives are unit skills and actions that the robot already knows. They can be used collectively to form complex operations. The full documentation for all available primitives can be found in [Flexiv Primitives Manual](https://www.flexiv.com/primitives/).

### Plan execution mode (`Mode::NRT_PLAN_EXECUTION`)

The robot receives and executes plans specified by the user. A list of all available plans can be obtained via `Robot::plan_list()`. The command-transmission function of this mode is `Robot::ExecutePlan()`.

## Idle mode (`Mode::IDLE`)

Idle is when the robot is not in any of the control modes listed above. It will hold its current position and wait for new user commands. The robot will transit to idle mode when `Robot::Stop()` is called.

## Switch control modes

To switch to a certain control mode, simply call `Robot::SwitchMode()`. If the robot is still moving when this function is called, it will automatically decelerate to a complete stop first, then make the mode transition.

‍

# Robot States

Robot states refer to the measured or estimated information about the robot at a snapshot in time. The data structure containing all robot states is defined by `flexiv::rdk::RobotStates` in header file `flexiv/rdk/data.hpp`.

Note

Despite the control mode the robot is currently in, robot states are always updated and published to the user in real time at 1kHz. However, the user can control how frequently they access the data by simply controlling the rate at which `Robot::states()` function is called.

Robot states include:

* Measured joint-space states: joint positions, velocities, torques, etc.
* Computed Cartesian-space states: Cartesian pose, velocity, etc.
* Estimated states: external joint torques, external TCP wrench (force and moment), etc.

Please refer to `flexiv::rdk::RobotStates` for detailed documentation on each state.

‍

# Robot Description (URDF)

The URDF files of all Flexiv Rizon models can be found under `flexiv_rdk/resources` directory. The visual and collision mesh files are also available under this directory.

Warning

The URDF files contain accurate kinematics parameters but **blurred** dynamics parameters. Accurate dynamics data can be obtained via the `flexiv::rdk::Model` API.

‍

# Digital I/O Control

Flexiv RDK can also control the general-purpose digital I/O ports located on the robot’s control box. A total of 16 digital outputs and 16 digital inputs are available. The digital inputs can be read via `Robot::ReadDigitalInput()`, and the digital outputs can be written via `flexiv::Robot::WriteDigitalOutput()`.

![_images/digital_io_ports.jpg](https://www.flexiv.com/software/rdk/manual/_images/digital_io_ports.jpg "5 - General-purpose digital I/O, 6 - Safety I/O")

Note

Make sure to use the I/O ports marked in the red rectangle. Safety I/O is only accessible by the safety system, not by the robot software.

‍

# Loss of Connection

A few things happen when the connection between the RDK client and the robot is lost, which can be caused by terminating a running RDK program or network interruption like unplugging the Ethernet cable.

## Automatic stop

Upon loss of connection, the robot will automatically transit to [Idle mode (Mode::IDLE)](https://www.flexiv.com/software/rdk/manual/control_modes.html#idle-mode), which means the ongoing task will be stopped and the robot will decelerate to a complete stop then hold its position.

## Hot reconnection

After the connection is lost, the robot can be reconnected on-the-fly, thus you can restart the RDK program or re-plug the Ethernet cable to get reconnected without doing anything to the robot.

Note

Because the robot has automatically transited to idle mode, `Robot::SwitchMode()` needs to be called again to switch control mode before new commands can be sent.

‍

# Free Drive

## Invoke directly from RDK

1. Switch the robot into [Primitive execution mode (Mode::NRT_PRIMITIVE_EXECUTION)](https://www.flexiv.com/software/rdk/manual/control_modes.html#primitive-mode).
2. Call `Robot::ExecutePrimitive()` to execute `FloatingCartesian` primitive for free drive in Cartesian space, or `FloatingJoint` for free drive in joint space. For example:
   解释

   ```
   # Python
   ...

   robot.ExecutePrimitive("FloatingCartesian()")
   while robot.busy():
       time.sleep(1)

   ...
   ```

Caution

Free drive will be activated immediately regardless of whether the enabling button on the motion bar is pressed down or not. You can implement your own code to only activate free drive while enabling button is pressed down with the help of a condition check on `Robot::enabling_button_pressed()`.

Note

Both `FloatingCartesian` and `FloatingJoint` primitives require a license.

## Invoke from Flexiv Elements

With the teach pendant connected, free drive can be invoked under either Manual or Auto mode.

### Free drive under Manual mode

The robot’s movement speed is restricted under Manual mode, thus free drive feels **heavy**. To invoke:

1. Toggle the *Auto/Manual Slide Switch* on the motion bar to the **lower** position to exit Auto (Remote) mode and enter Manual mode.
2. Click the *Freedrive On &amp; Off* button on the motion bar. LED on the motion bar will turn deep blue, and a window for controlling free drive will pop up in Flexiv Elements.
3. Follow instructions in Flexiv Elements to unlock Cartesian or joint axes to free drive.
4. Press and hold *Enabling Button* on the motion bar to activate free drive.

### Free drive under Auto mode

The robot’s movement speed is not restricted under Auto mode, thus free drive feels **light**. To invoke:

1. Same as step 1 above to put the robot into Manual mode first.
2. Push the *Auto/Manual Slide Switch* back to **upper** position, a window will pop-up asking you to choose which type of Auto mode to enter, choose **AUTO**.
3. Same as steps 2 to 4 as above.

‍

# Frequently Asked Questions

## Where can I download Flexiv RDK?

See [Download Flexiv RDK](https://www.flexiv.com/software/rdk/manual/download_rdk.html).

## What OS and programming languages does RDK support?

See [Environment Compatibility](https://www.flexiv.com/software/rdk/manual/environment_compatibility.html).

## Where can I see which version of robot software is compatible with a given RDK version?

See [Robot Software Compatibility](https://www.flexiv.com/software/rdk/manual/robot_software_compatibility.html).

## What features are available in the current version of RDK?

See [Key Features](https://www.flexiv.com/software/rdk/manual/key_features.html).

## It seems something was wrong and the robot is not doing what I commanded, how can I check what happened?

Flexiv RDK will throw exceptions and provide error messages for faults occurred on the connected robot or Flexiv RDK itself. You can read through the error messages and try to solve the problem, then clear the robot fault if any (see question below).

## Can I clear robot faults via RDK?

Yes, you can use `Robot::ClearFault()` to try to clear minor or critical fault of the robot without a power cycle. See [Critical fault](https://www.flexiv.com/software/rdk/manual/error_handling.html#critical-fault) for more details.

## How can I access the external force and moment applied to the end-effector?

Call `Robot::states()` to obtain the latest `RobotStates` data structure, whose member variables `ext_wrench_in_tcp` and `ext_wrench_in_world` are what you are looking for.

## How can I free drive the robot when using RDK?

See [Free Drive](https://www.flexiv.com/software/rdk/manual/free_drive.html).

## I toggled the Auto/Manual slide switch on the motion bar, and now RDK is not working, how to solve this?

See [Enter Remote mode](https://www.flexiv.com/software/rdk/manual/enter_and_exit_remote_mode.html#enter-remote-mode).

## Where can I find the robot kinematics?

See [Robot Description (URDF)](https://www.flexiv.com/software/rdk/manual/robot_description.html).

‍

# Error Handling

## Robot fault and error messages

It is recommended to always check if the robot is in fault state using `Robot::fault()` before enabling the robot. During runtime, if a fault occurred on the robot, `Robot::fault()` will return true and the error message from the robot will be printed by RDK. Important log messages from the robot will be cached by RDK and can be accessed via `Robot::mu_log()`, which includes the aforementioned error message as well as other important info and warning messages.

## Robot operational

After releasing E-Stop and sending enabling command to the robot, it will take several seconds to release the brakes and become operational. Use `Robot::operational()` to check if the robot is ready before sending any user commands.

## Critical fault

After the robot is enabled, its certified safety system will constantly monitor the robot to make sure it always operates under the predefined safety limits such as joint torque/position/velocity limit, TCP force/position/velocity limit, robot power and momentum limit, etc. Any violation to the safety limits will trigger a critical fault, also known as the *Category 0 Stop*, or *CAT0 Stop*. If triggered, the robot’s main drive power will be cutoff instantly and all joint brakes will engage. In order to re-run the robot, you need to try to clear the critical fault first without a power cycle using `Robot::ClearFault()`, which can hot reset the safety system and takes about 30 seconds. However, for older models that do not support hot reset, a power cycle is mandatory. In addition, based on the type of critical fault occurred, a recovery operation may be needed. See [Recover from joint position limit violation](https://www.flexiv.com/software/rdk/manual/error_handling.html#recovery-operation) for more details.

## Minor fault

Besides critical faults triggered by the safety system, there are also minor faults that are triggered from the robot software. They are often related to unreasonable user commands or invalid program workflow. Such minor faults will not lead to a power cut nor system lock-down, and can be quickly cleared via `Robot::ClearFault()`, which takes less than 3 seconds.

## Recover from joint position limit violation

The *Critical fault* section above mentioned that violating any of the safety system limits will lead to a critical fault that requires a hot reset or power cycle, which should clear the fault in most cases. However, there’s one special case: the violation of the joint position limit. When this happens, resetting the system won’t change the fact that one or more of the joints is at a position outside the allowed safe region. Therefore, after resetting, the safety system will enter **recovery state**, in which it requires the user to figure out a way to move the violating joint(s) back into the allowed safe region. This can be easily done with the help of Flexiv RDK’s automatic recovery function:

1. Keep the mode selection switch on the motion bar at the upper position (i.e. Auto mode).
2. Hot reset or power cycle the system.
3. Release E-stop as usual.
4. Run the example program `basics7_auto_recovery`, C++ or Python.
5. Wait for all violating joints to move back to safe region.
6. Press down E-stop, then do another hot reset or power cycle, after which the robot can be normally operated.


# ROS 2 Bridge

For ROS 2 users to easily work with RDK, the APIs of RDK are wrapped into ROS packages in the [[flexiv_ros2]](https://github.com/flexivrobotics/flexiv_ros2) repository. Key functionalities like joint torque and position control are supported, and the integration with [ros2_control](https://control.ros.org/master/index.html) framework and [MoveIt! 2](https://moveit.picknik.ai/humble/index.html) is also implemented.

## Compatibility

| Supported OS | Supported ROS 2 distribution                               |
| ------------ | ---------------------------------------------------------- |
| Ubuntu 20.04 | [Foxy Fitzroy](https://docs.ros.org/en/foxy/index.html)       |
| Ubuntu 22.04 | [Humble Hawksbill](https://docs.ros.org/en/humble/index.html) |

## Overview

`flexiv_ros2` contains the following packages:

| Package                  | Description                                                             |
| ------------------------ | ----------------------------------------------------------------------- |
| `flexiv_bringup`       | Launch and run-time configurations for controllers and demos.           |
| `flexiv_controllers`   | Implementation of custom controllers.                                   |
| `flexiv_description`   | Robot URDF and mesh files.                                              |
| `flexiv_gripper`       | Implementation of the action server for Flexiv gripper control.         |
| `flexiv_hardware`      | Hardware interface between Flexiv robots and*ros2_control* framework. |
| `flexiv_moveit_config` | MoveIt configuration for Flexiv robots.                                 |
| `flexiv_msgs`          | Definition of messages used in RDK.                                     |
| `flexiv_test_nodes`    | Demo nodes and examples.                                                |

More details can be found in section [Packages](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html#packages).

## Environment setup

Note

The following instructions are for ROS 2 Humble. For ROS 2 Foxy, please replace `foxy` with `humble` in the commands, and clone the `foxy` branch of [[flexiv_ros2]](https://github.com/flexivrobotics/flexiv_ros2).

1. Install [ROS 2 Humble via Debian Packages](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html) (ros-humble-desktop)
2. Install additional packages:

   ```
   sudo apt install -y \
   python3-colcon-common-extensions \
   python3-rosdep2 \
   libeigen3-dev \
   ros-humble-xacro \
   ros-humble-tinyxml2-vendor \
   ros-humble-ros2-control \
   ros-humble-realtime-tools \
   ros-humble-control-toolbox \
   ros-humble-moveit \
   ros-humble-ros2-controllers \
   ros-humble-test-msgs \
   ros-humble-joint-state-publisher \
   ros-humble-joint-state-publisher-gui \
   ros-humble-robot-state-publisher \
   ros-humble-rviz2
   ```
3. Create a ROS 2 workspace and clone `flexiv_ros2`:

   ```
   mkdir -p ~/flexiv_ros2_ws/src
   cd ~/flexiv_ros2_ws/src
   git clone https://github.com/flexivrobotics/flexiv_ros2.git
   cd flexiv_ros2/
   git submodule update --init --recursive
   ```
4. Install dependencies:

   ```
   cd ~/flexiv_ros2_ws
   rosdep update
   rosdep install --from-paths src --ignore-src --rosdistro humble -r -y
   ```
5. Compile `flexiv_rdk` library and install to the `~/rdk_install` directory:

   ```
   cd ~/flexiv_ros2_ws/src/flexiv_ros2/flexiv_hardware/rdk/thirdparty
   bash build_and_install_dependencies.sh ~/rdk_install
   cd ~/flexiv_ros2_ws/src/flexiv_ros2/flexiv_hardware/rdk
   mkdir build && cd build
   cmake .. -DCMAKE_INSTALL_PREFIX=~/rdk_install
   cmake --build . --target install --config Release
   ```
6. Build and source the workspace:

   ```
   cd ~/flexiv_ros2_ws
   source /opt/ros/humble/setup.bash
   colcon build --symlink-install --cmake-args -DCMAKE_PREFIX_PATH=~/rdk_install
   source install/setup.bash
   ```

Important

Whenever a new Terminal is opened, the ROS 2 Humble environment and `flexiv_ros2` workspace must be sourced before running any ROS 2 commands:

```
source /opt/ros/humble/setup.bash
source ~/flexiv_ros2_ws/install/setup.bash
```

## Packages

Below are detailed descriptions of all available packages, whose structure is based on that of [ros2_control_demos](https://github.com/ros-controls/ros2_control_demos).

### flexiv\_bringup

This package contains launch files: the main driver launcher, the MoveIt launch file and demo examples. To run the main launcher:

```
ros2 launch flexiv_bringup rizon.launch.py robot_sn:=[robot_sn]
```

Note

The required arguments for the launch file is:* `robot_sn`: the serial number of the robot. Remove any space, for example: Rizon4s-123456

To show all available arguments, run `ros2 launch flexiv_bringup rizon.launch.py --show-args`.

It will establish connection with the robot server, load the default *rizon_arm_controller*, and visualize the robot in RViZ. This controller uses `position_command_interface`, and will put the robot into joint position mode.

If you don’t have an real robot connected, you can test with the simulated hardware:

```
ros2 launch flexiv_bringup rizon.launch.py robot_sn:=dont-care use_fake_hardware:=true
```

which will use the `mock_components` simulated hardware interface instead of `flexiv_hardware` for real robot.

### flexiv\_controllers

This package contains custom `ros2_control` controllers and broadcasters. For example, the `joint_impedance_controller` converts joint motion inputs to torque outputs.

### flexiv\_description

This package contains xacro files to generate URDF with accurate kinematics but approximated dynamics parameters, as well as mesh files for visualization. In addition, it contains a launch file that visualizes the robot without accessing a real robot:

```
ros2 launch flexiv_description view_rizon.launch.py gui:=true
```

### flexiv\_gripper

This package contains the gripper action server to interface with the gripper that is connected to the robot.

Start the `flexiv_gripper_node` with the following launch file:

```
ros2 launch flexiv_gripper flexiv_gripper.launch.py robot_sn:=[robot_sn]
```

Or, start the gripper control with the robot driver if the gripper is Flexiv Grav:

```
ros2 launch flexiv_bringup rizon.launch.py robot_sn:=[robot_sn] load_gripper:=true
```

In a new terminal, send the gripper action `move` goal to open or close the gripper:

```
# Closing the gripper
ros2 action send_goal /flexiv_gripper_node/move flexiv_msgs/action/Move "{width: 0.01, velocity: 0.1, max_force: 20}"
# Opening the gripper
ros2 action send_goal /flexiv_gripper_node/move flexiv_msgs/action/Move "{width: 0.09, velocity: 0.1, max_force: 20}"
```

The `grasp` action enables the gripper to grasp with direct force control, but it requires the mounted gripper to support direct force control. Send a `grasp` command to the gripper:

```
ros2 action send_goal /flexiv_gripper_node/grasp flexiv_msgs/action/Grasp "{force: 0}"
```

To stop the gripper, send a `stop` service call:

```
ros2 service call /flexiv_gripper_node/stop std_srvs/srv/Trigger {}
```

### flexiv\_hardware

This package contains the `flexiv_hardware` plugin needed by *ros2_control*. The plugin is passed to the controller manager via the `robot_description` topic, and provides for each joint:

* position state interface: measured joint position.
* velocity state interface: measured joint velocity.
* effort state interface: measured joint torque.
* position command interface: desired joint position.
* velocity command interface: desired joint velocity.
* effort command interface: desired joint torque.

### flexiv\_moveit\_config

This package contains the configuration for [MoveIt 2](https://moveit.picknik.ai/humble/index.html). The planning group of the manipulator is called `rizon_arm`. The joint values for the **Home** pose configuration is [0, -40, 0, 90, 0, 40, 0] (deg).

The planning group of the gripper is called `grav_gripper`. The joint values for the **Open** pose configuration is [0.1] (m), and for the **Close** pose configuration is [0.0] (m).

### flexiv\_msgs

This package contains messages for the measured or estimated information of the robot.

### flexiv\_test\_nodes

This package contains the demo nodes for the examples in [Demos](https://www.flexiv.com/software/rdk/manual/ros2_bridge.html#ros2-demo). This package is adapted from [ros2_control_test_nodes](https://github.com/ros-controls/ros2_control_demos/tree/master/ros2_control_test_nodes).

## MoveIt

To run the MoveIt example with the real robot:

```
ros2 launch flexiv_bringup rizon_moveit.launch.py robot_sn:=[robot_sn]
```

You should be able to use the MotionPlanning plugin in RViZ to plan and execute motions with the robot.

To run MoveIt with the simulated hardware:

```
ros2 launch flexiv_bringup rizon_moveit.launch.py robot_ip:=dont-care use_fake_hardware:=true
```

## Demos

This section provides examples with the executable nodes in the `flexiv_test_nodes` package.

### Mode switching demo

First start the robot with the default *rizon_arm_controller*:

```
ros2 launch flexiv_bringup rizon.launch.py robot_sn:=[robot_sn]
```

Then load *joint_impedance_controller* and switch to it:

```
ros2 control load_controller joint_impedance_controller --set-state configured
ros2 control switch_controllers --deactivate rizon_arm_controller --activate joint_impedance_controller
```

The robot will stop joint position control and start joint torque control.

To start *joint_impedance_controller* directly, run the `rizon.launch.py` launch file with an additional argument `robot_controller:=joint_impedance_controller`.

Note

1. To list all available and claimed hardware interfaces, use command: `ros2 control list_hardware_interfaces`.
2. To list all loaded controllers, use command: `ros2 control list_controllers`.

### Joint position control

First start the robot with *rizon_arm_controller*:

```
ros2 launch flexiv_bringup rizon.launch.py robot_sn:=[robot_sn] robot_controller:=rizon_arm_controller
```

Then in a new terminal run the test program to send joint position commands to the controller:

```
ros2 launch flexiv_bringup test_joint_trajectory_controller.launch.py
```

After a few seconds, the robot joints will move to the position goals defined in `flexiv_bringup/config/joint_trajectory_position_publisher.yaml`

### Joint impedance control

First start the robot with *joint_impedance_controller*:

```
ros2 launch flexiv_bringup rizon.launch.py robot_sn:=[robot_sn] robot_controller:=joint_impedance_controller
```

Important

The command starts the robot in the joint torque mode. In this mode, gravity and friction are compensated **only** for the robot **without** any attached objects (e.g. the gripper, camera).

Then in a new terminal run the test program to send joint torque commands to the controller:

```
ros2 launch flexiv_bringup sine_sweep_impedance.launch.py
```

The robot will run a sine-sweep motion from the current joint positions using impedance control.

Caution

The gains used in *joint_impedance_controller* are only for demo purpose, and can be changed in `flexiv_bringup/config/rizon_controllers.yaml`.

‍

# ROS 1 Bridge

Please refer to [[flexiv_ros]](https://github.com/flexivrobotics/flexiv_ros) on GitHub.

‍

Rizon 10

| Frame i | α ( i - 1 ) [rad] | a ( i - 1 ) [m] | d (i) [m] | θ (i) [rad] |
| ------- | ------------------ | --------------- | --------- | ------------ |
| 1       | 0                  | 0               | 0.450     | 0            |
| 2       | π/2               | 0               | 0.130     | 0            |
| 3       | -π/2              | 0               | 0.450     | 0            |
| 4       | -π/2              | 0               | 0.120     | 0            |
| 5       | π/2               | 0               | 0.395     | 0            |
| 6       | π/2               | 0               | 0.103     | 0            |
| 7       | π/2               | 0.113           | 0         | 0            |
| Flange  | 0                  | 0               | 0.096     | π           |

每个关节的坐标

{ 0 }( reference )
{ 1 }( 0, 0, 0.450 )
{ 2 }( 0, -0.130, 0.450 )
{ 3 }( 0, -0.130, 0.900 )
{ 4 }( 0, -0.100, 0.900 )
{ 5 }( 0, -0.100, 1.295 )
{ 6 }( 0, -0.113, 1.295 )
{ 7 }( 0.110, -0.113, 1.295)
{ flange }( 0.110, -0.113, 1.199 )
