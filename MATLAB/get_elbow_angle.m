function theta = get_elbow_angle(pitch, side)
arguments
    pitch struct
    side string
end

joint_group = get_joint_group("elbow");
joint_ids = get_joint_ids(joint_group, side);
shoulder_data = get_joint_data(pitch, joint_ids(1));
elbow_data = get_joint_data(pitch, joint_ids(2));
wrist_data = get_joint_data(pitch, joint_ids(3));

% Apply filtering
dt = get_framerate(pitch);
cutoff_freq = 10;
fs = 1/dt;
[b, a] = butter(2, cutoff_freq/(fs/2));
shoulder_data_filtered = filtfilt(b, a, shoulder_data);
elbow_data_filtered = filtfilt(b, a, elbow_data);
wrist_data_filtered = filtfilt(b, a, wrist_data);

theta = get_joint_angle(shoulder_data_filtered, elbow_data_filtered, ...
    wrist_data_filtered);


end