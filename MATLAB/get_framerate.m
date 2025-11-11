function framerate = get_framerate(pitch)

first = str2double(pitch(1).timeStamp{1}(end-9:end-1));
last = str2double(pitch(end).timeStamp{1}(end-9:end-1));

if (last-first) < 0
    last = 60 + last;
end

framerate = (last - first) / length(pitch);

% If minute ticks over
% if framerate < 0
%     last = 60 + last;
%     framerate = (last - first) / length(pitch);
% 
% end