function joint_group = get_joint_group(joint)
arguments
    joint string
end

joint = lower(joint);
extra = "";

try
    switch joint
        case "elbow"
            proximal = "shoulder";
            distal = "wrist";
        case "shoulder"
            proximal = "neck";
            distal = "elbow";
            extra = "nose";
        case "knee"
            proximal = "hip";
            distal = "ankle";
    end

catch
    error("Joint grouping not available for '%s'", joint);
end

if extra == ""
    joint_group = [proximal, joint, distal];
else
    joint_group = [proximal, joint, distal, extra];
end

end