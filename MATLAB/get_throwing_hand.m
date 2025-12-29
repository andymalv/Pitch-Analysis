function side = get_throwing_hand(player)
arguments
    player struct
end

right_id = get_joint_ids("wrist", "right");
left_id = get_joint_ids("wrist", "left");

right_data = get_joint_data(player.pitch1, right_id);
left_data = get_joint_data(player.pitch1, left_id);

if right_data(1,2) > left_data(1,2)
    side = "right";
elseif right_data(1,2) < left_data(1,2)
    side = "left";
else
    error("Unable to determine throwing hand. Please check data.")
end


end