function theta = get_knee_angle(pitch, side)
arguments
    pitch struct
    side string
end

joint_group = get_joint_group("knee");
joint_ids = get_joint_ids(joint_group, side);
hip_data = get_joint_data(pitch, joint_ids(1));
knee_data = get_joint_data(pitch, joint_ids(2));
ankle_data = get_joint_data(pitch, joint_ids(3));

% Apply filtering
dt = get_framerate(pitch);
cutoff_freq = 10;
fs = 1/dt;
[b, a] = butter(2, cutoff_freq/(fs/2));
hip_data_filtered = filtfilt(b, a, hip_data);
knee_data_filtered = filtfilt(b, a, knee_data);
ankle_data_filtered = filtfilt(b, a, ankle_data);

theta = get_joint_angle(hip_data_filtered, knee_data_filtered, ...
    ankle_data_filtered);


end