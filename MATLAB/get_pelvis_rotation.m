function theta = get_pelvis_rotation(pitch)
arguments
    pitch struct
end

right_hip_id = get_joint_ids("hip", "right");
left_hip_id = get_joint_ids("hip", "left");
right_hip_data = get_joint_data(pitch, right_hip_id);
left_hip_data = get_joint_data(pitch, left_hip_id);

% Apply filtering
dt = get_framerate(pitch);
cutoff_freq = 10;
fs = 1/dt;
[b, a] = butter(2, cutoff_freq/(fs/2));
right_hip_data_filtered = filtfilt(b, a, right_hip_data);
left_hip_data_filtered = filtfilt(b, a, left_hip_data);



theta = get_segment_rotation(right_hip_data_filtered,...
    left_hip_data_filtered, "z");

end