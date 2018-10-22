# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 18:09:14 2018

@author: wmy
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import random
import time

class DCGAN(object):
    
    def __init__(self, image_width=64, image_height=64, batch_size=64, z_dim=128):
        '''
        function: parameters initialize
        input image_width: the width of output images
        input image_height: the height of output images
        input batch_size: the number of output images
        input z_dim: the size of vector z
        return: none
        '''
        self.image_width = image_width
        self.image_height = image_height
        self.batch_size = batch_size
        self.z_dim = z_dim
        pass
    
    def load_dataset(self, floder, max_size=1000, show_sample=False):
        '''
        function: load the dataset
        input floder: the path and your floder name
        input max_size: the max number of your train images
        input show_sample: if show a sample of images
        return: trainset
        '''
        # names of your train images
        images = os.listdir(floder)
        # the number of train images
        num_images = min(len(images), max_size)
        # choose a sample
        sample = plt.imread(floder + '/' + random.choice(images[0:max_size-1]))
        if show_sample:
            print('One of sample:')
            plt.imshow(sample)
            plt.show()
            pass
        resize_width = self.image_width
        resize_height = self.image_height
        dataset = np.empty((num_images, resize_height, resize_width, 3), dtype="float32")
        # convert to numpy array
        for i in range(num_images):
            img = Image.open(floder + "/" + images[i])   
            img = img.resize((resize_height, resize_width))             
            img_arr = np.asarray(img, dtype="float32")                  
            dataset[i, :, :, :] = img_arr     
            pass
        print('dataset size: ' + str(dataset.shape))
        # convert to tensor
        with tf.Session() as sess:        
            sess.run(tf.initialize_all_variables())
            dataset = tf.reshape(dataset, [-1, resize_height, resize_width, 3])
            traindata = dataset * 1.0 / 127.5 - 1.0 
            traindata = tf.reshape(traindata, [-1, resize_height*resize_width*3])
            trainset = sess.run(traindata)
        print('[OK] ' + str(num_images) + ' samples have been loaded')
        return trainset
    
    def generator(self, z, reuse, trainable=True):
        '''
        function: creat a generator
        input z: tensor z
        input trainable: if train
        input reuse: if reuse
        return: images generated by generator
        '''
        m = int(self.image_height/16)
        n = int(self.image_width/16)
        # layer 1: fc layer 4 by 4
        with tf.variable_scope("G_L1_FC", reuse=reuse):
            output = tf.layers.dense(z, 1024*m*n, trainable=trainable)
            output = tf.reshape(output, [self.batch_size, m, n, 1024])
            output = tf.layers.batch_normalization(output, training=trainable)
            output = tf.nn.relu(output)
        # layer 2: deconv2d layer 8 by 8
        with tf.variable_scope("G_L2_DC", reuse=reuse):
            output = tf.layers.conv2d_transpose(output, 512, [5, 5], strides=(2, 2), padding="SAME", trainable=trainable)
            output = tf.layers.batch_normalization(output, training=trainable)
            output = tf.nn.relu(output)
        # layer 3: deconv2d layer 16 by 16
        with tf.variable_scope("G_L3_DC", reuse=reuse):
            output = tf.layers.conv2d_transpose(output, 256, [5, 5], strides=(2, 2), padding="SAME", trainable=trainable)
            output = tf.layers.batch_normalization(output, training=trainable)
            output = tf.nn.relu(output)
        # layer 4: deconv2d layer 32 by 32
        with tf.variable_scope("G_L4_DC", reuse=reuse):
            output = tf.layers.conv2d_transpose(output, 128, [5, 5], strides=(2, 2), padding="SAME", trainable=trainable)
            output = tf.layers.batch_normalization(output, training=trainable)
            output = tf.nn.relu(output)
        # layer 5: deconv2d layer 64 by 64
        with tf.variable_scope("G_L5_DC", reuse=reuse):
            output = tf.layers.conv2d_transpose(output, 3, [5, 5], strides=(2, 2), padding="SAME", trainable=trainable)
            generator_images = tf.nn.tanh(output)
        return generator_images
    
    def discriminator(self, x, reuse, trainable=True):
        '''
        function: creat a discriminator
        input x: tensor x
        input trainable: if train
        input reuse: if reuse
        return: images discriminated by discriminator
        '''
        # layer 1: conv2d layer
        with tf.variable_scope("D_L1_CV", reuse=reuse):
            output = tf.layers.conv2d(x, 64, [5, 5], strides=(2, 2), padding="SAME", trainable=trainable)
            output = tf.layers.batch_normalization(output, training=trainable)
            output = tf.nn.leaky_relu(output)
        # layer 2: conv2d layer
        with tf.variable_scope("D_L2_CV", reuse=reuse):
            output = tf.layers.conv2d(output, 128, [5, 5], strides=(2, 2), padding="SAME", trainable=trainable)
            output = tf.layers.batch_normalization(output, training=trainable)
            output = tf.nn.leaky_relu(output)
        # layer 3: conv2d layer
        with tf.variable_scope("D_L3_CV", reuse=reuse):
            output = tf.layers.conv2d(output, 256, [5, 5], strides=(2, 2), padding="SAME", trainable=trainable)
            output = tf.layers.batch_normalization(output, training=trainable)
            output = tf.nn.leaky_relu(output)
        # layer 4: conv2d layer
        with tf.variable_scope("D_L4_CV", reuse=reuse):
            output = tf.layers.conv2d(output, 512, [5, 5], strides=(2, 2), padding="SAME", trainable=trainable)
            output = tf.layers.batch_normalization(output, training=trainable)
            output = tf.nn.leaky_relu(output)
        # layer 5: fc layer
        with tf.variable_scope("D_L5_FC", reuse=reuse):
            output = tf.layers.flatten(output)
            discriminator_images = tf.layers.dense(output, 1, trainable=trainable)
        return discriminator_images
    
    def make_dir(self, path):
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
            print("You created a new path!")
            print("Path: " + str(path))
            pass
        else:
            print("Path: " + str(path) + " is already existed.")
        pass
    
    def plot_and_save(self, order, images, floder_name='output'):
        '''
        function: save the output picture
        input order: number
        input images: images
        input floder_name: floder name
        return: none
        '''
        self.make_dir(floder_name + '/')
        batch_size = len(images)
        # 64 = 8 * 8
        n = np.int(np.sqrt(batch_size))
        # shape of images
        image_height = np.shape(images)[1]
        image_width = np.shape(images)[2]
        n_channel = np.shape(images)[3]
        images = np.reshape(images, [-1, image_height, image_width, n_channel])
        # output
        canvas = np.empty((n * image_height, n * image_width, n_channel))
        for i in range(n):
            for j in range(n):
                canvas[i*image_height:(i+1)*image_height, j*image_width:(j+1)*image_width, :] = \
                images[n*i+j].reshape(image_height, image_width, 3)
                pass
            pass
        plt.figure(figsize=(n, n))
        plt.imshow(canvas, cmap="gray")
        label = "Epoch: {0}".format(order+1)
        plt.xlabel(label)
        if type(order) is str:
            file_name = order
        else:
            file_name = "DCGAN_GEN_" + str(order+1)
            pass
        plt.savefig(floder_name + '/' + file_name)
        print(os.getcwd())
        print("Image saved in file: ", floder_name + '/' + file_name)
        plt.show()
        pass
    
    def train(self, learning_rate=0.0001, beta1=0.5, epoch=500):
        '''
        function: train
        input learning_rate: learning rate
        input beta1: beta1
        input epoch: epoch
        return none
        '''
        # load the trainset
        trainset = self.load_dataset('./faces', show_sample=True)
        # placeholders
        x = tf.placeholder(tf.float32, shape=[None, self.image_height*self.image_width*3], name="input_real")
        x_img = tf.reshape(x, [-1] + [self.image_height, self.image_width, 3])
        z = tf.placeholder(tf.float32, shape=[None, self.z_dim], name="z")
        # generate images
        G = self.generator(z, reuse=False)
        # discriminator judges
        D_fake_logits = self.discriminator(G, reuse=False)
        D_true_logits = self.discriminator(x_img, reuse=True)
        # loss function
        G_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_fake_logits, labels=tf.ones_like(D_fake_logits)))
        D_loss_1 = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_true_logits, labels=tf.ones_like(D_true_logits)))
        D_loss_2 = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_fake_logits, labels=tf.zeros_like(D_fake_logits)))
        D_loss = D_loss_1 + D_loss_2
        # all vars
        total_vars = tf.trainable_variables()
        d_vars = [var for var in total_vars if "D_" in var.name]
        g_vars = [var for var in total_vars if "G_" in var.name]
        # adam optimizer
        with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
            g_optimization = tf.train.AdamOptimizer(learning_rate=learning_rate, beta1=beta1).minimize(G_loss, var_list=g_vars)
            d_optimization = tf.train.AdamOptimizer(learning_rate=learning_rate, beta1=beta1).minimize(D_loss, var_list=d_vars)
        print("we successfully make the network")
        start_time = time.time()      
        sess = tf.Session()
        sess.run(tf.initialize_all_variables()) 
        for i in range(epoch):
            total_batch = int(len(trainset)/self.batch_size)
            d_value = 0
            g_value = 0
            # train in batchs
            for j in range(total_batch):
                batch_xs = trainset[j*self.batch_size:j*self.batch_size + self.batch_size]
                # train dnn
                z_sampled1 = np.random.uniform(low=-1.0, high=1.0, size=[self.batch_size, self.z_dim])
                Op_d, d_ = sess.run([d_optimization, D_loss], feed_dict={x: batch_xs, z: z_sampled1})
                # train gnn
                z_sampled2 = np.random.uniform(low=-1.0, high=1.0, size=[self.batch_size, self.z_dim])
                Op_g, g_ = sess.run([g_optimization, G_loss], feed_dict={x: batch_xs, z: z_sampled2})
                # save
                images_generated = sess.run(G, feed_dict={z: z_sampled2})
                d_value += d_/total_batch
                g_value += g_/total_batch
                self.plot_and_save(i, images_generated)
                # loss
                hour = int((time.time() - start_time)/3600)
                minute = int(((time.time() - start_time) - 3600*hour)/60)
                sec = int((time.time() - start_time) - 3600*hour - 60*minute)
                print("Time: ", hour, "h", minute, "m", sec, "s\n", "Epoch: ", i, "\nG_loss: ", g_value, "\nD_loss: ", d_value)
                pass
            pass
        pass
    
    pass
    
tf.reset_default_graph()  
dcgan = DCGAN()
dcgan.train()
    