# MsgGeneration
A python script to generate UROSBridge compatible message and service files from ROS-like templates.

## Introduction
You are tired of having to write every single message or service file for UROSBridge yourself? You want to stop having to bang your head against the wall in frustration at the thought of **even more** copypasta?

If you answered yes (or YEAH!!!) to any of those, today is your lucky day. I wrote several scripts which will allow you to easily generate all messages and services in a ROS package with a simple command.

**Warning: Anything containing enums, empty files and services with one empty part (request or response) are currently not supported.**

## Usage
Begin by cloning this repository to your local machine. You will also need to install Python 3 as well as [numpy](http://www.numpy.org/) and [tkinter](https://wiki.python.org/moin/TkInter). 

Call the desired generator script (they're all located in the bin folder) from the commandline and specify a path to a ROS package. The -p option allows you to write a path directly. If you use -g a filedialog will open which allows you to pick a folder. If you want to run the script on multiple ROS packages you can do so by adding the -multi option and then picking a parent folder containing multiple ROS packages (non-recursive, currently only works in GenerateAll and GenerateAllBson).

The directory you choose should be a ROS-Package containing a msg and/or srv folder which holds your msg or srv files. (This is the same directory tree you will find in any normal ROS-Package). After running, the generated C++ files will be placed in the main folder of the package.

Calling the Bson versions of the generators will give you Json functionality as well, calling the non-bson versions will give you _only_ Json functionality.

## Formatting
For formatting rules for the contents of the .txt file refer to [this](http://wiki.ros.org/msg).

The namespace of your message or service will be the packages name. (e.g. if you have a file in 'geometry_msgs' it's namespace will be 'geometry_msgs'.)

The name of the message will be the name of your file with a .h at the end.
