# %%
using(JSON)
using DataFrames

# %%
@kwdef mutable struct Pitch
    positions :: Vector{DataFrame}
    ∆t :: Vector{String} 
    metrics
end

@kwdef mutable struct Player
    name :: String
    pitches :: Vector{Pitch}
    metrics 
end    

# %%
function get_data(directory)
    name = directory[4:end]
    println("Gathering data for ", name, "...\n")

    files = readdir(directory)
    files = files[occursin.(".json", files)]
    num_files = length(files)
    pitches = Pitch[]

    for i ∈ 1:num_files 
        path = directory * "/" * files[i]
        data = JSON.parsefile(path)

        num_frames = length(data.skeletalData.frames)
        # time_stamps = String[]
        time_stamps = [data.skeletalData.frames[j].timeStamp for j ∈ 1:num_frames]
        positions = DataFrame[]
        num_joints = length(data.skeletalData.frames[1].positions[1].joints)
        
        # for j ∈ 1:num_frames
        #     # push!(time_stamps, data.skeletalData.frames[j].timeStamp)
        #
        #     hold = DataFrame(x=Float64[], y=Float64[], z=Float64[])
        #     
        #     for k ∈ 1:num_joints
        #         x = data.skeletalData.frames[j].positions[1].joints[k]["x"]
        #         y = data.skeletalData.frames[j].positions[1].joints[k]["y"]
        #         z = data.skeletalData.frames[j].positions[1].joints[k]["z"]
        #         push!(hold, [x y z])
        #
        #     end
        #
        #     push!(positions, hold)
        # end

        for j ∈ 1:num_frames
            # hold = DataFrame(x=Float64[], y=Float64[], z=Float64[])
            hold = [data.skeletalData.frames[j].positions[1].joints[k]["x"]
                            data.skeletalData.frames[j].positions[1].joints[k]["y"]
                            data.skeletalData.frames[j].positions[1].joints[k]["z"]
                            for k ∈ 1:num_joints]
            push!(positions, hold)
        end


        pitch = Pitch(positions=positions, ∆t=time_stamps, metrics=[])
        pitches = push!(pitches, pitch)

    end

    player = Player(name=name, pitches=pitches, metrics=[])

    return player

end
