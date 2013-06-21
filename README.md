Super ANT Builder for SublimeText 2+
====================================

This plugin adds the ability to choose a target from an ANT build file in the root of your working folder in Sublime Text 2.


About
------------
This build system is based on the idea that you have a project with a single top level folder or multiple folders. At least the first folder should house your project files along with a build.xml and other build files, in the root.

Latest Update
------------
- Sublime Text 3 Support
- Project Support (SublimeText 3+)
-- Project Folder Searching for buildfile 
-- Project Custom buildfile (buildfile property at root of project)

Features 
------------
- Added the ability to specify the ant build file. This can be accessed through the preferences menu within Sublime Text or the Command Palette under "Preferences > Package Settings > Super Ant". The settings file will also automatically be opened in the case that SuperAnt cannot file a build file in your project.

- It is possible to launch a build.xml file from another folder than the main/first one in your sublime project by selecting the according build.xml and run the build command 

- ANT Import Traversal for nestest targets. (default: true)
- Target Hiding
-- Without a description. (default: true)
-- Targets with names that begin with "_". (default: true)
-- Targets in a project without a project name. (default: true)


Prerequisites
------------
ANT - http://ant.apache.org/


How to Use
------------

1. Install the plugin
2. Create a single folder project
3. Add Build.xml to the project
4. Select SuperAnt from your Tools -> BuildSystem
5. Select Tools -> Build
6. You will be presented with a list of all your ANT targets
7. Select the ANT target you wish to run
8. Enjoy!