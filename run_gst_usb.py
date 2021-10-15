#!/usr/bin/env python3


import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
from FPS import GETFPS
import numpy as np
import cv2
fps_streams={}

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True



def imageCallback(sink):
    
    
    sample = sink.emit('pull-sample')
    buf = sample.get_buffer()
    caps = sample.get_caps().get_structure(0)
    format  = caps.get_value('format')
    height = caps.get_value('height')
    width = caps.get_value('width')
    # print( 'imageCallback w:{} h:{} f:{}'.format(width,height,format) )
    
    image = np.ndarray((caps.get_value('height'),caps.get_value('width'),3), 
              buffer=buf.extract_dup(0,buf.get_size()),dtype=np.uint8)
    rgb = image[...,::-1].copy()          
    # cv2.imwrite('my_array.jpg',rgb)
    fps_streams[0].get_fps()
    return Gst.FlowReturn.OK
			
   
def main(args):
    # Check input arguments
    if len(args) != 2:
        sys.stderr.write("usage: %s <v4l2-device-path>\n" % args[0])
        sys.exit(1)
    fps_streams[0]=GETFPS(0)
    # Standard GStreamer initialization
    GObject.threads_init()
    Gst.init(None)

    # Create gstreamer elements
    # Create Pipeline element that will form a connection of other elements
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")

    # Source element for reading from the file
    print("Creating Source \n ")
    source = Gst.ElementFactory.make("v4l2src", "usb-cam-source")
    if not source:
        sys.stderr.write(" Unable to create Source \n")

    caps_v4l2src = Gst.ElementFactory.make("capsfilter", "v4l2src_caps")
    if not caps_v4l2src:
        sys.stderr.write(" Unable to create v4l2src capsfilter \n")


    print("Creating Video Converter \n")

    # videoconvert to make sure a superset of raw formats are supported
    vidconvsrc = Gst.ElementFactory.make("videoconvert", "convertor_src1")
    if not vidconvsrc:
        sys.stderr.write(" Unable to create videoconvert \n")
    tee = Gst.ElementFactory.make("tee", "tee-1")
    if not tee:
        sys.stderr.write(" Unable to create tee \n")
    queue1 = Gst.ElementFactory.make("queue","queue1")
    if not queue1:
        sys.stderr.write(" Unable to create queue1 \n")
    vidconvsrc2 = Gst.ElementFactory.make("videoconvert", "vidconvsrc2")
    if not vidconvsrc2:
        sys.stderr.write(" Unable to create vidconvsrc2 \n")
    rgb_caps = Gst.ElementFactory.make("capsfilter", "rgb_caps")
    if not rgb_caps:
        sys.stderr.write(" Unable to create rgb capsfilter \n")
    print("Creating EGLSink \n")

    rgb_sink = Gst.ElementFactory.make("appsink", "rgb-sink")
    if not rgb_sink:
        sys.stderr.write(" Unable to create rgb sink \n")
    rgb_sink.set_property("emit-signals", True)
    rgb_sink.connect("new-sample", imageCallback)


    queue2 = Gst.ElementFactory.make("queue","queue2")
    if not queue2:
        sys.stderr.write(" Unable to create queue2 \n")

    
    sink = Gst.ElementFactory.make("xvimagesink", "nvvideo-renderer")
    if not sink:
        sys.stderr.write(" Unable to create egl sink \n")

   

    print("Playing cam %s " %args[1])
    caps_v4l2src.set_property('caps', Gst.Caps.from_string("video/x-raw, framerate=30/1, width=640, height=480"))
    rgb_caps.set_property('caps', Gst.Caps.from_string("video/x-raw,format=RGB,framerate=30/1, width=640, height=480"))
    source.set_property('device', args[1])
   
    sink.set_property('sync', False)#synchronize( 0:as soon as better ,1:synchronize )。

    print("Adding elements to Pipeline \n")
    pipeline.add(source)
    pipeline.add(caps_v4l2src)
    pipeline.add(vidconvsrc)
    pipeline.add(tee)
    pipeline.add(queue1)
    pipeline.add(vidconvsrc2)
    pipeline.add(rgb_caps)
    pipeline.add(rgb_sink)
    pipeline.add(queue2)
    
    pipeline.add(sink)
    
    print("Linking elements in the Pipeline \n")
    source.link(caps_v4l2src)
    caps_v4l2src.link(vidconvsrc)
    vidconvsrc.link(tee)
    tee.link(queue1)
    tee.link(queue2) 

    queue1.link(vidconvsrc2)
    vidconvsrc2.link(rgb_caps)
    rgb_caps.link(rgb_sink)

   
    queue2.link(sink)

    # # create an event loop and feed gstreamer bus mesages to it
    loop = GObject.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)

    # # Lets add probe to get informed of the meta data generated, we add probe to
    # # the sink pad of the osd element, since by that time, the buffer would have
    # # had got all the metadata.
    

    

    # osdsinkpad = vidconvsrc.get_static_pad("sink")
    # if not osdsinkpad:
    #     sys.stderr.write(" Unable to get sink pad of nvosd \n")

    # osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)
    # start play back and listen to events
    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    # cleanup
    pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main(sys.argv))

