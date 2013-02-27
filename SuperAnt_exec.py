import sublime, sublime_plugin, sys,os
from xml.dom.minidom import parseString

DEFAULT_BUILD_CMD = "exec"
DEFAULT_BUILD_TASK = "build"


class SuperAntExecCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        package_dir = os.path.join(sublime.packages_path(), "Super Ant");
        
        self.working_dir = kwargs['working_dir'];
        self.build = None;

        s = sublime.load_settings("SuperAnt.sublime-settings");
        build_file = s.get("build_file", "build.xml");

        # buildfile by selection: search build file in project folder that file from active view is in  
        try:
            active_file = self.window.active_view().file_name();
            active_folder = os.path.dirname(active_file);
            if os.path.exists(active_folder + os.sep + build_file):
                self.build = active_folder + os.sep + build_file;
                self.working_dir = active_folder
            else:
                raise Exception('not a build file');
        except Exception as ex:
            print 'No build file in base folder of currently viewed file';

        # buildfile by default: build.xml found in first project folder
        if self.build == None and os.path.exists(self.working_dir + os.sep + build_file):
            self.build = self.working_dir + os.sep + build_file;

        try:
            f = open(self.build);
        except Exception as ex:
            print ex;
            self.window.open_file(os.path.join(package_dir, 'SuperAnt.sublime-settings'));
            return 'The file could not be opened';
    
        self.working_dir = os.path.dirname(self.build);

        data = f.read();
        dom = parseString(data);
        self.targets = dom.getElementsByTagName('target');

        # get project name for target prefixing in quick panel
        project_name = None;
        try:
            project_name = dom.firstChild.getAttributeNode('name').nodeValue;
        except Exception, e:
            # default to folder name if name attribute is not given in project tag
            project_name = os.path.basename(self.working_dir);
        print project_name;

        self.targetsList = [];
        for target in self.targets:
            targetName = target.getAttributeNode("name").nodeValue;
            if targetName[0] != "_":
                self.targetsList.append(project_name + ': ' + target.getAttributeNode("name").nodeValue);

        self.targetsList = sorted(self.targetsList);

        self.window.show_quick_panel(self.targetsList, self._quick_panel_callback);

    def _quick_panel_callback(self, index):

        if (index > -1):
            targetName = self.targets[index].getAttributeNode("name").nodeValue;
            print targetName;
            
            ant = "ant";
            # Check for Windows Overrides and Merge
            if sys.platform.startswith('win32'):
                ant = "ant.bat";

            cmd = {
                'cmd': [ant, "-f", self.build, targetName],
                'working_dir': self.working_dir
            }

            print cmd;
            # run build
            self.window.run_command("exec", cmd);
