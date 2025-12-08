function run_pitch_analysis()

% clear all
close all

% Find subdirectories (ie player folders)
d = dir('..');
isub = [d(:).isdir];
directories = {d(isub).name}';
directories = directories(contains(directories, "player"));
players = string(directories);

for i = 1:length(players)

    player = players(i);

    player_data = get_data(strcat("../", player));
    df.(player) = get_metrics(player_data);

end

window_size = [300 150];

% Select Player
players = strrep(players, "player", "Player ");
player_index = listdlg('ListString', players, 'SelectionMode', 'single',...
    "Name", "Select Player to Analyze", "ListSize", window_size);

if isempty(player_index), return; end
player_selection = string(players{player_index});
player_selection = strrep(player_selection, "Player ", "player");

% Select pitches
pitches = string(fieldnames(df.(player_selection)));
pitches = pitches(contains(pitches, "pitch", "IgnoreCase", true));
pitches = strrep(pitches, "pitch", "Pitch ");
pitch_index = listdlg('ListString', pitches, 'SelectionMode', 'multiple',...
    "Name", "Select Pitch to Analyze", "ListSize", window_size);

if isempty(pitch_index), return; end
pitches_selection = pitches(pitch_index);

% Select metrics
metrics = ["Knee Flexion", "Elbow Flexion", "Shoulder Rotation", ...
    "Elbow Extension Velocity", "Pelvis Angular Velocity", ...
    "Trunk Angular Velocity", "Hand Angular Velocity"];
metrics_index = listdlg('ListString', metrics, 'SelectionMode', 'multiple',...
    "Name", "Select Metrics to Plot", "ListSize", window_size);

if isempty(metrics_index), return; end
metrics_selection = metrics(metrics_index);


% Plot
plot_metrics(df.(player_selection), pitches_selection, metrics_selection);

end