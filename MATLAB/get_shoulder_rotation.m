function theta = get_shoulder_rotation(pitch, side)
arguments
    pitch struct
    side string
end

joint_group = get_joint_group("shoulder");
joint_ids = get_joint_ids(joint_group, side);
neck_data = get_joint_data(pitch, joint_ids(1));
shoulder_data = get_joint_data(pitch, joint_ids(2));
elbow_data = get_joint_data(pitch, joint_ids(3));
nose_data = get_joint_data(pitch, joint_ids(4));

% Apply filtering
dt = get_framerate(pitch);
cutoff_freq = 10;
fs = 1/dt;
[b, a] = butter(2, cutoff_freq/(fs/2));
hip_data_filtered = filtfilt(b, a, neck_data);
knee_data_filtered = filtfilt(b, a, shoulder_data);
ankle_data_filtered = filtfilt(b, a, elbow_data);
nose_data_filtered = filtfilt(b, a, nose_data);

theta = get_joint_angle(hip_data_filtered, knee_data_filtered, ...
    ankle_data_filtered, nose_data_filtered);

end