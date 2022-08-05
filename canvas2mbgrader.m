%%%%%%%%%%%%%%%%%
%%%%% SETUP %%%%%
%%%%%%%%%%%%%%%%%

% Read Canvas IDs and Student Numbers
if isfile('canvasIDstudentID.csv')
    classlist = readmatrix('canvasIDstudentID.csv');
else
    disp('File canvasIDstudentID.csv not found.')
    disp('Create csv file with Canvas IDs in first column and Student IDs in second column (no header).')
    disp('Save as canvasIDstudentID.csv in current directory.')
    return
end
fprintf('Found %d students in the classlist.\n',length(classlist));

% Get path to Canvas assignment downloads folder
% and create mbgrader submissions folder
assignment_folder = input('Enter assignment folder [canvas/{*}]: ','s');
canvas_submissions = fullfile('canvas',assignment_folder);
if ~isdir(canvas_submissions)
    disp(['Cannot find assignment: ', assignment_folder])
    clear assignment_folder canvas_submissions classlist
    return
end
mbgrader_submissions = fullfile('submissions',assignment_folder);
if isfolder(mbgrader_submissions)
    rmdir(mbgrader_submissions,'s');
end
mkdir(mbgrader_submissions);

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

disp('Loading MATLAB files to mbgrader/submissions folder ...')

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
    saved_vars = 0;
    for i=1:length(vars)
        varname = vars{i};
        value = getfield(S,varname);
        varname = lower(varname);
        % Ignore variable filename and skip duplicate variable names (ie. x and X)
        if strcmp(varname,'filename')
            continue
        elseif ~isempty(dir([varname,'.*']))
            f = fopen(fullfile(issues,'issues.txt'),'a');
            fprintf(f,['Duplicate variable ',varname,' ignored for Student Number ',student_number,' Canvas ID ',canvas_id,'\n']);
            fclose(f);
            continue
        end

        saved_vars = saved_vars + 1;
        % Write variable data to file
        if isa(value,'string') || isa(value,'char')
            target = fullfile(destination,[varname,'.txt']);
            f = fopen(target,'w');
            fprintf(f,'%s',value);
            fclose(f);
        elseif isa(value,'double')
            target = fullfile(destination,[varname,'.csv']);
            dlmwrite(target,value,'precision',10);
        elseif isa(value,'logical')
            target = fullfile(destination,[varname,'.log']);
            dlmwrite(target,value,'precision',1);
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
    if saved_vars == 0
        f = fopen(fullfile(issues,'issues.txt'),'a');
        fprintf(f,['No variables found for Student Number ',student_number,' Canvas ID ',canvas_id,' filename ',filename,'\n']);
        fclose(f);
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
    null_values = false;
    for n=1:length(Lines)
        if any(isnan(Lines(n).XData)) || any(isnan(Lines(n).YData)) || any(isinf(Lines(n).XData)) || any(isinf(Lines(n).YData))
            copyfile(fullfile(temp,filename),issues);
            f = fopen(fullfile(issues,'issues.txt'),'a');
            fprintf(f,['Null/Inf values in .fig file for Student Number ',student_number,' Canvas ID ',canvas_id,'\n']);
            fclose(f);
            null_values = true;
            break
        end
        s.Lines{n} = [Lines(n).XData' Lines(n).YData'];
    end
    if null_values
        continue
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
name = split(name,{' ','-','(',')','.'});
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
