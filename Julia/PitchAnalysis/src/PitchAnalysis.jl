module PitchAnalysis

# %%
using JSON
using DataFrames
using LinearAlgebra
using DSP
using Infiltrator
using Debugger

export get_data, get_metrics, get_joint_ids, get_framerate,
    get_hand_path, get_joint_data, get_knee_angle, get_elbow_angle,
    get_joint_angle, get_joint_group, get_throwing_hand, get_pelvis_rotation,
    get_segment_rotation, get_shoulder_rotation

# %%
@kwdef mutable struct Pitch
    positions::Vector{DataFrame}
    ∆t::Vector{String}
    # metrics::Vector{DataFrame}
    metrics
end

@kwdef mutable struct Player
    name::String
    pitches::Vector{Pitch}
    # metrics::Vector{DataFrame}
    metrics
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

# %%
# Vector input
function get_joint_ids(joint, side)
    if typeof(joint) == String
        joint = [joint]
    end

    joint_lookup = Dict(
        "nose" => 0,
        "neck" => 1,
        "eye_right" => 15,
        "eye_left" => 16,
        "shoulder_right" => 2,
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

            push!(joint_id, joint_lookup[this_joint] + 1)

        catch
            println("Joint ", joint[i], " and side ", side, " combination not found.")
        end

    end

    return joint_id

end


# %%
function get_joint_data(pitch::Pitch, joint)
    joint_data = Matrix(pitch.positions[joint])
    return joint_data

end


function get_throwing_hand(player)
    right_id = get_joint_ids("wrist", "right")
    left_id = get_joint_ids("wrist", "left")

    # right_data = get_joint_data(player.pitches[1], right_id)
    # left_data = get_joint_data(player.pitches[1], left_id)
    right_data = Matrix(player.pitches[1].positions[right_id][1])
    left_data = Matrix(player.pitches[1].positions[left_id][1])
    # @infiltrate
    if right_data[1, 2] > left_data[1, 2]
        side = "right"
    elseif right_data[1, 2] < left_data[1, 2]
        side = "left"
    end

    return side

end

function get_joint_group(joint)
    extra = ""

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


function get_framerate(pitch::Pitch)
    first = parse(Float64, pitch.∆t[1][18:end-1])
    last = parse(Float64, pitch.∆t[end][18:end-1])

    if (last - first) < 0
        last = 60 + last
    end

    framerate = (last - first) / length(pitch.∆t)

    return framerate

end


function get_joint_angle(
    proximal_data,
    joint_data,
    distal_data,
    extra_data=nothing)

    num_frames = size(joint_data)[1]

    distal_segment = Matrix(joint_data) - Matrix(distal_data)

    if extra_data != nothing && size(extra_data)[1] == size(joint_data)[1]
        intermediate_segment = Matrix(joint_data) - Matrix(proximal_data)
        extra_segment = Matrix(extra_data) - Matrix(proximal_data)
        # proximal_segment = [cross(extra_segment[i, :], intermediate_segment[i, :]) for i ∈ 1:num_frames]
        proximal_segment = similar(distal_segment)
        for i in 1:num_frames
            proximal_segment[i, :] = cross(extra_segment[i, :], intermediate_segment[i, :])
        end
    else
        proximal_segment = Matrix(proximal_data) - Matrix(joint_data)
    end

    Θ = zeros(num_frames)
    # @infiltrate
    for i ∈ 1:num_frames
        proximal_vector = proximal_segment[i, :]
        distal_vector = distal_segment[i, :]
        # @warn size(proximal_vector)
        # @warn size(distal_vector)

        Θ[i] = atand(
            norm(cross(proximal_vector, distal_vector)),
            dot(proximal_vector, distal_vector)
        )

    end

    return Θ

end


# %%
function filter_data(data, ∆t, cutoff, order)
    nyquist_freq = 1 / (∆t * 2)
    filter = digitalfilter(Lowpass(cutoff / nyquist_freq), Butterworth(order))
    filtered_data = filtfilt(filter, Matrix{Float64}(data))

    return filtered_data

end


function get_elbow_angle(pitch::Pitch, side)
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


function get_knee_angle(pitch::Pitch, side)
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


function get_shoulder_rotation(pitch::Pitch, side)
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
    point1_data, point2_data, rotation_axis)
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

    # start_axis1 = abs(point1_data[1, :] - point2_data[1, :])
    start_axis1 = point1_data[1, :] - point2_data[1, :]
    start_axis2 = cross(rotation_axis, start_axis1)
    start_axis2 = start_axis2 / norm(start_axis2)

    for i ∈ 2:num_frames
        # axis1 = abs(point1_data[i, :] - point2_data[i, :])
        axis1 = point1_data[1, :] - point2_data[1, :]
        axis2 = cross(rotation_axis, axis1)
        current_axis2 = axis2 / norm(axis2)

        dot_product = dot(start_axis2[1], current_axis2[1])
        cross_product = (
            start_axis2[1] * current_axis2[2] - start_axis2[2] * current_axis2[1]
        )
        ∆Θ = atand(cross_product, dot_product)

        Θ[i] = Θ[i-1] + ∆Θ
        start_axis2 = current_axis2
    end

    return Θ

