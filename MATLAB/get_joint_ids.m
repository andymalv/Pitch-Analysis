function joint_id = get_joint_ids(joint, side)
arguments
    joint string
    side string
end

num_joints = length(joint);

joint_lookup = struct();
joint_lookup.nose = 1;
joint_lookup.neck = 2;
joint_lookup.eye.right = 16;
joint_lookup.eye.left = 17;
joint_lookup.ear.right = 18;
joint_lookup.ear.left = 19;
joint_lookup.shoulder.right = 3;
joint_lookup.shoulder.left = 6;
joint_lookup.elbow.right = 4;
joint_lookup.elbow.left = 7;
joint_lookup.wrist.right = 5;
joint_lookup.wrist.left = 8;
joint_lookup.thumb.right = 28;
joint_lookup.thumb.left = 25;
joint_lookup.pinky.right = 29;
joint_lookup.pinky.left = 27;
joint_lookup.hip.center = 9;
joint_lookup.hip.right = 10;
joint_lookup.hip.left = 13;
joint_lookup.knee.right = 11;
joint_lookup.knee.left = 14;
joint_lookup.ankle.right = 12;
joint_lookup.ankle.left = 15;
joint_lookup.bigtoe.right = 23;
joint_lookup.bigtoe.left = 20;
joint_lookup.smalltoe.right = 24;
joint_lookup.smalltoe.left = 21;
joint_lookup.heel.right = 25;
joint_lookup.heel.left = 22;

joint_id = zeros(num_joints,1);

for i = 1:num_joints

    try
        if joint(i) == "neck" || joint(i) == "nose"
            joint_id(i) = joint_lookup.(lower(joint(i)));
        else
            joint_id(i) = joint_lookup.(lower(joint(i))).(lower(side));
        end
    catch ME
        error("Joint '%s' and side '%s' combination not found", joint(i), side);
    end

end

end