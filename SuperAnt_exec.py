import sublime, sublime_plugin, sys,os
from xml.dom.minidom import parseString

DEFAULT_BUILD_CMD = "exec"
DEFAULT_BUILD_TASK = "build"


class SuperAntExecCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        self.package_dir = os.path.join(sublime.packages_path(), "Super Ant");
        self.mainProject = None;
        
        self.working_dir = kwargs['working_dir'];
        self.build = None;
        self.separator = ".";

        s = sublime.load_settings("SuperAnt.sublime-settings");
        build_file = s.get("build_file", "build.xml");
        use_sorting = s.get("use_sorting", "true") == "true";
        follow_imports = s.get("follow_imports", "true") == "true";
        seach_project_folders = s.get("search_project_folders", "true") == "true";
        hide_targets_without_project_name = s.get("hide_targets_without_project_name", "true") == "true";
        hide_targets_without_description = s.get("hide_targets_without_description", "true") == "true";
        hide_targets_starting_with_underscore = s.get("hide_targets_starting_with_underscore", "true") == "true";

        if int(sublime.version()) >= 3000:
            data = self.window.project_data();
            buildfile = data.get("buildfile", None);
            folders = data.get("folders", None);
            if data != None:
                if buildfile != None:
                    self.build = os.path.join(self.working_dir, buildfile);
                    print('Project specified buildfile at "' + self.build + '".');
                elif folders != None and seach_project_folders:
                    print('Project detected searching folders for buildfile');
                    for folder in folders:
                        folder_path = folder.get("path", None);
                        if folder_path != None:
                            current_path = os.path.join(self.working_dir, folder_path);
                            if os.path.exists(current_path + os.sep + build_file):
                                self.build = current_path + os.sep + build_file
                                self.working_dir = current_path;
                                print('Project folder search found buildfile at "' + self.build + '".');
                                break;

        if self.build == None:
            # buildfile by selection: search build file in project folder that file from active view is in  
            try:
                active_file = self.window.active_view().file_name();
                active_folder = os.path.dirname(active_file);
                if os.path.exists(active_folder + os.sep + build_file):
                    self.build = active_folder + os.sep + build_file;
                    self.working_dir = active_folder
                else:
                    print('No "'+build_file+'" found in "' + active_folder+'".');
            except Exception as ex:
                print('Error Searching for "'+build_file+'" in Active Folder.');

        # buildfile by default: build.xml found in your working directory
        if self.build == None and os.path.exists(self.working_dir + os.sep + build_file):
            print('Unable to find "' + build_file + '" in Active Folder. Checking "' + self.working_dir+ '".');
            self.build = self.working_dir + os.sep + build_file;

        #unable to find buildfile anywhere. Time to give up
        if self.build == None:
            print('Unable to find Build File in Active Folder or "' + self.working_dir +'". Showing Settings.');
            self.window.open_file(os.path.join(self.package_dir, 'SuperAnt.sublime-settings'));
            return;

        # Load all projects for this build
        projects = self._get_projects_from_file(self.build, follow_imports, True);

        # loop through all projects and get targets with a description
        targetNames = [];
        for project in projects:
            for target in project.targets:
                targetName = target.getAttributeNode("name").nodeValue;
                showTarget = True;
                if hide_targets_without_description and target.hasAttribute('description') == False :
                    showTarget = False;
                if hide_targets_starting_with_underscore and targetName[0] == "_":
                    showTarget = False;
                if hide_targets_without_project_name and project.name == None:
                    showTarget = False;

                if showTarget:
                    if project.name == None:
                        targetNames.append(targetName);
                    else:
                        targetNames.append(project.name + self.separator + targetName);

        self.targets = sorted(targetNames) if use_sorting else targetNames;
        self.window.show_quick_panel(self.targets, self._quick_panel_callback);

    def _get_projects_from_file(self, file, followImports, mainProject = False):

        try:
            f = open(file);
        except Exception as ex:
            print('The file: "' + file + '" could not be opened');
            return [];

        data = f.read();
        dom = parseString(data);

        # get project name for target prefixing in quick panel
        project_name = None;
        try:
            project_name = dom.getElementsByTagName("project")[0].getAttributeNode('name').nodeValue;
        except Exception as e:
            project_name = None;

        if mainProject == True and project_name != None:
            self.mainProject = project_name;

        project = type('project', (object,), {'name' : project_name, 'targets' : dom.getElementsByTagName('target')})

        projects = [];
        projects.append(project);

        if followImports:
            imports = dom.getElementsByTagName('import');
            for imp in imports:
                importFile = imp.getAttributeNode("file").nodeValue;
                importFile = importFile.replace("${basedir}", self.working_dir);
                projects = projects + self._get_projects_from_file(importFile, followImports);

        return projects;

    def _quick_panel_callback(self, index):

        if (index > -1):
            targetName = self.targets[index];
            if self.mainProject != None:
                targetName = targetName.replace(self.mainProject + self.separator, "");
            
            ant = "ant";
            # Check for Windows Overrides and Merge
            if sys.platform.startswith('win32'):
                ant = "ant.bat";

            cmd = {
                'cmd': [ant, "-f", self.build, targetName],
                'working_dir': self.working_dir
            }

            # run build
            self.window.run_command("exec", cmd);
