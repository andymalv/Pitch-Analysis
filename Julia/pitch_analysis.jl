# %%
using JSON, DataFrames, LinearAlgebra, DSP
# using Match

# %%
@kwdef mutable struct Pitch
    positions :: Vector{DataFrame}
    ∆t :: Vector{String} 
    metrics :: Vector{DataFrame}
end

@kwdef mutable struct Player
    name :: String
    pitches :: Vector{Pitch}
    metrics :: Vector{DataFrame}
end    

# %%
function get_data(directory::String)::Player
    name = directory[4:end]
    println("Gathering data for ", name, "...\n")

    files = readdir(directory)
    files = files[occursin.(".json", files)]
    num_files = length(files)
    pitches = Pitch[]

    for i ∈ 1:num_files 
        path = directory * "/" * files[i]
        data = JSON.parsefile(path)

        num_frames = length(data["skeletalData"]["frames"])
        time_stamps = [data["skeletalData"]["frames"][j]["timeStamp"] for j ∈ 1:num_frames]
        positions = DataFrame[]
        num_joints = length(data["skeletalData"]["frames"][1]["positions"][1]["joints"])
        
        # for j ∈ 1:num_frames
        #
        #     hold = DataFrame(x=Float64[], y=Float64[], z=Float64[])
        #     
        #     for k ∈ 1:num_joints
        #         x = data["skeletalData"]["frames"][j]["positions"][1]["joints"][k]["x"]
        #         y = data["skeletalData"]["frames"][j]["positions"][1]["joints"][k]["y"]
        #         z = data["skeletalData"]["frames"][j]["positions"][1]["joints"][k]["z"]
        #         push!(hold, [x y z])
        #
        #     end
        #
        #     push!(positions, hold)
        # end
        for j ∈ 1:num_joints

            hold = DataFrame(x=Float64[], y=Float64[], z=Float64[])
            
            for k ∈ 1:num_frames
                x = data["skeletalData"]["frames"][k]["positions"][1]["joints"][j]["x"]
                y = data["skeletalData"]["frames"][k]["positions"][1]["joints"][j]["y"]
                z = data["skeletalData"]["frames"][k]["positions"][1]["joints"][j]["z"]
                push!(hold, [x y z])

            end

            push!(positions, hold)
        end


        pitch = Pitch(positions=positions, ∆t=time_stamps, metrics=[])
        push!(pitches, pitch)

    end

    player = Player(name=name, pitches=pitches, metrics=[])

    return player

end

# Vector input
function get_joint_ids(joint::Vector{String}, side::String)::Vector{Int}
    
    joint_lookup = Dict(
        "nose" => 0,
        "neck" => 1,
        "eye_right" => 15,
        "eye_left"=> 16,
        "shoulder_right"=> 2,
        "shoulder_left" => 5,
        "elbow_right" => 3,
        "elbow_left" => 6,
        "wrist_right" => 4,
        "wrist_left" => 7,
        "thumb_right" => 27,
        "thumb_left" => 24,
        "pinky_right" => 28,
        "pinky_left" => 26,
        "hip_center" => 8,
        "hip_right" => 9,
        "hip_left" => 12,
        "knee_right" => 10,
        "knee_left" => 13,
        "ankle_right" => 11,
        "ankle_left" => 14,
        "bigtoe_right" => 22,
        "bigtoe_left" => 19,
        "smalltoe_right" => 23,
        "smalltoe_left" => 20,
        "heel_right" => 24,
        "heel_left" => 21,
    )

    num_joints = length(joint)
    joint_id = Int[]

    for i ∈ 1:num_joints
        try
            if joint[i] == "nose" || joint[i] == "neck"
                this_joint = joint[i]
            else
                this_joint = joint[i] * "_" * side
            end

            push!(joint_id, joint_lookup[this_joint])

        catch
            println("Joint ", joint[i], " and side ", side, " combination not found.")
        end

    end

    return joint_id

end


# Single input
function get_joint_ids(joint::String, side::String)::Int
    
    joint_lookup = Dict(
        "nose" => 0,
        "neck" => 1,
        "eye_right" => 15,
        "eye_left"=> 16,
        "shoulder_right"=> 2,
        "shoulder_left" => 5,
        "elbow_right" => 3,
        "elbow_left" => 6,
        "wrist_right" => 4,
        "wrist_left" => 7,
        "thumb_right" => 27,
        "thumb_left" => 24,
        "pinky_right" => 28,
        "pinky_left" => 26,
        "hip_center" => 8,
        "hip_right" => 9,
        "hip_left" => 12,
        "knee_right" => 10,
        "knee_left" => 13,
        "ankle_right" => 11,
        "ankle_left" => 14,
        "bigtoe_right" => 22,
        "bigtoe_left" => 19,
        "smalltoe_right" => 23,
        "smalltoe_left" => 20,
        "heel_right" => 24,
        "heel_left" => 21,
    )

    try
        if joint == "nose" || joint == "neck"
            this_joint = joint
        else
            this_joint = joint * "_" * side
        end
    catch
        println("Joint ", joint, " and side ", side, " combination not found.")
    end

    joint_id = joint_lookup[this_joint]

    return joint_id

