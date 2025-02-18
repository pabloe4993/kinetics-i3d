# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Loads a sample video and classifies using a trained Kinetics checkpoint."""
#%%
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import numpy as np
# import setGPU
import matplotlib
# matplotlib.use('Qt5Agg')
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import imageio
import pickle
from collections import namedtuple

# import rgb_lab_conv.rgb_lab_formulation as lab_tool

#
# import foolbox_2.foolbox as fb_2
# import i3d
# import skvideo
import pre_process_rgb_flow as img_tool


_IMAGE_SIZE = 224
_BATCH_SIZE = 1

_SAMPLE_VIDEO_FRAMES =90 # 79 #90 #90 #250 #90 #79
_BASE_PATCH_FRAMES = 90 #_SAMPLE_VIDEO_FRAMES #_SAMPLE_VIDEO_FRAMES # 1# _SAMPLE_VIDEO_FRAMES # 1:for sticker _SAMPLE_VIDEO_FRAMES # 1
_IND_START = 0  # 0 #50
_IND_END =_SAMPLE_VIDEO_FRAMES




# res_dict['correct_cls_prob']
# res_dict['correct_cls']
# res_dict['correct_cls_id']
# res_dict['video_name']
# res_dict['softmax_init']
# res_dict['rgb_sample']
#
# res_dict['total_loss_l']
# res_dict['adv_loss_l']
# res_dict['reg_loss_l']
# res_dict['norm_reg_loss_l']
# res_dict['diff_norm_reg_loss_l']
# res_dict['perturbation']
# res_dict['adv_video']
# res_dict['softmax']
# res_dict['total_steps']
# res_dict['beta_1']
# res_dict['beta_2']

results_path ='/home/ROIPO/DL_server/data/DL/Adversarial/kinetics-i3d/result/videos_for_tests/npy/'#'/data/DL/Adversarial/kinetics-i3d/result/videos_for_tests/npy/'
stats=[]

