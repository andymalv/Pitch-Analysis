function player_data = new_metrics(player)
arguments
    player struct
end

arm = get_throwing_hand(player);

if arm == "right"
    leg = "left";
elseif arm == "left"
    leg = "right";
end

pitches = string(fieldnames(player));
pitches = pitches(contains(pitches, "pitch", "IgnoreCase", true));
num_pitches = length(pitches);

player.metrics = struct;

fprintf("Calculating metrics for %s...\n", player.name);

for i = 1:num_pitches

    pitch = pitches(i);
    frames = length(player.(pitch));

    

    theta_knee = get_knee_angle(player.(pitch), leg);
    theta_elbow = get_elbow_angle(player.(pitch), arm);
    theta_shoulder = get_shoulder_rotation(player.(pitch), arm);
    omega_elbow = get_elbow_extension_velocity(player.(pitch), arm);
    omega_pelvis = get_pelvis_angular_velocity(player.(pitch));
    omega_trunk = get_trunk_angular_velocity(player.(pitch));
    omega_hand = get_hand_angular_velocity(player.(pitch), arm);

    for j = 1:frames

        player.(pitch)(j).metrics.kneeFlexion = theta_knee(j);
        player.(pitch)(j).metrics.elbowFlexion = theta_elbow(j);
        player.(pitch)(j).metrics.shoulderRotation = theta_shoulder(j);
        player.(pitch)(j).metrics.elbowVelocity = omega_elbow(j);
        player.(pitch)(j).metrics.pelvisVelocity = omega_pelvis(j);
        player.(pitch)(j).metrics.trunkVelocity = omega_trunk(j);
        player.(pitch)(j).metrics.handVelocity = omega_hand(j);

    end


    % If there's a difference in frames, cut some off the start
    try
        player.metrics.kneeFlexion(:,:,i) = theta_knee;
        player.metrics.elbowFlexion(:,:,i) = theta_elbow;
        player.metrics.shoulderRotation(:,:,i) = theta_shoulder;
        player.metrics.elbowVelocity(:,:,i) = omega_elbow;
        player.metrics.pelvisVelocity(:,:,i) = omega_pelvis;
        player.metrics.trunkVelocity(:,:,i) = omega_trunk;
        player.metrics.handVelocity(:,:,i) = omega_hand;
    catch
        diff = frames - size(player.metrics.kneeFlexion, 1);
        warning("%s %s has %d frames - removing %d frame(s)",...
            player.name, pitch, frames, diff);

        player.metrics.kneeFlexion(:,:,i) = theta_knee(1+diff:end, :);
        player.metrics.elbowFlexion(:,:,i) = theta_elbow(1+diff:end, :);
        player.metrics.shoulderRotation(:,:,i) = theta_shoulder(1+diff:end, :);
        player.metrics.elbowVelocity(:,:,i) = omega_elbow(1+diff:end, :);
        player.metrics.pelvisVelocity(:,:,i) = omega_pelvis(1+diff:end, :);
        player.metrics.trunkVelocity(:,:,i) = omega_trunk(1+diff:end, :);
        player.metrics.handVelocity(:,:,i) = omega_hand(1+diff:end, :);
    end

end


player.metrics.kneeFlexion = mean(player.metrics.kneeFlexion, 3);
player.metrics.elbowFlexion = mean(player.metrics.elbowFlexion, 3);
player.metrics.shoulderRotation = mean(player.metrics.shoulderRotation, 3);
player.metrics.elbowVelocity = mean(player.metrics.elbowVelocity, 3);
player.metrics.pelvisVelocity = mean(player.metrics.pelvisVelocity, 3);
player.metrics.trunkVelocity = mean(player.metrics.trunkVelocity, 3);
player.metrics.handVelocity = mean(player.metrics.handVelocity, 3);

player_data = player;

end