end


function get_joint_data(pitch::Pitch, joint::Int)::DataFrame
    # num_frames = length(pitch.∆t)
    joint_data = pitch.positions[joint]

end


function get_throwing_hand(player::Player)::String
    right_id = get_joint_ids("wrist", "right")
    left_id = get_joint_ids("wrist", "left")

    right_data = get_joint_data(player.pitches[1], right_id)
    left_data = get_joint_data(player.pitches[1], left_id)

    try
        if right_data[1,2] > left_data[1,2]
            side = "right"
        elseif right_data[1,2] < left_data[1,2]
            side = "left"
        end
    catch
        println("Could not determine pitching hand for ", player.name)
    end

    return side
    
end

function get_joint_group(joint::String)::Vector{String}
    extra = ""

    # @match joint begin
    #     "elbow" => proximal = "shoulder", distal = "wrist"
    #     "shoulder" => proximal = "neck", distal = "elbow", extra = "nose"
    #     "knee" => proximal = "hip", distal = "ankle"
    #     _ => println("Joint grouping not available for ", joint)
    # end
    if joint == "elbow"
        proximal = "shoulder"
        distal = "wrist"
    elseif joint == "shoulder"
        proximal = "neck"
        distal = "elbow"
        extra = "nose"
    elseif joint == "knee"
        proximal = "hip"
        distal = "ankle"
    else
        println("Joint grouping not available for ", joint)
    end

    if extra == ""
        joint_group = [proximal, joint, distal]
    else
        joint_group = [proximal, joint, distal, extra]
    end

    return joint_group

end


function get_framerate(pitch::Pitch)::Float64
    first = parse(Float64, pitch.∆t[1][18:end-1])
    last = parse(Float64, pitch.∆t[end][18:end-1])

    if (last - first) < 0
        last = 60 + last
    end

    framerate = (last - first) / length(pitch.∆t)

    return framerate

end


function get_joint_angle(
    proximal_data::DataFrame,
    joint_data::DataFrame,
    distal_data::DataFrame,
    extra_data = nothing
)::DataFrame
    num_frames = size(joint_data)[1]

    distal_segment = joint_data - distal_data

    if extra_data != nothing && size(extra_data)[1] == size(joint_data)[1]
        intermediate_segment = joint_data - proximal_data
        extra_segment = extra_data - proximal_data
        proximal_segment = cross(extra_segment, intermediate_segment)
    else
        proximal_segment = proximal_data - joint_data
    end

    Θ = zeros(num_frames)

    for i ∈ 1:num_frames
        proximal_vector = proximal_segment[i,:]
        distal_vector = distal_segment[i,:]
        
        Θ[i] = atand(
            norm(cross(proximal_vector, distal_vector)),
            dot(proximal_vector, distal_vector)
        )

    end

    return Θ

end


# %%
function filter_data(data::DataFrame, ∆t::Float64, cutoff::Int, order::Int)::DataFrame
    nyquist_freq = 1 / (∆t * 2)
    filter = digitalfilter(Lowpass(cutoff/nyquist_freq), Butterworth(order))
    filtered_data = filtfilt(filter, Matrix{Float64}(data))

    return DataFrame(filtered_data, :auto)
    
end


function get_elbow_angle(pitch::Pitch, side::String)::DataFrame
    joint_group = get_joint_group("elbow")
    joint_ids = get_joint_ids(joint_group, side)
    shoulder_data = get_joint_data(pitch, joint_ids[1])
    elbow_data = get_joint_data(pitch, joint_ids[2])
    wrist_data = get_joint_data(pitch, joint_ids[3])

    ∆t = get_framerate(pitch)
    cutoff = 10
    order = 2
    shoulder_data_filtered = filter_data(
        shoulder_data, ∆t, cutoff, order)
    elbow_data_filtered = filter_data(
        elbow_data, ∆t, cutoff, order)
    wrist_data_filtered = filter_data(
        wrist_data, ∆t, cutoff, order)

    Θ = get_joint_angle(
        shoulder_data_filtered, elbow_data_filtered, wrist_data_filtered)

    return Θ

