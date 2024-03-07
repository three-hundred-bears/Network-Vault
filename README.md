# Network Saver

This project is meant to provide an easy, artist-friendly interface that allows 
users to save and distribute Houdini networks without the need to compile or 
parameterize them as an HDA. 

## Overview

Oftentimes one or more shot, asset, or sequence setups need to be shared across a 
department. This application takes care of storing and managing any number of 
Houdini networks across any number of users, and provides a UI allowing artists to 
easily interface with it. This allows users to quickly store and distribute a 
setup to any who might need it. 
Networks are saved with a name and description, additionally saving the 
version of Houdini and network category they were saved from in an effort to 
avoid any potential backward compatibility issues.

## Installation

This application assumes that both the HFS and HHP environment variables are 
set to their relevant directories. 
network_saver/python must be prepended to PYTHONPATH, and network_saver/toolbar 
must be prepended to HOUDINI_TOOLBAR_PATH.
