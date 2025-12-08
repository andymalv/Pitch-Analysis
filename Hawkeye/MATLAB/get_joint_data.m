function joint_data = get_joint_data(pitch, joint_id)
arguments
    pitch struct
    joint_id double
end

num_frames = length(pitch);

joint_data = zeros(num_frames, 3);


% Get joint data
for i = 1:num_frames

    joint_data(i,:) = [pitch(i).positions.joints(joint_id).x,...
        pitch(i).positions.joints(joint_id).y,...
        pitch(i).positions.joints(joint_id).z];

end


end