end


function get_knee_angle(pitch::Pitch, side::String)::DataFrame
    joint_group = get_joint_group("knee")
    joint_ids = get_joint_ids(joint_group, side)
    hip_data = get_joint_data(pitch, joint_ids[1])
    knee_data = get_joint_data(pitch, joint_ids[2])
    ankle_data = get_joint_data(pitch, joint_ids[3])

    ∆t = get_framerate(pitch)
    cutoff = 10
    order = 2
    hip_data_filtered = filter_data(
        hip_data, ∆t, cutoff, order)
    knee_data_filtered = filter_data(
        knee_data, ∆t, cutoff, order)
    ankle_data_filtered = filter_data(
        ankle_data, ∆t, cutoff, order)

    Θ = get_joint_angle(
        hip_data_filtered, knee_data_filtered, ankle_data_filtered)

    return Θ

end


function get_shoulder_rotation(pitch::Pitch, side::String)::DataFrame
    joint_group = get_joint_group("shoulder")
    joint_ids = get_joint_ids(joint_group, side)
    neck_data = get_joint_data(pitch, joint_ids[1])
    shoulder_data = get_joint_data(pitch, joint_ids[2])
    elbow_data = get_joint_data(pitch, joint_ids[3])
    nose_data = get_joint_data(pitch, joint_ids[4])

    ∆t = get_framerate(pitch)
    cutoff = 10
    order = 2
    neck_data_filtered = filter_data(
        neck_data, ∆t, cutoff, order)
    shoulder_data_filtered = filter_data(
        shoulder_data, ∆t, cutoff, order)
    elbow_data_filtered = filter_data(
        elbow_data, ∆t, cutoff, order)
    nose_data_filtered = filter_data(
        nose_data, ∆t, cutoff, order)

    Θ = get_joint_angle(
        neck_data_filtered, shoulder_data_filtered,
        elbow_data_filtered, nose_data_filtered)

    return Θ

end


# %%
function get_segment_rotation(
    point1_data::DataFrame, point2_data::DataFrame, rotation_axis::String
)::DataFrame
    point1_data = Matrix{Float64}(point1_data)
    point2_data = Matrix{Float64}(point2_data)

    if lowercase(rotation_axis) == "x"
        rotation_axis = [1, 0, 0]
    elseif lowercase(rotation_axis) == "y"
        rotation_axis = [0, 1, 0]
    elseif lowercase(rotation_axis) == "z"
        rotation_axis = [0, 0, 1]
    else
        println("Error: invalid axis input: ", rotation_axis)
    end

    num_frames = size(point1_data)[1]
    Θ = zeros(num_frames)

    start_axis1 = abs(point1_data[1,:] - point2_data[1,:])
    start_axis2 = cross(rotation_axis, start_axis1)
    start_axis2 = start_axis2 / norm(start_axis2)

    for i ∈ 2:num_frames
        axis1 = abs(point1_data[i,:] - point2_data[i,:])
        axis2 = cross(rotation_axis, axis1)
        current_axis2 = axis2 / norm(axis2)

        dot_product = dot(start_axis2[1], current_axis2[1])
        cross_product = (
            start_axis2[1] * current_axis2[2] - start_axis2[2] * curent_axis2[1]
        )
        ∆Θ = atand(cross_product, dot_product)

        Θ[i] = Θ[i-1] + ∆Θ
        start_axis2 = current_axis2
    end

    return Θ

end


# %%
function get_pelvis_rotation(pitch::Pitch)::DataFrame
    right_hip_id = get_joint_id("hip", "right")
    left_hip_id = get_joint_id("hip", "left")
    right_hip_data = get_joint_data(pitch, right_hip_id)
    left_hip_data = get_joint_data(pitch, left_hip_id)

    ∆t = get_framerate(pitch)
    cutoff = 10
    order = 2
    right_hip_filtered = filter_data(
       right_hip_data, ∆t, cutoff, order)
    left_hip_filtered = filter_data(
        left_hip_data, ∆t, cutoff, order)

    Θ = get_segment_rotation(right_hip_filtered, left_hip_filtered, "z")
    
    return Θ
end


function get_shoulder_rotation(pitch::Pitch)::DataFrame
    right_shoulder_id = get_joint_id("hip", "right")
    left_shoulder_id = get_joint_id("hip", "left")
    right_shoulder_data = get_joint_data(pitch, right_shoulder_id)
    left_shoulder_data = get_joint_data(pitch, left_shoulder_id)

    ∆t = get_framerate(pitch)
    cutoff = 10
    order = 2
    right_shoulder_filtered = filter_data(
       right_shoulder_data, ∆t, cutoff, order)
    left_shoulder_filtered = filter_data(
        left_shoulder_data, ∆t, cutoff, order)

    Θ = get_segment_rotation(right_shoulder_filtered, left_shoulder_filtered, "z")
    
    return Θ
