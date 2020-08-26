%%%%% SETUP %%%%%

% Get path to Canvas assignment downloads folder
% and create mbgrader submissions folder
assignment_folder = input('Enter assignment folder [canvas/{*}]: ','s');
canvas_submissions = fullfile('canvas',assignment_folder);
mbgrader_submissions = fullfile('submissions',assignment_folder);
if isfolder(mbgrader_submissions)
    rmdir(mbgrader_submissions,'s');
end
mkdir(mbgrader_submissions);

% Get path to Canvas classlist and read Canvas IDs and Studend Numbers
disp('Classlist format (Canvas ID, Student Number) with no header.')
classlist_filename = input('Enter Canvas classlist filename [./classlist.csv]: ','s');
if strcmp(classlist_filename,'')
    classlist_filename = 'classlist.csv';
end
classlist = readmatrix(classlist_filename);
classlist = classlist(2:end-1,[2 5]);

% Enter variable names to ignore (such as data provided with assignment)
ignore_vars = input('Enter variable names to ignore (as comma-separated list with no spaces such as ans,varA,varB): ','s');
ignore_vars = split(ignore_vars,',');

% Enter preferred variable names if there are naming conflicts (such as upper
% and lower case names like A and a, X and x, ...)
preferred_names = input('Enter preferred variable names (as comma-separated list with no spaces such as X,Y,Z): ','s');
preferred_names = split(preferred_names,',');

% Copy Canvas submissions to temporary folder
temp = 'temp';
if isfolder(temp)
    rmdir(temp,'s');
end
copyfile(canvas_submissions,temp);

% Create issues folder for student files that will not open
issues = fullfile('issues',assignment_folder);
if isfolder(issues)
    rmdir(issues,'s');
end
mkdir(issues);

% Find .mat and .fig files in temporary folder
mat_files = dir(fullfile(temp,'*.mat'));
fig_files = dir(fullfile(temp,'*.fig'));

%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%% READ .MAT FILES %%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%

for i=1:length(mat_files)
    
    % Get Canvas ID and student number from Canvas filename
    filename = mat_files(i).name;
    [canvas_id,student_number] = get_canvas_id_student_number(filename,classlist);
    
    % Load .mat file or copy to issues folder and skip if it will not open
    try
        S = load(fullfile(temp,filename));
    catch
        copyfile(fullfile(temp,filename),issues);
        f = fopen(fullfile(issues,'issues.txt'),'a');
        fprintf(f,['Could not open .mat file for Student Number ',student_number,' Canvas ID ',canvas_id,'\n']);
        fclose(f);
        continue
    end
    
    % Create destination folder for student variables in .mat file
    destination = fullfile(mbgrader_submissions,student_number);
    if isfolder(destination)
        f = fopen(fullfile(issues,'issues.txt'),'a');
        fprintf(f,['Multiple .mat submissions for Student Number ',student_number,' Canvas ID ',canvas_id,'\n']);
        fclose(f);
    else
        mkdir(destination);
        f = fopen(fullfile(destination,'filename.txt'),'w');
        fprintf(f,'%s',filename);
        fclose(f);
    end
    
    % Load and write each variable to its own file in destination folder
    vars = fieldnames(S);
    for i=1:length(vars)
        varname = vars{i};
        value = getfield(S,varname);
        
        % Ignore the variable called filename and any other user specified
        % variable names to ignore, and skip duplicate variable names
        if strcmp(varname,'filename') || any(strcmp(ignore_vars,varname))
            continue
        elseif ~isempty(dir([varname,'.*'])) && ~any(strcmp(varname,preferred_names))
            f = fopen(fullfile(issues,'issues.txt'),'a');
            fprintf(f,['Duplicate variable ',varname,' ignored for Student Number ',student_number,' Canvas ID ',canvas_id,'\n']);
            fclose(f);
            continue
        end

        % Write variable data to file
        if isa(value,'string') || isa(value,'char')
            target = fullfile(destination,[varname,'.txt']);
            f = fopen(target,'w');
            fprintf(f,'%s',value);
            fclose(f);
        elseif isa(value,'double')
            target = fullfile(destination,[varname,'.csv']);
            dlmwrite(target,value,'precision',10);
        elseif isa(value,'sym') || isa(value,'symfun')
            target = fullfile(destination,[varname,'.sym']);
            f = fopen(target,'w');
            fprintf(f,'%s',char(value));
            fclose(f);
        elseif isa(value,'function_handle')
            target = fullfile(destination,[varname,'.txt']);
            f = fopen(target,'w');
            fprintf(f,'%s',func2str(value));
            fclose(f);
        elseif isa(value,'struct')
            target = fullfile(destination,[varname,'.txt']);
            f = fopen(target,'w');
            fprintf(f,'Cannot read type struct.');
            fclose(f);
        else
            target = fullfile(destination,[varname,'.txt']);
            f = fopen(target,'w');
            fprintf(f,'%s','Do not recognize datatype.');
            fclose(f);
        end
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%% READ .FIG FILES %%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%

for i=1:length(fig_files)
    
    close all;
    % Get Canvas ID and student number from Canvas filename
    filename = fig_files(i).name;
    [canvas_id,student_number,real_filename] = get_canvas_id_student_number(filename,classlist);
    
    % Create destination folder for student variables in .fig file
    destination = fullfile(mbgrader_submissions,student_number);
    if ~isfolder(destination)
        mkdir(destination);
    end

    % Open .fig file or copy to issues folder and skip if it will not open
    try
        fig = openfig(fullfile(temp,filename),'invisible');
    catch
        copyfile(fullfile(temp,filename),issues);
        f = fopen(fullfile(issues,'issues.txt'),'a');
        fprintf(f,['Could not open .fig file for Student Number ',student_number,' Canvas ID ',canvas_id,'\n']);
        fclose(f);
        continue
    end
    ax = gca;
    if isempty(ax)
        continue
    end
    s.Title = ax.Title.String;
    s.XLabel = ax.XLabel.String;
    s.YLabel = ax.YLabel.String;
    Lines = findobj(ax,'Type','line');
    s.Lines = cell(1,length(Lines));
    for n=1:length(Lines)
        s.Lines{n} = [Lines(n).XData' Lines(n).YData'];
    end
    output = jsonencode(s);
    [~,name,~] = fileparts(real_filename);
    target = fullfile(destination,[name,'.json']);
    f = fopen(target,'w');
    fprintf(f,'%s',output);
    fclose(f);
end
    
rmdir(temp,'s');
clear; close all;

%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%% GET ID FUNCTION %%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [canvas_id,student_number,real_filename] = get_canvas_id_student_number(filename,classlist)

underscores = strfind(filename,'_');
if strcmpi(filename(underscores(1)+1:underscores(2)-1),'late')
    canvas_id = filename(underscores(2)+1:underscores(3)-1);
    filename_with_extension = filename(underscores(4)+1:end);
else
    canvas_id = filename(underscores(1)+1:underscores(2)-1);
    filename_with_extension = filename(underscores(3)+1:end);
end

[~,name,ext] = fileparts(filename_with_extension);
name = split(name,{' ','-','(',')'});
name = name{1};
real_filename = [name,ext];

index = find(classlist(:,1) == str2num(canvas_id));
if isempty(index)
    disp(['Cannot find ',num2str(canvas_id),' in the classlist.']);
    student_number = canvas_id;
else
    student_number = num2str(classlist(index,2));
end

end