fig_3, ax = plt.subplots()
for res in os.listdir(results_path):


    with open(os.path.join(results_path,res), 'rb') as handle:
        tmp_dict = pickle.load(handle)

        tmp_dict['softmax'] =np.concatenate(tmp_dict['softmax'],axis=0)
        tmp_dict['perturbation'] = np.stack(tmp_dict['perturbation']).squeeze()
        tmp_struct = namedtuple("dict", tmp_dict.keys())(*tmp_dict.values())

        stats.append(tmp_struct)

        t = np.arange(0.01, 10.0, 0.01)
        data1 = np.exp(t)
        data2 = np.sin(2 * np.pi * t)

        fig, ax1 = plt.subplots()

        color = 'tab:red'
        ax1.plot(tmp_struct.softmax[:, tmp_struct.correct_cls_id], color=color)
        color = 'tab:green'
        ax1.plot(np.max(tmp_struct.softmax, axis=-1), color=color)

        ax1.set_xlabel('iter (#)')
        ax1.set_ylabel('probability', color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        color = 'tab:blue'
        ax2.set_ylabel('MAP (%)', color=color)  # we already handled the x-label with ax1
        mean_avg_perturbation = np.mean(np.mean(tmp_struct.perturbation.__abs__(), axis=-1), axis=-1)
        mean_diff_avg_perturbation= np.mean(np.mean((np.roll(tmp_struct.perturbation,1,axis=1) -tmp_struct.perturbation).__abs__(), axis=-1), axis=-1)
        mean_diff_avg_perturbation = mean_diff_avg_perturbation/2.0*100
        ax2.plot(mean_avg_perturbation, color='tab:orange')
        mean_avg_perturbation= mean_avg_perturbation/2.0 *100
        ax2.plot(mean_avg_perturbation, color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        sort_ind_MAP = np.argsort(mean_avg_perturbation)
        ax.plot(mean_avg_perturbation[sort_ind_MAP], tmp_struct.softmax[:, tmp_struct.correct_cls_id][sort_ind_MAP])
        is_adversarial_idx = np.where(
            tmp_struct.softmax[:, tmp_struct.correct_cls_id][sort_ind_MAP] != np.max(tmp_struct.softmax, axis=-1)[
                sort_ind_MAP])
        ax.scatter(mean_avg_perturbation[is_adversarial_idx],
                   tmp_struct.softmax[:, tmp_struct.correct_cls_id][is_adversarial_idx], color='red')
        ax.set_xlabel('MAP (%)', color=color)
        ax.set_ylabel('probability', color=color)

        # fig.tight_layout()  # otherwise the right y-label is slightly clipped
        # plt.show()
        fig.savefig('/home/ROIPO/Downloads/' + tmp_struct.video_name.split('.')[0] + '.png')

fig_3.savefig('/home/ROIPO/Downloads/' + 'prob_as_function_fat.png')


a=1
# if np.random.rand() > 0.9:
#     plt.clf()
#     plt.subplot(2,1,2)
#     plt.plot(total_loss_l,'r')
#     plt.plot(adv_loss_l,'b')
#     plt.plot(reg_loss_l,'g')
#     plt.plot(norm_reg_loss_l,'k')
#     plt.plot(diff_norm_reg_loss_l,'m')
#
#     plt.subplot(2,1,1)
#     plt.plot(reg_loss_l,'g')
#     plt.plot(norm_reg_loss_l,'k')
#     plt.plot(diff_norm_reg_loss_l,'m')
#     plt.grid(True)
#
#     plt.show()
#     plt.pause(0.1)


_SAMPLE_PATHS = {
    'rgb': 'data/v_CricketShot_g04_c01_rgb.npy',
    'flow': 'data/v_CricketShot_g04_c01_flow.npy',
}

_CHECKPOINT_PATHS = {
    'rgb': 'data/checkpoints/rgb_scratch/model.ckpt',
    'rgb600': 'data/checkpoints/rgb_scratch_kin600/model.ckpt',
    'flow': 'data/checkpoints/flow_scratch/model.ckpt',
    'rgb_imagenet': 'data/checkpoints/rgb_imagenet/model.ckpt',
    'flow_imagenet': 'data/checkpoints/flow_imagenet/model.ckpt',
    'rgb_ucf_101': 'data/checkpoints/rgb_ucf_101/ucf101_rgb_0.946_model-44520.ckpt'
}

_LABEL_MAP_PATH = 'data/label_map.txt'
_LABEL_MAP_PATH_600 = 'data/label_map_600.txt'
_LABEL_MAP_PATH_UCF_101 = 'data/label_map_ucf_101.txt'

FLAGS = tf.flags.FLAGS

tf.flags.DEFINE_string('eval_type', 'rgb', 'rgb, rgb600, ,  flow, or joint')
tf.flags.DEFINE_boolean('imagenet_pretrained', True, '')

# test_list_path  = '/media/ROIPO/Data/projects/Adversarial/database/UCF-101/ucfTrainTestlist/testlist01.txt'

def get_video_sample(vid_list, random=True, id=0 ):
      base_path = '/media/ROIPO/Data/projects/Adversarial/database/UCF-101/video/'

      if random:
        id = np.random.choice(a=vid_list.__len__(), size=1)[0]
      cls, vid_name = vid_list[id].split('/')
      frames, flow_frames = img_tool.video_to_image_and_of(video_path=base_path+vid_name,n_steps=80)
      return frames, flow_frames, cls


def load_i3d_model(num_classes,eval_type='rgb', scope='RGB',spatial_squeeze=True, final_endpoint='Logits'):
    with tf.variable_scope(scope):
        i3d_model = i3d.InceptionI3d(
          num_classes, spatial_squeeze=spatial_squeeze, final_endpoint=final_endpoint)

    dummy_input = tf.placeholder(
        tf.float32,
        shape=(None, _SAMPLE_VIDEO_FRAMES, _IMAGE_SIZE, _IMAGE_SIZE, 3))
    i3d_model(dummy_input, is_training=False, dropout_keep_prob=1.0)


    return i3d_model

def init_model(model,sess, ckpt_path, eval_type='rgb'):
    rgb_variable_map = {}

    for variable in model.get_all_variables():

      if variable.name.split('/')[0] == 'RGB':
        if eval_type == 'rgb600':
          rgb_variable_map[variable.name.replace(':0', '')[len('RGB/inception_i3d/'):]] = variable
        else:
          rgb_variable_map[variable.name.replace(':0', '')] = variable

    for variable in model.graph.get_collection_ref('moving_average_variables'):

      if variable.name.split('/')[0] == 'RGB':
        if eval_type == 'rgb600':
          rgb_variable_map[variable.name.replace(':0', '')[len('RGB/inception_i3d/'):]] = variable
        else:
          rgb_variable_map[variable.name.replace(':0', '')] = variable

    saver = tf.train.Saver(var_list=rgb_variable_map, reshape=True)

    saver.restore(sess,ckpt_path)

def load_kinetics_classes(eval_type):
    if eval_type == 'rgb600':
        kinetics_classes = [x.strip() for x in open(_LABEL_MAP_PATH_600)]
    else:
        kinetics_classes = [x.strip() for x in open(_LABEL_MAP_PATH)]

    return kinetics_classes

def cx_loss(inputs,adversarial_inputs):
    vgg_real = build_vgg19(tf.squeeze(inputs))
    vgg_input = build_vgg19(tf.squeeze(adversarial_inputs))

    if config.W.CX > 0:
        CX_loss_list = [w * CX_loss_helper(vgg_real[layer], vgg_input[layer], config.CX)
                        for layer, w in config.CX.feat_layers.items()]
        CX_style_loss = tf.reduce_sum(CX_loss_list)
        CX_style_loss *= config.W.CX
    else:
        CX_style_loss = zero_tensor

    return CX_style_loss


logdir ='logs/'
# from tensorflow.contrib.slim.nets import vgg
#
# images = tf.placeholder(tf.float32, shape=(1, 224, 224, 3))
# preprocessed = images - [123.68, 116.78, 103.94]
# logits, _ = vgg.vgg_19(preprocessed, is_training=False)
# restorer = tf.train.Saver(tf.trainable_variables())
#
# image, label = fb_2.utils.imagenet_example()
# eps_rgb = tf.Variable(tf.zeros(shape=[1, 224, 224, 3], dtype=tf.float32),name='eps')
# adversarial_inputs_rgb = preprocessed +  eps_rgb
#
# with tf.Session() as session:
#   restorer.restore(session, 'vgg_19.ckpt')
#   model = fb_2.models.TensorFlowModelCX(inputs=images,adversarial_inputs=adversarial_inputs_rgb,
#   perturbation=eps_rgb,logits=logits,mask=None,bounds=(0, 255), session=session)
#   print(np.argmax(model.forward_one(image)))
#   criteria = fb_2.criteria.Misclassification()

  # target_class = kinetics_classes.index('javelin throw')
  # criteria = fb_2.criteria.TargetClass(target_class=target_class)
  # criteria = fb_2.criteria.TargetClassProbability(target_class=target_class, p=0.85)
  #
  # target_class = label
  #
  # # target_class =30
  # # criteria = fb_2.criteria.TargetClass(target_class=target_class)
  #
  # # attack = fb_2.attacks.FGSM(model=rgb_adv_model, criterion=criteria)
  #
  # attack = fb_2.attacks.MultiStepGradientBaseAttack(model=model, criterion=criteria)
  # rgb_adversarial = attack(image.squeeze(), label=target_class, unpack=False)

tf.logging.set_verbosity(tf.logging.INFO)
eval_type = FLAGS.eval_type

imagenet_pretrained = FLAGS.imagenet_pretrained

NUM_CLASSES = 400
if eval_type == 'rgb600':
        NUM_CLASSES = 600

scope ='RGB'
kinetics_classes = load_kinetics_classes(eval_type)

if eval_type in ['rgb', 'rgb600', 'joint']:
  if imagenet_pretrained:
    ckpt_path = _CHECKPOINT_PATHS['rgb_imagenet']
  else:
    ckpt_path = _CHECKPOINT_PATHS[eval_type]


# ucf_video_list = [x.strip() for x in open(test_list_path)]


gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)


sess = tf.Session()
with tf.variable_scope(scope):

    # rgb_sample = np.load('/data/DL/Adversarial/kinetics-i3d/data/npy_videos/san_diego_ca_jadel_gregorio_triple_jump_1532m_short_approach.npy')[0, -_SAMPLE_VIDEO_FRAMES:]
    # rgb_sample = np.load('/data/DL/Adversarial/kinetics-i3d/data/npy_videos/triple_jump_kinetics.npy')[ -_SAMPLE_VIDEO_FRAMES:]
    # rgb_sample = np.load('/data/DL/Adversarial/kinetics-i3d/data/npy_videos/v_CricketShot_g04_c01_rgb.npy')[0, -_SAMPLE_VIDEO_FRAMES:]

    # rgb_sample = np.load('/data/DL/Adversarial/kinetics-i3d/data/npy_videos/juggling_balls_wkVU4KyWS4k.npy')[0, -_SAMPLE_VIDEO_FRAMES:]
    rgb_sample = np.load('/data/DL/Adversarial/kinetics-i3d/data/npy_videos/7pxmupXYnuo.npy')[0,-_SAMPLE_VIDEO_FRAMES:]
    # rgb_sample = np.load('data/npy_videos/triple_jump_1_kinetics.npy')[0,-_SAMPLE_VIDEO_FRAMES:]
    rgb_sample = rgb_sample[np.newaxis]
    correct_cls = 'juggling balls' #'triple jump' #'playing cricket' #'triple jump' #'juggling balls' #'triple jump' 'playing cricket'
    target_class = correct_cls # 'javelin throw'
    target_class = kinetics_classes.index(target_class)
    # rgb_sample, flow_sample, correct_cls = get_video_sample(ucf_video_list)

    default_adv_flag = tf.constant(1.0,dtype=tf.float32)
    adv_flag = tf.placeholder_with_default(default_adv_flag,shape=default_adv_flag.shape)

    # RGB input has 3 channels.
    rgb_input = tf.placeholder(tf.float32,
        shape=(_BATCH_SIZE, _SAMPLE_VIDEO_FRAMES, _IMAGE_SIZE, _IMAGE_SIZE, 3))

    eps_rgb = tf.Variable(tf.zeros(shape=[_BASE_PATCH_FRAMES, 1, 1, 3], dtype=tf.float32),name='eps')
    # extend_eps_rgb = tf.tile(eps_rgb, [9, 1, 1, 1])

    extend_eps_rgb = eps_rgb


    mask = tf.ones(shape=[_SAMPLE_VIDEO_FRAMES, _IMAGE_SIZE, _IMAGE_SIZE, 3])
    # mask = np.zeros(rgb_input.shape, dtype=np.float32)
    # mask[0,:,112,112,:]=1
    # mask = tf.constant(mask)

    #_SAMPLE_VIDEO_FRAMES# 50 #_SAMPLE_VIDEO_FRAMES # _SAMPLE_VIDEO_FRAMES
    # default_T = tf.constant(int(_IND_END - _IND_START + 1), dtype=tf.int32)
    # T = tf.placeholder_with_default(default_T,
    #                                 shape=default_T.shape)

    # indices = tf.cast(tf.linspace(float(_IND_START),float(_IND_END),T), tf.int32)

    indices = np.linspace(_IND_START,_IND_END,_IND_END-_IND_START+1)
    mask_indecator = tf.one_hot(indices =indices, depth=_SAMPLE_VIDEO_FRAMES)
    mask_indecator = tf.reduce_sum(mask_indecator, reduction_indices=0)
    mask_indecator = tf.reshape(mask_indecator, [_SAMPLE_VIDEO_FRAMES,1,1,1])
    mask_rgb = tf.convert_to_tensor(mask*mask_indecator,name='eps_mask') # same shape as input
    # adversarial_inputs_rgb = tf.nn.tanh(rgb_input + adv_flag * (mask_rgb * eps_rgb),name='adversarial_input')
    random_shift = tf.random_uniform(dtype=tf.int32, minval=0, maxval=rgb_input.shape[1].value, shape=[])
    cyclic_rgb_input = tf.roll(rgb_input,shift=random_shift,axis=1)

    cyclic_flag_default = tf.constant(0.0, dtype=tf.float32)
    cyclic_flag = tf.placeholder_with_default(cyclic_flag_default, name='cyclic_flag',
                                               shape=cyclic_flag_default.shape)

    adversarial_inputs_rgb = tf.clip_by_value(cyclic_flag*cyclic_rgb_input +(1-cyclic_flag)*rgb_input + adv_flag * (mask_rgb * extend_eps_rgb),
                                              clip_value_min = -1.0,
                                              clip_value_max = 1.0,
                                              name='adversarial_input')


rgb_model = load_i3d_model(num_classes=NUM_CLASSES)
init_model(model=rgb_model,sess=sess, ckpt_path=ckpt_path,eval_type=eval_type)
sess.run(eps_rgb.initializer)
model_logits, _ = rgb_model(adversarial_inputs_rgb, is_training=False, dropout_keep_prob=1.0)
softmax = tf.nn.softmax(logits = model_logits)


labels = tf.placeholder(tf.int64, (_BATCH_SIZE,), name='labels')

corret_cls_prob = tf.reduce_sum(tf.gather(softmax,labels,axis=-1))
# for untargeted attack set to -1.0
label_coeff_default = tf.constant(-1.0, dtype=tf.float32)
labels_coeff = tf.placeholder_with_default(label_coeff_default, name='label_coeff', shape=label_coeff_default.shape)
_is_adversarial = tf.cast(tf.reduce_all(tf.not_equal(tf.argmax(softmax,axis=-1),labels)), dtype=tf.float32)

# is_adversarial = tf.cast(tf.argmax(softmax[0, ...]) == labels, dtype=tf.float32)


inputs = rgb_input
perturbation = eps_rgb

# target label: for untargeted attack set original label


# adversarial classification loss
scores, ind = tf.math.top_k(tf.squeeze(softmax,axis=0),k=2)

max_non_correct_cls = scores[tf.cast(tf.squeeze(tf.equal(tf.cast(ind[0], dtype=tf.int64), labels)),dtype=tf.int64)]


ce_loss = 10*tf.maximum(0.0, - (max_non_correct_cls -corret_cls_prob))

# ce_loss = 10(corret_cls_prob)

# ce_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels, logits=model_logits)
# ce_loss_mean = tf.reduce_mean(labels_coeff *ce_loss)
ce_loss_mean = ce_loss


beta_0_default = tf.constant(1, dtype=tf.float32)
beta_0 = tf.placeholder_with_default(beta_0_default, name='beta_0', shape=beta_0_default.shape)

beta_1_default = tf.constant(0.1, dtype=tf.float32)
beta_1 = tf.placeholder_with_default(beta_1_default, name='beta_1', shape=beta_1_default.shape)

beta_2_default = tf.constant(0.1, dtype=tf.float32)
beta_2 = tf.placeholder_with_default(beta_2_default, name='beta_2', shape=beta_2_default.shape)

# norm_reg = tf.reduce_mean(tf.reduce_mean(tf.math.abs(perturbation), axis=-1))
#
# diff_norm_reg = tf.reduce_mean(tf.reduce_mean(tf.math.abs(perturbation - tf.roll(perturbation,1,axis=0)), axis=-1))

norm_reg = tf.reduce_mean(tf.reduce_mean(tf.math.abs(perturbation), axis=-1))

diff_norm_reg = tf.reduce_mean(tf.sqrt(tf.reduce_sum((perturbation - tf.roll(perturbation,1,axis=0))**2, axis=0)+1e-12)/_SAMPLE_VIDEO_FRAMES)
# diff_norm_reg = tf.reduce_mean((tf.norm(perturbation - tf.roll(perturbation,1,axis=0), axis=0,ord=2) + 1e-12)/_SAMPLE_VIDEO_FRAMES)

#diff_norm_reg =  tf.sqrt(tf.reduce_sum( (tf.roll(perturbation,-1,axis=0) - tf.roll(perturbation,1,axis=0))**2) + 1e-12)

# adversarial_inputs_rgb_0_255 =tf.cast(tf.cast((adversarial_inputs_rgb+1)*127.5,dtype=tf.uint8),dtype=tf.float32)
# dversarial_inputs_lab = lab_tool.rgb_to_lab(adversarial_inputs_rgb_0_255)
# L_chan, a_chan, b_chan = lab_tool.preprocess_lab(dversarial_inputs_lab)
#
# lab_reg =tf.sqrt(tf.reduce_sum(L_chan ** 2) + 1e-12)

regularizer_loss = beta_1*norm_reg + beta_2*diff_norm_reg # +lab_reg
# regularizer = tf.reduce_max(perturbation) - tf.reduce_min(perturbation)
# with tf.device('/gpu:1'):
# regularizer_loss = cx_loss(tf.expand_dims(inputs[0,_IND_START:_IND_END+1,...],axis=0),tf.expand_dims(adversarial_inputs_rgb[0,_IND_START:_IND_END+1,...],axis=0))
weighted_regularizer_loss = beta_0 * regularizer_loss

# total loss:
_use_regularizer =1.0 #  tf.cast(tf.exp(tf.reduce_mean(-ce_loss)) < 0.99, dtype=tf.float32)
# loss = (1.0 - _is_adversarial)*ce_loss_mean + _use_regularizer*weighted_regularizer_loss

loss = ce_loss_mean + _use_regularizer*weighted_regularizer_loss


# loss = corret_cls_prob*ce_loss_mean + (1-corret_cls_prob)*_use_regularizer*weighted_regularizer_loss


learning_rate_default = tf.constant(0.001, dtype=tf.float32)
learning_rate = tf.placeholder_with_default(learning_rate_default, name='learning_rate', shape=learning_rate_default.shape)
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
gradients = optimizer.compute_gradients(loss=loss, var_list=perturbation)
train_op = optimizer.apply_gradients(gradients)
sess.run(tf.variables_initializer(optimizer.variables()))

writer = tf.summary.FileWriter(logdir, sess.graph)
# with tf.name_scope('input'):
#     clean_summary = tf.summary.image('clean_image', tf.expand_dims(inputs[0, _IND_START], axis=0), max_outputs=inputs.shape[0].value)
#     pert_summary = tf.summary.image('perturbation', perturbation, max_outputs=perturbation.shape[0].value)
#     adv_summary = tf.summary.image('adversarial_image', tf.expand_dims(adversarial_inputs_rgb[0,_IND_START],axis=0), max_outputs=adversarial_inputs_rgb.shape[0].value)

# adv_vec = np.zeros(shape=[1,_SAMPLE_VIDEO_FRAMES])
# merged = tf.summary.merge_all()
#
# feed_dict = {inputs: rgb_sample, labels: [target_class], labels_coeff: -1.0}
# model_softmax = sess.run(softmax, feed_dict={inputs: rgb_sample})
#
# base_prob =model_softmax[0,target_class]
criteria = fb_2.criteria.Misclassification()
# criteria = fb_2.criteria.ConfidentMisclassification(p=0.95)
# criteria = fb_2.criteria.TargetClass(target_class=kinetics_classes.index('javelin throw'))

_labels_coeff =-1. # -1.0
_cyclic_flag = 0.0
_adv_flag =1.0

_lr=0.001

# regularization loss:
_beta_0 = 1.0 #0.1# 1 #1 #1.0 #1.0
_beta_1 =0.5# 0.5 #0.5 #0.5 #0.1 #0.1 #0.1 #0.1 #0.1 #100000 #0.01  # 100000 #0.0001 # 0.001 #0.01 #0.1 #0.0001 #1
_beta_2 =1.0 -_beta_1

npy_path = '/data/DL/Adversarial/kinetics-i3d/data/videos_for_tests/npy/'
result_path = '/data/DL/Adversarial/kinetics-i3d/result/videos_for_tests/npy/'
save_result =True
stats = []

bad_video=[]

for video in os.listdir(npy_path):


    if save_result:
        dict_result_path = os.path.join(result_path, video.split('.')[0] + '.pkl')

        if not os.path.exists(dict_result_path):
            with open(dict_result_path, 'wb') as file:
                pickle.dump("some obejct", file)
        else:
            continue

    res_dict = {}
    video_path = os.path.join(npy_path,video)
    rgb_sample =np.load(video_path)[0, -_SAMPLE_VIDEO_FRAMES:]
    rgb_sample = rgb_sample[np.newaxis]
    correct_cls = video.split('@')[-1].split('.')[0].replace('_',' ')
    assert correct_cls in kinetics_classes, "Oh no! {} not in kinetics classes".format(correct_cls)

    correct_cls_id= kinetics_classes.index(correct_cls)

    target_class = correct_cls  # 'javelin throw'
    target_class_id = kinetics_classes.index(target_class)


    feed_dict_for_train = {inputs: rgb_sample,
                           labels: [target_class_id],
                           labels_coeff: _labels_coeff,
                           cyclic_flag: _cyclic_flag,
                           learning_rate:_lr,
                           beta_0: _beta_0,
                           beta_1: _beta_1,
                           beta_2: _beta_2}

    feed_dict_for_clean_eval = {inputs: rgb_sample, adv_flag: 0}

    model_softmax = sess.run(softmax, feed_dict=feed_dict_for_clean_eval)

    top_id = model_softmax.argmax()
    top_id_prob = model_softmax.max()

    # if top_id!=correct_cls_id or top_id_prob> 0.99:
    #     print(top_id_prob)
    #     bad_video.append(video)
    #     os.remove(video_path)
    #
    # continue

    assert top_id==correct_cls_id, "Oh no! top cls is {} while correct cls is {}".format(kinetics_classes[top_id],correct_cls)

    res_dict['correct_cls_prob']=top_id_prob
    res_dict['correct_cls'] = correct_cls
    res_dict['correct_cls_id'] = correct_cls_id
    res_dict['video_name'] = video
    res_dict['softmax_init'] =model_softmax
    res_dict['rgb_sample'] = rgb_sample


    total_loss_l=[]
    adv_loss_l = []
    reg_loss_l= []
    norm_reg_loss_l=[]
    diff_norm_reg_loss_l=[]

    plt.figure(1)
    step = 0
    max_step =500

    sess.run(eps_rgb.initializer)
    sess.run(tf.variables_initializer(optimizer.variables()))

    while True:  # to repeat with decreased epsilons if necessary

        _, total_loss, adv_loss, reg_loss, norm_reg_loss, diff_norm_reg_loss = sess.run(fetches=[train_op, loss, ce_loss_mean, regularizer_loss, norm_reg,diff_norm_reg],
                                                     feed_dict=feed_dict_for_train)

        model_softmax = sess.run(softmax, feed_dict={inputs: rgb_sample})

        print("Total Loss: {:5f} , Cls Loss: {:5f} , Total Reg Loss: {:5f}, Fat Loss: {:5f}, Diff Loss: {:5f}, prob_correct_cls: {:5f}, top_prob: {:5f} ".format(total_loss, adv_loss, reg_loss,norm_reg_loss, diff_norm_reg_loss, model_softmax[0,correct_cls_id],model_softmax[0].max()))


        total_loss_l.append(total_loss)
        adv_loss_l.append(adv_loss)
        reg_loss_l.append(reg_loss)
        norm_reg_loss_l.append(norm_reg_loss)
        diff_norm_reg_loss_l.append(diff_norm_reg_loss)
        # if np.random.rand() > 0.9:
        #     plt.clf()
        #     plt.subplot(2,1,2)
        #     plt.plot(total_loss_l,'r')
        #     plt.plot(adv_loss_l,'b')
        #     plt.plot(reg_loss_l,'g')
        #     plt.plot(norm_reg_loss_l,'k')
        #     plt.plot(diff_norm_reg_loss_l,'m')
        #
        #     plt.subplot(2,1,1)
        #     plt.plot(reg_loss_l,'g')
        #     plt.plot(norm_reg_loss_l,'k')
        #     plt.plot(diff_norm_reg_loss_l,'m')
        #     plt.grid(True)
        #
        #     plt.show()
        #     plt.pause(0.1)


            # _, total_loss, adv_loss = sess.run(fetches=[train_op, loss, ce_loss_mean],
        #                                              feed_dict=feed_dict)
        # print("Total Loss: {} , Cls Loss: {}  ".format(total_loss, adv_loss))
        pert = sess.run(perturbation)

        _model_logits =  sess.run(model_logits, feed_dict={inputs: rgb_sample})
        # is_adversarial = criteria.is_adversarial(model_softmax, target_class)

        # run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
        # run_metadata = tf.RunMetadata()
        # summary = sess.run(merged, feed_dict={inputs: rgb_sample},
        #                    options=run_options,
        #                    run_metadata=run_metadata)
        # writer.add_summary(summary, step)

        is_adversarial = criteria.is_adversarial(_model_logits.squeeze(), target_class_id)

        if  step > max_step and is_adversarial :
            res_dict['total_loss_l'] = total_loss_l
            res_dict['adv_loss_l'] = adv_loss_l
            res_dict['reg_loss_l'] = reg_loss_l
            res_dict['norm_reg_loss_l'] = norm_reg_loss_l
            res_dict['diff_norm_reg_loss_l'] = diff_norm_reg_loss_l
            res_dict['perturbation'] = pert
            res_dict['adv_video'] =  sess.run(adversarial_inputs_rgb, feed_dict={inputs: rgb_sample})
            res_dict['softmax'] = model_softmax
            res_dict['total_steps'] = step
            res_dict['_beta_1'] = _beta_1
            res_dict['_beta_2'] = _beta_2


            with open(dict_result_path, 'wb') as file:
                    pickle.dump(res_dict, file)
            break

        step+=1
        # _, total_loss, adv_loss, reg_loss = sess.run(fetches=[train_op, loss, ce_loss_mean,regularizer_loss], feed_dict=feed_dict)
        # print("Total Loss: {} , Cls Loss: {} , Reg Loss: {} ".format(total_loss, adv_loss, reg_loss))
        # pert = sess.run(perturbation)


#
# run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
# run_metadata = tf.RunMetadata()
# summary = sess.run(merged, feed_dict={inputs: rgb_sample},
#                    options=run_options,
#                    run_metadata=run_metadata)
# writer.add_summary(summary,step)
# # if is_adversarial:
# #     return
#
# out_logits, out_predictions = sess.run(
#     [model_logits, model_predictions],
#     feed_dict=feed_dict)
#
# out_logits = out_logits[0]
# out_predictions = out_predictions[0]
# sorted_indices = np.argsort(out_predictions)[::-1]
#
# print('Norm of logits: %f' % np.linalg.norm(out_logits))
# print('\nTop classes and probabilities')
# for index in sorted_indices[:20]:
#   print(out_predictions[index], out_logits[index], kinetics_classes[index])
#
#
# feed_dict[adv_flag]=0.0
# out_logits, out_predictions = sess.run(
#     [model_logits, model_predictions],
#     feed_dict=feed_dict)
#
# out_logits = out_logits[0]
# out_predictions = out_predictions[0]
# sorted_indices = np.argsort(out_predictions)[::-1]
#
# print('Norm of logits: %f' % np.linalg.norm(out_logits))
# print('\nTop classes and probabilities')
# for index in sorted_indices[:20]:
#   print(out_predictions[index], out_logits[index], kinetics_classes[index])
#
# a=1



