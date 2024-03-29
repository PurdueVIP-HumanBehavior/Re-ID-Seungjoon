import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image
import os

image_list = list()
ct = 0

#for pic in os.listdir("./images/"):
#    os.rename("./images/" + pic, "./images/seq_%04d" %ct + ".jpg")
#    ct += 1

for pic in os.listdir("./images/"):
    image_list.append(pic)

# Load the pretrained model
model = models.resnet18(pretrained=True)
model.cuda()

# Use the model object to select the desired layer
layer = model._modules.get('avgpool')

# Set model to evaluation mode
model.eval()

scaler = transforms.Resize((224, 224))
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
to_tensor = transforms.ToTensor()

def get_vector(image_name):
    # 1. Load the image with Pillow library
    img = Image.open(image_name)

    # 2. Create a PyTorch Variable with the transformed image
    t_img = Variable(normalize(to_tensor(scaler(img))).unsqueeze(0))
    t_img = t_img.cuda()
    # 3. Create a vector of zeros that will hold our feature vector
    #    The 'avgpool' layer has an output size of 512
    my_embedding = torch.zeros(1, 512, 1, 1)
    # 4. Define a function that will copy the output of a layer
    def copy_data(m, i, o):
        my_embedding.copy_(o.data)
    # 5. Attach that function to our selected layer
    h = layer.register_forward_hook(copy_data)
    # 6. Run the model on our transformed image
    model(t_img)
    # 7. Detach our copy function from the layer
    h.remove()
    # 8. Return the feature vector
    return my_embedding

cos = nn.CosineSimilarity(dim=1, eps=1e-6)

for ct, img in enumerate(image_list):
    if ct < len(image_list) - 1:

        pic_one_vector = get_vector("./images/" + img)
        pic_two_vector = get_vector("./images/" + image_list[ct + 1])

        cos_sim = cos(pic_one_vector, pic_two_vector)
        print(cos_sim.item())
        print("----------------------")
        if cos_sim.item() < 0.9:
            print("wrong person")
        #print('\nCosine similarity: {0}\n'.format(cos_sim))




