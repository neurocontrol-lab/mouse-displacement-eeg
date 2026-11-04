function root = project_root()
% Repository location, independent of the current working directory.
root = fileparts(fileparts(mfilename('fullpath')));
end