end


function get_hand_path(pitch::Pitch, side::String)::DataFrame
    shoulder_id = get_joint_id("shoulder", side)
    wrist_id = get_joint_id("wrist", side)
    shoulder_data = get_joint_data(pitch, shoulder_id)
    wrist_data = get_joint_data(pitch, wrist_id)

    ∆t = get_framerate(pitch)
    cutoff = 15
    order = 4
    shoulder_data_filtered = filter_data(
       shoulder_data, ∆t, cutoff, order)
    wrist_data_filtered = filter_data(
        wrist_data, ∆t, cutoff, order)

    num_frames = size(shoulder_data_filtered)[1]

    hand_path = shoulder_data_filtered - wrist_data_filtered
    Θ = zeros(num_frames)

    for i ∈ 2:num_frames
        path_prev = hand_path[i-1, 1:2]
        path_current = hand_path[i, 1:2]

        if norm(path_prev) > 0.1 && norm(path_current) > 0.1
            path_prev = path_prev / norm(path_prev)
            path_current = path_current / norm(path_current)

            dot_product = dot(path_prev, path_current)
            cross_product = (
                path_prev[1] * path_current[2] - path_prev[2] * path_current[1]
            )
            ∆Θ = atand(cross_product, dot_product)

            Θ[i] = Θ[i - 1] + ∆Θ
        else
            Θ[i] = Θ[i - 1]
        end
    end

    return Θ

end

# %%
function gradient(data::Matrix{Float64}; spaceing=1.0)::Matrix{Float64}
    n, m = size(data)
    output = similar(data)

    for i ∈ 1:m

        for j ∈ 2:n-1 # interior diff
            output[i,j] = (data[i+1,j] - data[i-1, j]) / (2 * spacing)
        end 
        # forwrad/back diff
        output[1, j] = (data[2, j] - data[1, j]) / spacing
        output[n, j] = (data[n, j] - data[n-1, j]) / spacing
    end

    return output
end

# %%
function get_metrics(player::Player)
    arm = get_throwing_hand(player)
    if arm == "right"
        leg = "left"
    elseif arm == "left"
        leg = "right"
    end

    println("Calculating metrics for ", player.name, "...\n")

    num_pitches = length(player.pitches)
    num_frames = size(player.pitches[1].∆t)[1]
    Θ_hold = zeros(num_frames, 6)
    ω_hold = zeros(num_frames, 6)

    for i ∈ 1:num_pitches
        pitch = player.pitches[i]
        ∆t = get_framerate(pitch)

        Θ_metrics = Dict(
            "knee" => get_knee_angle(pitch, leg),
            "elbow" => get_elbow_angle(pitch, arm),
            "shoulder" => get_shoulder_rotation(pitch, arm),
            "pelvis" => get_pelvis_rotation(pitch),
            "trunk" => get_trunk_rotation(pitch),
            "hand" => get_hand_path(pitch, arm)
        )
        ω_metrics = Dict(
            "knee" => gradient(Θ_metrics["knee"], ∆t),
            "elbow" => gradient(Θ_metrics["elbow"], ∆t),
            "shoulder" => gradient(Θ_metrics["shoulder"], ∆t),
            "pelvis" => gradient(Θ_metrics["pelvis"], ∆t),
            "trunk" => gradient(Θ_metrics["trunk"], ∆t),
            "hand" => gradient(Θ_metrics["hand"], ∆t)
        )

        if size(Θ_metrics)[1] != size(Θ_hold)[1]
            diff = size(Θ_metrics)[1] - size(Θ_hold)[1]
            println("Frames mismatch: removing ", diff, 
                    " frames from ", player.name, 
                    " pitch ", i + 1, "\n")
            Θ_metrics = Θ_metrics[2:end]
            ω_metrics = ω_metrics[2:end]
        end

        Θ_hold = (Θ_hold + Θ_metrics) / 2
        ω_hold = (ω_hold + ω_metrics) / 2
        Θ_metrics = DataFrame(Θ_metrics, :auto)
        ω_metrics = DataFrame(ω_metrics, :auto)
        pitch.metrics = [Θ_metrics, ω_metrics]

    end


    player.metrics = [Θ_hold, ω_hold]

end

# %%
function main()
    player1 = get_data("../player1")
    player2 = get_data("../player2")

    get_metrics(player1)
    get_metrics(player2)
end

main()
