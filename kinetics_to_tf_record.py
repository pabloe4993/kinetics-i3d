import cv2
import numpy as np
import imageio
import tensorflow as tf

def image_resize(image, width = None, height = None, inter = cv2.INTER_LINEAR):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def crop_center_image(image, rec_len):
    # crop center
    (h, w) = image.shape[:2]
    x_1 = (w - rec_len) // 2
    x_2 = (h - rec_len) // 2
    cropped = image[x_2:x_2+rec_len, x_1:x_1+rec_len]
    return cropped



def video_to_image_and_of(video_path, target_fps=25, resize_height=256, crop_size=224, n_steps=100,plotting=False,flow=False):
# preprocessing:

    # video_path = '/media/ROIPO/Data/projects/Adversarial/database/video/v_LongJump_g03_c06.avi'
    #video_path = '/home/ADAMGE/Downloads/test_jog.mp4'
    # target_fps = 25.0
    # n_steps = 100
    # resize_height = 256
    # crop_size = 224


    clip_frames = []
    clip_frames_flow = []
    bit = 0
    capture = cv2.VideoCapture(video_path)
    fps = capture.get(cv2.CAP_PROP_FPS)

    frame_gap = int(round(fps / target_fps))
    if frame_gap == 0:
        raise ValueError
    frame_num = 0

    ret, frame1 = capture.read()
    resized_frame1 = image_resize(frame1, height = resize_height)
    prvs = cv2.cvtColor(resized_frame1,cv2.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame1)
    hsv[...,1] = 255

    # extract features
    while (capture.isOpened()) & (bit == 0):
        flag, frame = capture.read()
        if flag == 0:
            bit = 1
            print("******ERROR: Could not read frame in " + video_path + " frame_num: " + str(frame_num))
            break

        #name = params['res_vids_path'] + str(frame_num) + 'frame.jpg'
        #cv2.imwrite(name, frame)
        #cv2.imshow("Vid", frame)
        #key_pressed = cv2.waitKey(10)  # Escape to exit

        # process frame (according to the correct frame rate)
        if frame_num % frame_gap == 0:
            # RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if image.shape[0] < image.shape[1]:
                resized_frame = image_resize(image, height=resize_height)
            else:
                resized_frame = image_resize(image, width=resize_height)


            res = resized_frame.astype('float32') / 128. - 1
            res = crop_center_image(res, crop_size)
            clip_frames.append(res)

            if plotting:
                res_to_plot = cv2.cvtColor(res, cv2.COLOR_RGB2BGR)
                res_to_plot = res_to_plot + 1.0 / 2.0
                cv2.imshow("Vid", res_to_plot)
                key_pressed = cv2.waitKey(10)  # Escape to exit

            # FLOW
            if flow:
                image_flow = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2GRAY)
                # flow = cv2.calcOpticalFlowFarneback(prvs,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                optical_flow = cv2.DualTVL1OpticalFlow_create()
                flow = optical_flow.calc(prvs, image_flow, None)
                flow[flow > 20] = 20
                flow[flow < -20] = -20
                flow = flow / 20.
                flow = crop_center_image(flow, crop_size)
                clip_frames_flow.append(flow)

                # potting:
                if plotting:
                    flow_temp = (flow + 1.0) / 2.0
                    last_channel = np.zeros((crop_size,crop_size), dtype=float) + 0.5
                    flow_to_plot = np.dstack((flow_temp, last_channel))
                    cv2.imshow("Vid-flow", flow_to_plot)
                    key_pressed = cv2.waitKey(10)  # Escape to exit


            #mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            #hsv[..., 0] = ang * 180 / np.pi / 2
            #hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
            #bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            #cv2.imshow('frame2', bgr)
            #k = cv2.waitKey(30) & 0xff

                prvs = image_flow
            frame_num += 1



    capture.release()


     # (int(round(frame_num / frame_gap)) < n_steps)
    if frame_num>=n_steps:
        frames = np.array(clip_frames)[-n_steps:]
        frames_flow = np.array(clip_frames_flow)
        frames = np.expand_dims(frames, axis=0)
        frames_flow = np.expand_dims(frames_flow, axis=0)
    else:

        frames = np.array(clip_frames)
        frames = np.pad(frames, ((0, n_steps-frames.shape[0]),(0,0),(0,0),(0,0)),'wrap')
        frames_flow = np.array(clip_frames_flow)
        frames = np.expand_dims(frames, axis=0)
        frames_flow = np.expand_dims(frames_flow, axis=0)



    return frames, frames_flow