end


# %%
function get_pelvis_rotation(pitch::Pitch)
    right_hip_id = get_joint_ids("hip", "right")[1]
    left_hip_id = get_joint_ids("hip", "left")[1]
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


function get_trunk_rotation(pitch::Pitch)
    right_shoulder_id = get_joint_ids("shoulder", "right")[1]
    left_shoulder_id = get_joint_ids("shoulder", "left")[1]
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


function get_hand_path(pitch::Pitch, side)
    shoulder_id = get_joint_ids("shoulder", side)[1]
    wrist_id = get_joint_ids("wrist", side)[1]
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

            Θ[i] = Θ[i-1] + ∆Θ
        else
            Θ[i] = Θ[i-1]
        end
    end

    return Θ

end

# %%
function gradient(data, spacing)
    n = size(data)[1]
    output = similar(data)


    # Interior points (central differences)
    for i in 2:n-1
        output[i] = (data[i+1] - data[i-1]) / (2 * spacing)
    end

    # Boundaries (forward/backward differences)
    output[1] = (data[2] - data[1]) / spacing
    output[n] = (data[n] - data[n-1]) / spacing

    return output
end

# %%
function get_metrics(player)
    arm = get_throwing_hand(player)
    if arm == "right"
        leg = "left"
    elseif arm == "left"
        leg = "right"
    end

    println("Calculating metrics for ", player.name, "...\n")

    num_pitches = length(player.pitches)
    num_frames = size(player.pitches[1].∆t, 1)
    num_metrics = 6
    Θ_hold = zeros(num_frames, num_metrics)
    ω_hold = zeros(num_frames, num_metrics)

    for i ∈ 1:num_pitches
        pitch = player.pitches[i]
        ∆t = get_framerate(pitch)

        Θ_metrics = hcat(
            get_knee_angle(pitch, leg),
            get_elbow_angle(pitch, arm),
            get_shoulder_rotation(pitch, arm),
            get_pelvis_rotation(pitch),
            get_trunk_rotation(pitch),
            get_hand_path(pitch, arm)
        )
        # ω_metrics = [gradient(Θ_metrics[:, j], ∆t) for j in 1:num_metrics]
        ω_metrics = similar(Θ_metrics)
        for j in 1:num_metrics
            ω_metrics[:, j] = gradient(Θ_metrics[:, j], ∆t)
        end
        # Θ_metrics = Dict(
        #     "knee" => get_knee_angle(pitch, leg),
        #     "elbow" => get_elbow_angle(pitch, arm),
        #     "shoulder" => get_shoulder_rotation(pitch, arm),
        #     "pelvis" => get_pelvis_rotation(pitch),
        #     "trunk" => get_trunk_rotation(pitch),
        #     "hand" => get_hand_path(pitch, arm)
        # )
        # ω_metrics = Dict(
        #     "knee" => gradient(Θ_metrics["knee"], ∆t),
        #     "elbow" => gradient(Θ_metrics["elbow"], ∆t),
        #     "shoulder" => gradient(Θ_metrics["shoulder"], ∆t),
        #     "pelvis" => gradient(Θ_metrics["pelvis"], ∆t),
        #     "trunk" => gradient(Θ_metrics["trunk"], ∆t),
        #     "hand" => gradient(Θ_metrics["hand"], ∆t)
        # )

        if size(Θ_metrics)[1] != size(Θ_hold)[1]
            diff = size(Θ_metrics)[1] - size(Θ_hold)[1]
            println("Frames mismatch: removing ", diff,
                " frames from ", player.name,
                " pitch ", i + 1, "\n")
            # @infiltrate
            Θ_metrics = Θ_metrics[1+diff:end, :]
            ω_metrics = ω_metrics[1+diff:end, :]
        end

        # @infiltrate
        Θ_hold = (Θ_hold + Θ_metrics) / 2
        ω_hold = (ω_hold + ω_metrics) / 2
        Θ_metrics = DataFrame(Θ_metrics, :auto)
        ω_metrics = DataFrame(ω_metrics, :auto)
        pitch.metrics = [Θ_metrics, ω_metrics]

    end


    player.metrics = [Θ_hold, ω_hold]
    return player
end


# %%
end # module PitchAnalysis
