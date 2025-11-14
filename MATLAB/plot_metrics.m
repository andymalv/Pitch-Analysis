function plot_metrics(player, pitch_index, metrics)

player_name = strrep(player.name, "player", "Player ");

pitches = string(fieldnames(df.(player_selection)));
pitches = pitches(contains(pitches, "pitch", "IgnoreCase", true));

pitches_selected = pitches(pitch_index);
num_pitches = length(pitches_selected);

if num_pitches == length(pitches)

    theta_knee = player.metrics.kneeFlexion;
    theta_elbow = player.metrics.kneeFlexion;
    theta_shoulder = player.metrics.kneeFlexion;
    omega_elbow = player.metrics.kneeFlexion;
    omega_pelvis = player.metrics.kneeFlexion;
    omega_trunk = player.metrics.kneeFlexion;
    omega_hand = player.metrics.kneeFlexion;

else

    for i = 1:num_pitches



    end


end

num_metrics = length(metrics);
rows = ceil(num_metrics/2);
cols = 2;
i = 1;

figure('Position', [100, 100, 1000, rows*200]);

if ismember("Knee Flexion", metrics)
    subplot(rows, cols, i);
    plot(theta_knee, 'LineWidth', 2);
    title(sprintf("%s Mean Knee Flexion", player_name));
    xticks("manual");
    ylabel("Flexion Angle (deg)");
    grid on;
    hold on;
    i = i+1;
end

if ismember("Shoulder Rotation", metrics)
    subplot(rows, cols, i);
    plot(theta_shoulder, 'LineWidth', 2);
    title(sprintf("%s Mean Shoulder Rotation", player_name))
    xticks("manual");
    ylabel("Rotation Angle (deg)");
    grid on;
    hold on;
    i = i+1;
end

if ismember("Elbow Flexion", metrics)
    subplot(rows, cols, i);
    plot(theta_elbow, 'LineWidth', 2);
    title(sprintf("%s Mean Elbow Flexion", player_name))
    xticks("manual");
    ylabel("Flexion Angle (deg)");
    grid on;
    hold on;
    i = i+1;
end

if ismember("Elbow Velocity", metrics)
    subplot(rows, cols, i);
    plot(omega_elbow, 'LineWidth', 2);
    title(sprintf("%s Mean Elbow Extension Velocity", player_name))
    xticks("manual");
    ylabel("Extension Velocity (deg/s)");
    grid on;
    hold on;
    i = i+1;
end

if ismember("Pelvis Velocity", metrics)
    subplot(rows, cols, i);
    plot(omega_pelvis, 'LineWidth', 2);
    title(sprintf("%s Mean Pelvis Angular Velocity", player_name))
    xticks("manual");
    ylabel("Angular Velocity (deg/s)");
    grid on;
    hold on;
    i = i+1;
end

if ismember("Trunk Velocity", metrics)
    subplot(rows, cols, i);
    plot(omega_trunk, 'LineWidth', 2);
    title(sprintf("%s Mean Trunk Angular Velocity", player_name))
    xticks("manual");
    ylabel("Angular Velocity (deg/s)");
    grid on;
    hold on;
    i = i+1;
end

if ismember("Hand Velocity", metrics)
    subplot(rows, cols, i);
    plot(omega_hand, 'LineWidth', 2);
    title(sprintf("%s Mean Hand Angular Velocity", player_name))
    xticks("manual");
    ylabel("Angular Velocity (deg/s)");
    grid on;
end

end