def frames_to_gif(frames, output_path, fps=25):
    imageio.mimsave(output_path, frames, fps=fps)

# np.save('rgb.npy', frames)
# np.save('flow.npy', frames_flow)

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))
def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))
def _float_list_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def parse_example(serialized):
    context_features = {'train/label' : tf.FixedLenFeature((), tf.int64),
                        'train/video' : tf.VarLenFeature(dtype=tf.float32)}
    # context_features = {'train/label' : tf.FixedLenFeature((), tf.int64),
    #                     'train/video' : tf.FixedLenFeature((), tf.string)}

    context_parsed,_ = tf.parse_single_sequence_example(serialized=serialized,context_features =context_features,sequence_features={})

    # video =  tf.image.decode_jpeg(context_parsed['train/video'], channels=3)
    video =  tf.reshape(tf.sparse.to_dense(context_parsed['train/video']), shape=[-1,224,224,3])
    label = context_parsed['train/label']

    return video, label

def main(unused_argv):
    from os import listdir

    # f, of, = video_to_image_and_of('/home/ROIPO/Downloads/y2mate.com - utsa_track_devon_bond_triple_jump_67R1t4-b1nw_360p.mp4',n_steps=90)

    video_base_path = '/media/ROIPO/Data/projects/Adversarial/kinetics-downloader/dataset/train/juggling_balls/'#'/media/ROIPO/Data/projects/Adversarial/kinetics-downloader/dataset/train/triple_jump/'
    video_list_path = listdir(video_base_path)
    label_map_path='/media/ROIPO/Data/projects/Adversarial/kinetics-i3d/data/label_map.txt'

    # class_target = ['triple jump']
    class_target = ['juggling balls']
    n_frames = 250

    kinetics_classes = [x.strip() for x in open(label_map_path)]

    #
    # video_list = [x.strip() for x in open(vl)]
    k=0

    for i, v in enumerate(video_list_path):
        if i%10 ==0:
            if i>0:
                writer.close()
                k+=1
            train_filename = 'data/kinetics_{}_{}_{:03}.tfrecords'.format(class_target[0].replace(' ','_'), video_base_path.split('/')[
                -3],k)  # address to save the TFRecords file
            # open the TFRecords file
            writer = tf.python_io.TFRecordWriter(train_filename)

        cls = class_target[0]
        cls_id = kinetics_classes.index(cls)
        vid_path = video_base_path + v
        try:
            frames, flow_frames = video_to_image_and_of(video_path=vid_path, n_steps=n_frames)
        except ValueError:
            continue
        if frames.shape[1] < n_frames-1:
            continue
        feature = {'train/label': _int64_feature(cls_id),
                   'train/video': _float_list_feature(frames.reshape([-1]))}
        example = tf.train.Example(features=tf.train.Features(feature=feature))
        writer.write(example.SerializeToString())



        # video_path= ['/media/ROIPO/Data/projects/Adversarial/database/UCF-101/video/v_BreastStroke_g01_c01.avi',
        # '/media/ROIPO/Data/projects/Adversarial/database/UCF-101/video/v_BreastStroke_g01_c02.avi']
        #



    # for i, vp in enumerate(video_path):
    #     frames, flow_frames = video_to_image_and_of(video_path=vp,n_steps=80)
    #     feature = {'train/label': _int64_feature(1),
    #                'train/video': _float_list_feature(frames.reshape([-1]))}
    #     example = tf.train.Example(features=tf.train.Features(feature=feature))
    #     writer.write(example.SerializeToString())
    

    # sys.stdout.flush()
    
    #     frames_list.append(frames)
    # np.save('data/db.npy', frames_list)

if __name__ == '__main__':
  tf.app.run(main)