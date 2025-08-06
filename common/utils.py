# Hàm chuyển đổi milliseconds thành chuỗi định dạng thời gian
def time_stamp(ms):
    hours, remainder = divmod(ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, _ = divmod(remainder, 1_000)
    return ("%d:%02d:%02d" % (hours, minutes, seconds)) if hours else ("%d:%02d" % (minutes, seconds))
