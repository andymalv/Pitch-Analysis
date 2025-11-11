function theta = get_hand_path(pitch, side)
arguments
    pitch struct
    side string
end

shoulder_id = get_joint_ids("shoulder", side);
wrist_id = get_joint_ids("shoulder", side);
shoulder_data = get_joint_data(pitch, shoulder_id);
wrist_data = get_joint_data(pitch, wrist_id);

% Apply filtering
dt = get_framerate(pitch);
cutoff_freq = 15;
fs = 1/dt;
[b, a] = butter(4, cutoff_freq/(fs/2));
shoulder_data_filtered = filtfilt(b, a, shoulder_data);
wrist_data_filtered = filtfilt(b, a, wrist_data);

num_frames = size(shoulder_data_filtered, 1);

hand_path = shoulder_data_filtered - wrist_data_filtered;
theta = zeros(num_frames, 1);

for i = 2:num_frames

    path_prev = hand_path(i-1, 1:2);
    path_current = hand_path(i, 1:2);

    % Normalize
    if norm(path_prev) > 0.1 && norm(path_current) > 0.1
        path_prev = path_prev / norm(path_prev);
        path_current = path_current / norm(path_current);

        dot_product = dot(path_prev, path_current);
        cross_product = path_prev(1)*path_current(2) - path_prev(2)*path_current(1);
        d_theta = atan2d(cross_product, dot_product);

        theta(i) = theta(i-1) + d_theta;
    else
        theta(i) = theta(i-1);
    end
end

end