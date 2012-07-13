import sublime, sublime_plugin, sys,os
from xml.dom.minidom import parseString

DEFAULT_BUILD_CMD = "exec"
DEFAULT_BUILD_TASK = "build"


class SuperAntExecCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):

        package_dir = os.path.join(sublime.packages_path(), "SuperAnt");
        self.build = os.path.join(package_dir, 'build.xml')
        self.build_properties = os.path.join(package_dir, 'build.properties')

        path = None;
        if len(self.window.folders()) > 0:
            for folder in self.window.folders():
                if os.path.exists(folder + os.sep + "build.xml"):
                    self.build = folder + os.sep + "build.xml";

                if os.path.exists(folder + os.sep + "build.properties"):
                    self.build_properties = folder + os.sep + "build.properties";

        try:
            f = open(self.build);
        except Exception as ex:
            print ex;
            return 'The file could not be opened'
    
        data = f.read();
        dom = parseString(data);
        targets = dom.getElementsByTagName('target');

        self.targetsList = [];
        for target in targets:
            self.targetsList.append(target.getAttributeNode("name").nodeValue)

        self.targetsList = sorted(self.targetsList);

        self.window.show_quick_panel(self.targetsList, self._quick_panel_callback);

    def _quick_panel_callback(self, index):
        if (index > -1):
            targetName = self.targetsList[index];
            print targetName;
            
            ant = "ant";
            # Check for Windows Overrides and Merge
            if sys.platform.startswith('win32'):
                    ant = "ant.bat";

            path = None;
            if len(self.window.folders()) > 0:
                path = self.window.folders()[0];

            if path != None:
                cmd = {
                    'cmd': [ant, "-f", self.build,"-propertyfile ", self.build_properties, targetName],
                    'working_dir': path
                }

                print cmd;
                # run build
                self.window.run_command("exec", cmd);
