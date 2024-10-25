import vapoursynth as vs
import sys

# Originately writen by YomikoR
#https://gist.github.com/RyougiKukoc/2dc1bf4fc7e54515329abdb2ff16b976#file-dual_output_v2-py

# Outputting various size and format clips requires VS R61 and later
def multiple_outputs(clips, files):
    # Checks
    num_clips = len(clips)
    num_files = len(files)
    assert num_clips > 0 and num_clips == num_files
    for clip in clips:
        assert clip.format

    is_y4m = [clip.format.color_family in (vs.YUV, vs.GRAY) for clip in clips]

    for n in range(num_files):
        fileobj = files[n]
        if (fileobj is sys.stdout or fileobj is sys.stderr) and hasattr(fileobj, "buffer"):
            files[n] = fileobj.buffer

    # Interleave
    max_len = max(len(clip) for clip in clips)
    clips_aligned = []
    for n, clip in enumerate(clips):
        if len(clip) < max_len:
            clip_aligned = clip + vs.core.std.BlankClip(clip, length=max_len - len(clip))
        else:
            clip_aligned = clip
        clips_aligned.append(vs.core.std.Interleave([clip_aligned] * num_clips))    
    if vs.__version__.release_major > 60:
        clips_varfmt = vs.core.std.BlankClip(length=max_len * num_clips, varformat=True, varsize=True)
    else:
        clips_varfmt = vs.core.std.BlankClip(clips[0], length=max_len * num_clips)
    def _interleave(n, f):
        return clips_aligned[n % num_clips]
    interleaved = vs.core.std.FrameEval(clips_varfmt, _interleave, clips_aligned, clips)

    # Y4M header
    for n in range(num_clips):
        if is_y4m[n]:
            clip = clips[n]
            fileobj = files[n]
            if clip.format.color_family == vs.GRAY:
                y4mformat = 'mono'
                if clip.format.bits_per_sample > 8:
                    y4mformat = y4mformat + str(clip.format.bits_per_sample)
            else: # YUV
                if clip.format.subsampling_w == 1 and clip.format.subsampling_h == 1:
                    y4mformat = '420'
                elif clip.format.subsampling_w == 1 and clip.format.subsampling_h == 0:
                    y4mformat = '422'
                elif clip.format.subsampling_w == 0 and clip.format.subsampling_h == 0:
                    y4mformat = '444'
                elif clip.format.subsampling_w == 2 and clip.format.subsampling_h == 2:
                    y4mformat = '410'
                elif clip.format.subsampling_w == 2 and clip.format.subsampling_h == 0:
                    y4mformat = '411'
                elif clip.format.subsampling_w == 0 and clip.format.subsampling_h == 1:
                    y4mformat = '440'
                if clip.format.bits_per_sample > 8:
                    y4mformat = y4mformat + 'p' + str(clip.format.bits_per_sample)

            y4mformat = 'C' + y4mformat + ' '

            data = 'YUV4MPEG2 {y4mformat}W{width} H{height} F{fps_num}:{fps_den} Ip A0:0 XLENGTH={length}\n'.format(
                y4mformat=y4mformat,
                width=clip.width,
                height=clip.height,
                fps_num=clip.fps_num,
                fps_den=clip.fps_den,
                length=len(clip)
            )
            fileobj.write(data.encode("ascii"))

    # Output#
    for idx, frame in enumerate(interleaved.frames(close=False)):
        clip_idx = idx % num_clips
        clip = clips[clip_idx]
        fileobj = files[clip_idx]
        finished = idx // num_clips
        if finished < len(clip):
            if is_y4m[clip_idx]:
                fileobj.write(b"FRAME\n")
            for planeno, plane in enumerate(frame):
                if frame.get_stride(planeno) != plane.shape[1] * clip.format.bytes_per_sample:
                    fileobj.write(bytes(plane))
                else:
                    fileobj.write(plane)
            if hasattr(fileobj, "flush"):
                fileobj.flush()

