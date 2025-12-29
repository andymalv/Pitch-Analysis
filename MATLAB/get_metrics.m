function player_data = get_metrics(player)
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
    dt = get_framerate(player.(pitch));

    theta_knee = get_knee_angle(player.(pitch), leg);
    omega_knee = gradient(theta_knee, dt);
    theta_elbow = get_elbow_angle(player.(pitch), arm);
    omega_elbow = gradient(theta_elbow, dt);
    theta_shoulder = get_shoulder_rotation(player.(pitch), arm);
    omega_shoulder = gradient(theta_shoulder, dt);
    theta_pelvis = get_pelvis_rotation(player.(pitch));
    omega_pelvis = gradient(theta_pelvis, dt);
    theta_trunk = get_trunk_rotation(player.(pitch));
    omega_trunk = gradient(theta_trunk, dt);
    theta_hand = get_hand_path(player.(pitch), arm);
    omega_hand = gradient(theta_hand, dt); % think about filtering again

    for j = 1:frames

        player.(pitch)(j).metrics.knee.angle = theta_knee(j);
        player.(pitch)(j).metrics.knee.velocity = omega_knee(j);
        player.(pitch)(j).metrics.elbow.angle = theta_elbow(j);
        player.(pitch)(j).metrics.elbow.velocity = omega_elbow(j);
        player.(pitch)(j).metrics.shoulder.angle = theta_shoulder;
        player.(pitch)(j).metrics.shoulder.velocity = omega_shoulder(j);
        player.(pitch)(j).metrics.pelvis.angle = theta_pelvis(j);
        player.(pitch)(j).metrics.pelvis.velocity = omega_pelvis(j);
        player.(pitch)(j).metrics.trunk.angle = theta_trunk(j);
        player.(pitch)(j).metrics.trunk.velocity = omega_trunk(j);
        player.(pitch)(j).metrics.handPath.angle = theta_hand(j);
        player.(pitch)(j).metrics.handPath.velocity = omega_hand(j);

    end


    % If there's a difference in frames, cut some off the start
    try
        player.metrics.knee.angle(:,:,i) = theta_knee;
        player.metrics.knee.velocity(:,:,i) = omega_knee;
        player.metrics.elbow.angle(:,:,i) = theta_elbow;
        player.metrics.elbow.velocity(:,:,i) = omega_elbow;
        player.metrics.shoulder.angle(:,:,i) = theta_shoulder;
        player.metrics.shoulder.velocity(:,:,i) = omega_shoulder;
        player.metrics.pelvis.angle(:,:,i) = theta_pelvis;
        player.metrics.pelvis.velocity(:,:,i) = omega_pelvis;
        player.metrics.trunk.angle(:,:,i) = theta_trunk;
        player.metrics.trunk.velocity(:,:,i) = omega_trunk;
        player.metrics.handPath.angle(:,:,i) = theta_hand;
        player.metrics.handPath.velocity(:,:,i) = omega_hand;
    catch
        diff = frames - size(player.metrics.knee.angle, 1);
        warning("%s %s has %d frames - removing %d frame(s)",...
            player.name, pitch, frames, diff);

        player.metrics.knee.angle(:,:,i) = theta_knee(1+diff:end, :);
        player.metrics.knee.velocity(:,:,i) = omega_knee(1+diff:end, :);
        player.metrics.elbow.angle(:,:,i) = theta_elbow(1+diff:end, :);
        player.metrics.elbow.velocity(:,:,i) = omega_elbow(1+diff:end, :);
        player.metrics.shoulder.angle(:,:,i) = theta_shoulder(1+diff:end, :);
        player.metrics.shoulder.velocity(:,:,i) = omega_shoulder(1+diff:end, :);
        player.metrics.pelvis.angle(:,:,i) = theta_pelvis(1+diff:end, :);
        player.metrics.pelvis.velocity(:,:,i) = omega_pelvis(1+diff:end, :);
        player.metrics.trunk.angle(:,:,i) = theta_trunk(1+diff:end, :);
        player.metrics.trunk.velocity(:,:,i) = omega_trunk(1+diff:end, :);
        player.metrics.handPath.angle(:,:,i) = theta_hand(1+diff:end, :);
        player.metrics.handPath.velocity(:,:,i) = omega_hand(1+diff:end, :);
    end

end


player.metrics.knee.angle = mean(player.metrics.knee.angle, 3);
player.metrics.knee.velocity = mean(player.metrics.knee.velocity, 3);
player.metrics.elbow.angle = mean(player.metrics.elbow.angle, 3);
player.metrics.elbow.velocity = mean(player.metrics.elbow.velocity, 3);
player.metrics.shoulder.angle = mean(player.metrics.shoulder.angle, 3);
player.metrics.shoulder.velocity = mean(player.metrics.shoulder.velocity, 3);
player.metrics.pelvis.angle = mean(player.metrics.pelvis.angle, 3);
player.metrics.pelvis.velocity = mean(player.metrics.pelvis.velocity, 3);
player.metrics.trunk.angle = mean(player.metrics.trunk.angle, 3);
player.metrics.trunk.velocity = mean(player.metrics.trunk.velocity, 3);
player.metrics.handPath.angle = mean(player.metrics.handPath.angle, 3);
player.metrics.handPath.velocity = mean(player.metrics.handPath.velocity, 3);

player_data = player;

end