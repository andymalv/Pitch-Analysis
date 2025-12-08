function theta = get_joint_angle(proximal_data, joint_data, distal_data, extra_data)
arguments
    proximal_data (:,3) double
    joint_data (:,3) double
    distal_data (:,3) double
    extra_data (:,3) double = 0
end

num_frames = size(joint_data,1);

if extra_data ~= 0

    distal_segment = joint_data - distal_data;
    intermediate_segment = joint_data - proximal_data;
    extra_segment = extra_data - proximal_data;
    proximal_segment = cross(extra_segment, intermediate_segment);

else

    distal_segment = joint_data - distal_data;
    proximal_segment = proximal_data - joint_data;

end

theta = zeros(num_frames, 1);

for i = 1:num_frames

    proximal_vector = proximal_segment(i,:);
    distal_vector = distal_segment(i,:);

    % Faster, but doesn't perform well w/ tiny angles
    % dot_product = dot(proximal_vector, distal_vector);
    % upper_arm_mag = norm(proximal_vector);
    % forearm_mag = norm(distal_vector);
    %
    % cos_theta = dot_product / (upper_arm_mag * forearm_mag);
    % cos_theta = max(min(cos_theta, 1), -1); % for stability
    %
    % theta(i) = acosd(cos_theta);

    % Slower, but works better w/ tiny angles
    theta(i) = atan2d(norm(cross(proximal_vector, distal_vector)), ...
        dot(proximal_vector, distal_vector));

end



end