function df = get_data(directory)
arguments
    directory string
end

file_pattern = fullfile(directory, '*.json');
files = dir(file_pattern);

num_files = length(files);
df = struct;
name = char(directory);
df.name = string(name(4:end));

fprintf("Gathering data for %s...\n", df.name);

for i = 1:num_files
    try
        file_path = fullfile(directory, files(i).name);
        data_hold = readstruct(file_path);

    catch ME
        warning('Error reading file %s: %s', files(i).name, ME.message);
    end

    field_name = strcat("pitch", num2str(i));
    df.(field_name) = data_hold.skeletalData.frames;

end

end