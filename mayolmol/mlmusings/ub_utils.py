""" Some convinience methods for working with ubigraph """

##########################
# Colors
# Ubigraph colors are specified by either:
#   - An rgb string like "#ff00aa" (3 bytes)
#   - An integer (use the internal palette)
##########################

def linear_gradient(start, end, steps):
    return hex(r)[2:], hex(g)[2:], hex(b)[2:]

def rgb2ubigraph(r, g, b):
    return '#%s%s%s' % (hex(r)[2:], hex(g)[2:], hex(b)[2:])

def gradient():
    """ Create a color gradient.
    http://www.pygame.org/project/307/
    http://stackoverflow.com/questions/3503158/programatically-working-with-color-gradients
    http://jtauber.com/blog/2008/05/18/creating_gradients_programmatically_in_python/
    """
    pass

def linear_gradient(start_value, stop_value, start_offset=0.0, stop_offset=1.0):
    return lambda offset: (start_value + (
            (offset - start_offset) / (stop_offset - start_offset) * (stop_value - start_value))) / 255.0

def gradient(segments):
    def gradient_function(y):
        segment_start = 0.0
        for segment_end, start, end in segments:
            if y < segment_end:
                return (linear_gradient(start[i], end[i], segment_start, segment_end)(y) for i in xrange(len(start)))
            segment_start = segment_end

    return gradient_function
