function theta = get_segment_rotation(point1_data, point2_data, rotation_axis)
arguments
    point1_data (:,3) double
    point2_data (:,3) double
    rotation_axis string
end

num_frames = size(point1_data,1);

switch lower(rotation_axis)
    case "x"
        rotation_axis = [1, 0, 0];
    case "y"
        rotation_axis = [0, 1, 0];
    case "z"
        rotation_axis = [0, 0, 1];
    otherwise
        error("Invalid axis input")
end

theta = zeros(num_frames, 1);

start_axis1 = abs(point1_data(1,:) - point2_data(1,:));
start_axis2 = cross(rotation_axis, start_axis1);
start_axis2 = start_axis2 / norm(start_axis2);

for i = 2:num_frames
    axis1 = abs(point1_data(i,:) - point2_data(i,:));
    axis2 = cross(rotation_axis, axis1);
    axis2_current = axis2 / norm(axis2);

    dot_product = dot(start_axis2(1:2), axis2_current(1:2));
    cross_product = start_axis2(1)*axis2_current(2) - ...
        start_axis2(2)*axis2_current(1);
    d_theta = atan2d(cross_product, dot_product);

    theta(i) = theta(i-1) + d_theta;
    start_axis2 = axis2_current;
end

end