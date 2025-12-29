function theta = get_trunk_rotation(pitch)
arguments
    pitch struct
end

right_shoulder_id = get_joint_ids("shoulder", "right");
left_shoulder_id = get_joint_ids("shoulder", "left");
right_shoulder_data = get_joint_data(pitch, right_shoulder_id);
left_shoulder_data = get_joint_data(pitch, left_shoulder_id);

% Apply filtering
dt = get_framerate(pitch);
cutoff_freq = 10;
fs = 1/dt;
[b, a] = butter(2, cutoff_freq/(fs/2));
right_shoulder_data_filtered = filtfilt(b, a, right_shoulder_data);
left_shoulder_data_filtered = filtfilt(b, a, left_shoulder_data);



theta = get_segment_rotation(right_shoulder_data_filtered,...
    left_shoulder_data_filtered, "z");

end
