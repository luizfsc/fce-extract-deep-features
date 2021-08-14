### https://gogul.dev/software/flower-recognition-deep-learning
### https://github.com/efidalgo/AutoBlur-CNN-Features

# filter warnings
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

# keras imports
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.applications.xception import Xception
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2
from tensorflow.keras.applications.mobilenet import MobileNet
from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input

# other imports
from sklearn.manifold import Isomap
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os
import datetime
import time
import pandas as pd
#import json
#import h5py

from utils import existing_directory

def dataReduction(df_selData, n_comp):
    #print('Feature Reduction with ISOMAP')
    isomap = Isomap(n_components=n_comp)
    df_selData = isomap.fit_transform(df_selData)
    return df_selData

datasets_available = ["Soccer"]

# datasets to be analyzed
dataset = datasets_available
test_set = [0.25, 0.25, 0.25]

for ds in range(0, len(dataset)):
    # Select the configuration file available
    #file = 'conf_' + dataset[ds] + '.json'
    
    # load the user configs. It has been created a json file per dataset
    #with open(file) as f:    
    #  config = json.load(f)
      
    # config variables
    model_name    = "vgg16"
    weights       = "imagenet"
    include_top   = 0 
    train_path    = "datasets/" + dataset[ds]
    features_path = "output/" + dataset[ds] + "/" + model_name + "/features.h5" 
    labels_path   = "output/" + dataset[ds] + "/" + model_name + "/labels.h5"
    results       = "output/" + dataset[ds] + "/" + model_name + "/results" + dataset[ds] + ".txt"
    model_path    = "output/" + dataset[ds] + "/" + model_name + "/model"
    test_size     = test_set[ds]
    
    # check if the output directory exists, if not, create it.
    existing_directory("results")
    existing_directory("results/deep_features")
    existing_directory("results/deep_features/" + dataset[ds])
    
    # start time
    print("[STATUS] start time - {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    start = time.time()
    
    # create the pretrained models
    # check for pretrained weight usage or not
    # check for top layers to be included or not
    if model_name == "vgg16":
        base_model = VGG16(weights=weights)
        model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)
        image_size = (224, 224)
    elif model_name == "vgg19":
        base_model = VGG19(weights=weights)
        model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)
        image_size = (224, 224)
    elif model_name == "resnet50":
        base_model = ResNet50(weights=weights)
        model = Model(inputs=base_model.input, outputs=base_model.get_layer('flatten').output)
        image_size = (224, 224)
    elif model_name == "inceptionv3":
        base_model = InceptionV3(include_top=include_top, weights=weights, input_tensor=Input(shape=(299, 299, 3)))
        model = Model(inputs=base_model.input, outputs=base_model.get_layer('flatten').output)
        image_size = (299, 299)
    elif model_name == "inceptionresnetv2":
        base_model = InceptionResNetV2(include_top=include_top, weights=weights, input_tensor=Input(shape=(299, 299, 3)))
        model = Model(inputs=base_model.input, outputs=base_model.get_layer('conv_7b').output)
        image_size = (299, 299)
    elif model_name == "mobilenet":
        base_model = MobileNet(include_top=include_top, weights=weights, input_tensor=Input(shape=(224, 224, 3)), input_shape=(224, 224, 3))
        model = Model(inputs=base_model.input, outputs=base_model.get_layer('conv1_relu').output)
        image_size = (224, 224)
    elif model_name == "xception":
        base_model = Xception(weights=weights)
        model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)
        image_size = (299, 299)
    else:
        base_model = None
    
    # check if the output directory exists, if not, create it.
    existing_directory("results/deep_features/" + dataset[ds] + "/" + model_name)
    
    print("[INFO] successfully loaded base model and model...")
    
    # path to training dataset
    train_labels = os.listdir(train_path)
    
    # encode the labels
    print("[INFO] encoding labels...")
    ### AQUI TEM QUE ALTERAR QDO. USAR NOSSA BASE DE DADOS, PARECE QUE PEGA OS LABELS PELOS NOMES DOS ARQUIVOS
    le = LabelEncoder()
    le.fit([tl for tl in train_labels])
    
    # variables to hold features and labels
    features = []
    labels   = []

    # loop over all the labels in the folder
    count = 1
    for i, label in enumerate(train_labels):   
        cur_path = train_path + "/" + label
        # check how many files are, together with their extensions
        list_files = os.listdir(cur_path)
        count = 1
        # for image_path in glob.glob(cur_path + "/*.jpg"):
        for image_path in range(0, len(list_files)):
            # print ("[INFO] Processing - " + str(count) + " named " + list_files[image_path])
            img = image.load_img(cur_path + "/" + list_files[image_path], target_size=image_size) ### carrega a imagem
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            feature = model.predict(x)
            flat = feature.flatten()
            features.append(flat)
            labels.append(label)  ### DE ONDE VEM ESSA LABEL?
            print ("[INFO] processed for image - " + list_files[image_path])
            count += 1
    print ("[INFO] completed label - " + label)
    
    # encode the labels using LabelEncoder
    le = LabelEncoder()
    le_labels = le.fit_transform(labels)
    
    # get the shape of training labels
    print("[STATUS] training labels: {}".format(le_labels))
    print("[STATUS] training labels shape: {}".format(le_labels.shape))
    
    # save features and labels
    '''try:
        h5f_data = h5py.File(features_path, 'w')
    except:
        a=1;'''

    features = pd.DataFrame(features)
    features = dataReduction(features, 8)

    ### Aqui tinha que salver em CSV mesmo...

    '''h5f_data.create_dataset('dataset_1', data=np.array(features))
    h5f_label = h5py.File(labels_path, 'w')
    h5f_label.create_dataset('dataset_1', data=np.array(le_labels))
    h5f_data.close()
    h5f_label.close()'''
    
    # save model and weights
    ''' model_json = model.to_json()
    with open(model_path + str(test_size) + ".json", "w") as json_file:
      json_file.write(model_json)
    
    # save weights
    model.save_weights(model_path + str(test_size) + ".h5")
    print("[STATUS] saved model and weights to disk..")
    
    print ("[STATUS] features and labels saved..")'''
    
    # end time
    end = time.time()
    print("[STATUS] end time - {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
